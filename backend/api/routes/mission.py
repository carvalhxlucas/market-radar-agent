"""Mission API routes."""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any
import asyncio
import json
import queue
from services.mission_service import MissionService
from repositories.mission_repository import MissionRepository
from infrastructure.browser_engine import BrowserEngine
from infrastructure.memory import Memory
from services.agent import MarketRadarAgent
from core.exceptions import MissionNotFoundError, MissionAlreadyRunningError
from config.settings import Settings

router = APIRouter()

# Dependency injection - in production, use a DI container
mission_repository = MissionRepository()
mission_service = MissionService(mission_repository)
settings = Settings()


class MissionRequest(BaseModel):
    """Request model for creating a mission."""
    goal: str = Field(..., description="Mission goal", min_length=1)
    headless: bool = Field(default=True, description="Run browser in headless mode")
    max_iterations: int = Field(
        default=100,
        ge=1,
        le=500,
        description="Maximum number of iterations"
    )


def run_mission(mission_id: str, goal: str, headless: bool, max_iterations: int, message_queue: queue.Queue):
    """
    Run mission in a separate thread.
    
    Args:
        mission_id: Mission identifier
        goal: Mission goal
        headless: Whether to run browser in headless mode
        max_iterations: Maximum number of iterations
        message_queue: Queue for sending messages
    """
    try:
        browser = BrowserEngine(headless=headless)
        memory = Memory()
        agent = MarketRadarAgent(browser, memory, goal)
        
        browser.start()
        browser.goto("https://www.google.com")
        
        message_queue.put({
            "type": "status",
            "message": "Mission started",
            "url": browser.current_url
        })
        
        iteration = 0
        
        while not agent.goal_achieved and iteration < max_iterations:
            iteration += 1
            
            page_state = browser.get_page_state()
            action_command = agent.decide_action(page_state)
            result = agent.execute_action(action_command)
            
            response_data = {
                "type": "action",
                "iteration": iteration,
                "thought_process": action_command["thought_process"],
                "reasoning": action_command["reasoning"],
                "action": action_command["action"],
                "result": result,
                "is_goal_achieved": action_command["is_goal_achieved"],
                "url": browser.current_url,
                "extracted_data_count": len(memory.get_extracted_data()),
                "sources_visited": len(agent.sources_visited)
            }
            
            message_queue.put(response_data)
            
            # Update mission status
            mission_service.repository.update(
                mission_id,
                sources_visited=len(agent.sources_visited),
                data_points=len(memory.get_extracted_data())
            )
            
            if action_command.get("is_goal_achieved") or action_command["action"]["name"] == "finish":
                mission_service.repository.update(mission_id, is_complete=True)
                final_data = {
                    "type": "complete",
                    "summary": memory.get_summary(),
                    "extracted_data": memory.get_extracted_data(),
                    "total_iterations": iteration
                }
                message_queue.put(final_data)
                break
            
            if not result.get("success", False):
                message_queue.put({
                    "type": "error",
                    "message": f"Action failed: {result.get('error', 'Unknown error')}"
                })
        
        if not agent.goal_achieved:
            mission_service.repository.update(mission_id, is_complete=True)
            message_queue.put({
                "type": "incomplete",
                "message": "Max iterations reached",
                "summary": memory.get_summary(),
                "extracted_data": memory.get_extracted_data()
            })
        
        browser.stop()
        mission_service.repository.update(mission_id, is_running=False)
        message_queue.put({"type": "finished"})
        
    except Exception as e:
        mission_service.repository.update(mission_id, is_running=False, error=str(e))
        message_queue.put({
            "type": "error",
            "message": f"Mission failed: {str(e)}"
        })


@router.post("/mission/start")
async def start_mission(request: MissionRequest) -> Dict[str, Any]:
    """
    Start a new mission.
    
    Args:
        request: Mission request data
        
    Returns:
        Mission ID and WebSocket URL
    """
    try:
        result = mission_service.create_mission(
            goal=request.goal,
            headless=request.headless,
            max_iterations=request.max_iterations
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/mission/{mission_id}/status")
async def get_mission_status(mission_id: str) -> Dict[str, Any]:
    """
    Get mission status.
    
    Args:
        mission_id: Mission identifier
        
    Returns:
        Mission status
    """
    try:
        status = mission_service.get_mission_status(mission_id)
        return status.model_dump()
    except MissionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/mission/{mission_id}")
async def stop_mission(mission_id: str) -> Dict[str, str]:
    """
    Stop a running mission.
    
    Args:
        mission_id: Mission identifier
        
    Returns:
        Success message
    """
    try:
        mission_service.stop_mission(mission_id)
        mission_service.delete_mission(mission_id)
        return {"message": "Mission stopped"}
    except MissionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.websocket("/ws/{mission_id}")
async def websocket_endpoint(websocket: WebSocket, mission_id: str):
    """
    WebSocket endpoint for mission updates.
    
    Args:
        websocket: WebSocket connection
        mission_id: Mission identifier
    """
    await websocket.accept()
    
    try:
        mission = mission_service.repository.get(mission_id)
    except MissionNotFoundError:
        await websocket.send_json({
            "type": "error",
            "message": "Mission not found"
        })
        await websocket.close()
        return
    
    if mission["is_running"]:
        await websocket.send_json({
            "type": "error",
            "message": "Mission already running"
        })
        await websocket.close()
        return
    
    try:
        message_queue = mission_service.get_message_queue(mission_id)
        
        mission_service.start_mission_thread(
            mission_id,
            run_mission,
            mission_id,
            mission["goal"],
            mission["headless"],
            mission["max_iterations"],
            message_queue
        )
        
        while True:
            try:
                try:
                    message = message_queue.get(timeout=0.5)
                    await websocket.send_json(message)
                    if message.get("type") in ["complete", "incomplete", "finished", "error"]:
                        break
                except queue.Empty:
                    if not mission_service.repository.get(mission_id)["is_running"]:
                        break
                    pass
                
                try:
                    data = await asyncio.wait_for(websocket.receive_text(), timeout=0.1)
                    message = json.loads(data)
                    if message.get("type") == "stop":
                        mission_service.stop_mission(mission_id)
                        break
                except asyncio.TimeoutError:
                    continue
                except WebSocketDisconnect:
                    break
                    
            except WebSocketDisconnect:
                break
        
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "message": f"WebSocket error: {str(e)}"
        })
    finally:
        mission_service.repository.update(mission_id, is_running=False)
        await websocket.close()


mission_router = router
