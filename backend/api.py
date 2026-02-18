from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
import asyncio
import threading
import json
import queue
from browser_engine import BrowserEngine
from memory import Memory
from agent import MarketRadarAgent
import os


app = FastAPI(title="MarketRadar API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class MissionRequest(BaseModel):
    goal: str
    headless: bool = True
    max_iterations: int = 50


class ActiveMission:
    def __init__(self, mission_id: str, goal: str, headless: bool, max_iterations: int):
        self.mission_id = mission_id
        self.goal = goal
        self.headless = headless
        self.max_iterations = max_iterations
        self.browser = None
        self.agent = None
        self.memory = None
        self.is_running = False
        self.is_complete = False
        self.error = None
        self.message_queue = queue.Queue()


active_missions: Dict[str, ActiveMission] = {}


def run_mission(mission: ActiveMission, message_queue: queue.Queue):
    try:
        mission.is_running = True
        browser = BrowserEngine(headless=mission.headless)
        memory = Memory()
        agent = MarketRadarAgent(browser, memory, mission.goal)
        
        mission.browser = browser
        mission.agent = agent
        mission.memory = memory
        
        browser.start()
        browser.goto("https://www.google.com")
        
        message_queue.put({
            "type": "status",
            "message": "Mission started",
            "url": browser.current_url
        })
        
        iteration = 0
        
        while not agent.goal_achieved and iteration < mission.max_iterations and mission.is_running:
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
                "extracted_data_count": len(memory.get_extracted_data())
            }
            
            message_queue.put(response_data)
            
            if action_command.get("is_goal_achieved") or action_command["action"]["name"] == "finish":
                mission.is_complete = True
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
        
        if not agent.goal_achieved and mission.is_running:
            message_queue.put({
                "type": "incomplete",
                "message": "Max iterations reached",
                "summary": memory.get_summary(),
                "extracted_data": memory.get_extracted_data()
            })
        
        browser.stop()
        mission.is_running = False
        message_queue.put({"type": "finished"})
        
    except Exception as e:
        mission.error = str(e)
        mission.is_running = False
        message_queue.put({
            "type": "error",
            "message": f"Mission failed: {str(e)}"
        })


@app.get("/")
async def root():
    return {"message": "MarketRadar API", "status": "running"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.websocket("/ws/{mission_id}")
async def websocket_endpoint(websocket: WebSocket, mission_id: str):
    await websocket.accept()
    
    if mission_id not in active_missions:
        await websocket.send_json({
            "type": "error",
            "message": "Mission not found"
        })
        await websocket.close()
        return
    
    mission = active_missions[mission_id]
    
    if mission.is_running:
        await websocket.send_json({
            "type": "error",
            "message": "Mission already running"
        })
        await websocket.close()
        return
    
    try:
        thread = threading.Thread(
            target=run_mission,
            args=(mission, mission.message_queue),
            daemon=True
        )
        thread.start()
        
        while True:
            try:
                try:
                    message = mission.message_queue.get(timeout=0.5)
                    await websocket.send_json(message)
                    if message.get("type") in ["complete", "incomplete", "finished", "error"]:
                        break
                except queue.Empty:
                    if not mission.is_running and mission.is_complete:
                        break
                    pass
                
                try:
                    data = await asyncio.wait_for(websocket.receive_text(), timeout=0.1)
                    message = json.loads(data)
                    if message.get("type") == "stop":
                        mission.is_running = False
                        if mission.browser:
                            mission.browser.stop()
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
        mission.is_running = False
        await websocket.close()


@app.post("/mission/start")
async def start_mission(request: MissionRequest):
    mission_id = str(uuid.uuid4())
    
    mission = ActiveMission(
        mission_id=mission_id,
        goal=request.goal,
        headless=request.headless,
        max_iterations=request.max_iterations
    )
    
    active_missions[mission_id] = mission
    
    return {
        "mission_id": mission_id,
        "websocket_url": f"ws://localhost:8000/ws/{mission_id}"
    }


@app.get("/mission/{mission_id}/status")
async def get_mission_status(mission_id: str):
    if mission_id not in active_missions:
        return {"error": "Mission not found"}
    
    mission = active_missions[mission_id]
    
    return {
        "mission_id": mission_id,
        "goal": mission.goal,
        "is_running": mission.is_running,
        "is_complete": mission.is_complete,
        "error": mission.error
    }


@app.delete("/mission/{mission_id}")
async def stop_mission(mission_id: str):
    if mission_id not in active_missions:
        return {"error": "Mission not found"}
    
    mission = active_missions[mission_id]
    mission.is_running = False
    
    if mission.browser:
        mission.browser.stop()
    
    del active_missions[mission_id]
    
    return {"message": "Mission stopped"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
