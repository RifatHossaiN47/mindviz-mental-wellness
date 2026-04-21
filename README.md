# MindViz

MindViz is a desktop mental wellness application that turns emotional patterns into an interactive visual journey.
It supports both:

- Text-based emotional analysis
- Game-based behavioral analysis (no writing required)

The system then recommends personalized techniques, visualizes your state as a 3D garden, and tracks your progress over time.

## Why MindViz

- Practical daily check-in for stress, anxiety, and mood
- Fast feedback loop: analyze -> practice -> re-check
- Visual-first experience instead of plain text-only reporting
- Local-first storage for user and session history.

## Core Features

- AI-powered emotional metric extraction (anxiety, mood, stress)
- Gameplay-based mental state detection (reaction + behavior signals)
- 3D mental garden that adapts to emotional metrics
- Personalized recommendations from a 20-technique wellness library
- Guided exercise sessions with animated, technique-specific widgets
- Journey mode with 3D historical progress map and trend indicators
- Gemini API support with demo fallback when API key is unavailable

## Project Architecture

- Frontend: PyQt5 + PyOpenGL
- Backend: FastAPI + Uvicorn
- Analysis: Gemini API (or fallback analyzer)
- Storage: local JSON files under data/

### Runtime Flow

1. User chooses text mode or game mode
2. Frontend sends payload to backend
3. Backend computes emotional metrics
4. Backend produces recommendations + visualization parameters
5. Frontend shows result dashboard (metrics + garden + suggestions)
6. User runs a guided session and saves progress
7. Journey screen visualizes historical change

## Repository Structure

```text
MindViz/
├── backend/
│   ├── server.py
│   ├── requirements.txt
│   └── modules/
│       ├── gemini_analyzer.py
│       ├── game_analyzer.py
│       ├── rag_system.py
│       └── visualizer.py
├── frontend/
│   ├── main.py
│   ├── requirements.txt
│   ├── screens/
│   │   ├── welcome_screen.py
│   │   ├── auth_screen.py
│   │   ├── input_screen.py
│   │   ├── game_mode_screen.py
│   │   ├── game_screen.py
│   │   ├── loading_screen.py
│   │   ├── result_screen.py
│   │   ├── session_screen.py
│   │   └── journey_screen.py
│   ├── opengl/
│   │   ├── garden_renderer.py
│   │   ├── journey_renderer.py
│   │   └── exercise_widgets.py
│   └── utils/
│       ├── http_client.py
│       └── api_client.py
├── data/
│   ├── techniques/
│   ├── users.json
│   └── sessions/
├── run_mindviz.bat
├── run_mindviz.ps1
└── test_api.py
```

## Prerequisites

- Python 3.10+ (recommended)
- Windows for one-click launcher scripts
- OpenGL-capable graphics driver for best visual experience

## Quick Start

### Option 1: One-click launch (Windows)

Batch:

```text
Double-click run_mindviz.bat
```

PowerShell:

```powershell
.\run_mindviz.ps1
```

This starts backend and frontend in separate terminals.

### Option 2: Manual setup

1. Install backend dependencies

```bash
cd backend
pip install -r requirements.txt
```

2. Install frontend dependencies

```bash
cd frontend
pip install -r requirements.txt
```

3. Configure environment

- Copy backend/.env.example to backend/.env
- Add your Gemini API key:

```env
GEMINI_API_KEY=your_key_here
```

Get a key from: https://aistudio.google.com/app/apikey

4. Start backend

```bash
cd backend
python server.py
```

5. Start frontend

```bash
cd frontend
python main.py
```

## How to Use

### Text Mode

Welcome -> Sign in or Guest -> Describe feelings -> Analyze -> Result -> Start recommended session

### Game Mode

Welcome -> Play a Game Instead -> Select duration -> Play bubble game -> Analyze gameplay -> Result

## API Endpoints

- GET /
  - Health check
- POST /analyze
  - Text-based emotional analysis
- POST /analyze-game
  - Game-behavior emotional analysis
- POST /save-session
  - Save session outcomes
- GET /get-sessions/{username}
  - Retrieve journey history

## Local Data and Privacy

- User/session data is stored locally in JSON files
- Technique content is local text corpus
- Gemini calls are only for analysis; fallback mode works without key

## Testing and Validation

Backend smoke test:

```bash
python test_api.py
```

This checks server availability and analyzes a sample payload.

## Troubleshooting

### Backend not connecting

- Make sure backend is running first
- Check: http://localhost:8000
- Check API docs: http://localhost:8000/docs

### Gemini key issues

- Verify backend/.env exists
- Verify GEMINI_API_KEY is valid
- App falls back to demo analysis mode if key is missing

### OpenGL rendering issues

- Update graphics drivers
- Run on a machine with OpenGL support
- The app still functions with reduced visual quality fallback where possible

## GitHub Publish Checklist

Before pushing:

1. Ensure backend/.env is not committed
2. Remove personal local data from data/users.json and data/sessions/
3. Run backend once and verify API docs load
4. Run frontend once and validate both text and game flows
5. Confirm README instructions match your latest code

## Contributors

- Rifat Hossain
- Denesh Pantho Barua
- Nino Chakma

## License

MIT License (see LICENSE file)
