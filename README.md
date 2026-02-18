# MarketRadar - Autonomous Web Navigation Agent

MarketRadar is an autonomous agent specialized in Open Source Intelligence (OSINT) and market research. It navigates the web autonomously to fulfill specific objectives, overcoming UI obstacles, pop-ups, and pagination.

## Features

- Autonomous web navigation using Playwright
- Loop detection and prevention
- Automatic data extraction (prices, products, etc.)
- Memory system for action tracking
- Structured JSON responses
- Human-like navigation (uses search bars and menus)

## Quick Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd market-radar-agent
```

2. Install backend dependencies:
```bash
cd backend
pip install -r requirements.txt
playwright install chromium
cd ..
```

3. Install frontend dependencies:
```bash
cd frontend
npm install
cd ..
```

> 📖 **For detailed execution instructions, see [EXECUTION_INSTRUCTIONS.md](./EXECUTION_INSTRUCTIONS.md)**

## Usage

### CLI Mode (Command Line)

Execute the agent with a specific objective:

```bash
cd backend
python main.py "Find the average price of Creatine in Brazil"
```

### Web Mode (Frontend)

#### Initial Installation

1. **Install backend dependencies:**
```bash
cd backend
pip install -r requirements.txt
playwright install chromium
cd ..
```

2. **Install frontend dependencies:**
```bash
cd frontend
npm install
cd ..
```

#### Execution

**Terminal 1 - Start the backend API:**
```bash
cd backend
python api.py
```

Or using uvicorn:
```bash
cd backend
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Start the frontend:**
```bash
cd frontend
npm start
```

3. **Access `http://localhost:3000` in your browser**

#### Web Interface Features

- **💬 Interactive Chat**: Type commands directly in the chat for the agent
- **📚 Source List**: Automatically view all consulted URLs
- **📊 Price Charts**: See price history in real-time
- **📄 PDF Export**: Generate complete reports in PDF
- **📡 Real-time Logs**: Track progress via WebSocket
- **⚙️ Settings**: Adjust options like headless mode and max iterations

#### Usage Example

1. Open `http://localhost:3000`
2. In the chat, type: "Find the average price of Creatine in Brazil"
3. Press Enter or click "Send"
4. Watch the agent navigate and collect data
5. See charts being updated in real-time
6. Export the complete report in PDF when finished

## Project Structure

### Backend
- `backend/`: Python backend code
  - `main.py`: Main CLI execution file
  - `api.py`: FastAPI with WebSocket for frontend
  - `agent.py`: MarketRadar agent logic with decision making
  - `browser_engine.py`: Web navigation engine using Playwright
  - `memory.py`: Memory and action history system
  - `extractor.py`: Web data extraction system
  - `requirements.txt`: Python dependencies

### Frontend
- `frontend/`: React application with TypeScript
  - `src/App.tsx`: Main component
  - `src/components/MissionControl.tsx`: Mission control
  - `src/components/MissionLog.tsx`: Real-time log
  - `src/components/DataViewer.tsx`: Extracted data viewer
  - `tsconfig.json`: TypeScript configuration

## Response Format

The agent returns commands in JSON format:

```json
{
  "thought_process": "Current state analysis",
  "reasoning": "Explanation of chosen action",
  "action": {
    "name": "type|click|goto|scroll|wait|extract|finish",
    "params": {
      "selector": "...",
      "text": "..."
    }
  },
  "is_goal_achieved": false
}
```

## Available Actions

- `goto(url)`: Navigate to a URL
- `click(selector)`: Click on an element
- `type(selector, text)`: Type into a field
- `scroll(direction)`: Scroll the page (down/up)
- `wait(seconds)`: Wait for a period
- `extract(data_points)`: Extract data from the page
- `finish(summary)`: Finish the mission

## Environment Variables

Create a `.env` file (optional):

```
BROWSER_HEADLESS=true
MAX_ITERATIONS=50
```

## Requirements

- Python 3.8+
- Playwright
- Chromium browser (installed via Playwright)
- Node.js 16+
- npm or yarn
