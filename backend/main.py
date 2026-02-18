import sys
import os
from browser_engine import BrowserEngine
from memory import Memory
from agent import MarketRadarAgent


def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py '<global_goal>'")
        print("Example: python main.py 'Find the average price of Creatine in Brazil'")
        sys.exit(1)
    
    global_goal = sys.argv[1]
    
    headless = os.getenv("BROWSER_HEADLESS", "true").lower() == "true"
    
    browser = BrowserEngine(headless=headless)
    memory = Memory()
    agent = MarketRadarAgent(browser, memory, global_goal)
    
    try:
        browser.start()
        browser.goto("https://www.google.com")
        
        print(f"Goal: {global_goal}\n")
        print("Starting MarketRadar agent...\n")
        
        iteration = 0
        max_iterations = int(os.getenv("MAX_ITERATIONS", "50"))
        
        while not agent.goal_achieved and iteration < max_iterations:
            iteration += 1
            print(f"\n--- Iteration {iteration} ---")
            
            response_json = agent.step()
            print(response_json)
            
            import json
            response = json.loads(response_json)
            
            if response.get("is_goal_achieved") or response["action"]["name"] == "finish":
                print("\n" + "="*50)
                print("MISSION COMPLETE")
                print("="*50)
                print(f"\nSummary:\n{memory.get_summary()}")
                print(f"\nExtracted Data:")
                for data in memory.get_extracted_data():
                    print(f"  - {data}")
                break
        
        if not agent.goal_achieved:
            print("\n" + "="*50)
            print("MISSION INCOMPLETE - Max iterations reached")
            print("="*50)
            print(f"\nSummary:\n{memory.get_summary()}")
    
    except KeyboardInterrupt:
        print("\n\nMission interrupted by user.")
    except Exception as e:
        print(f"\n\nError: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        browser.stop()


if __name__ == "__main__":
    main()
