# MindViz

MindViz is a desktop mental wellness application that turns emotional patterns into an interactive visual journey.
It supports:

- Text-based emotional analysis
- Game-based behavioral analysis (no writing required)
- **Optional face image capture** for multimodal wellness assessment

The system then recommends personalized techniques, visualizes your state as a 3D garden, and tracks your progress over time.

## Why MindViz

- Practical daily check-in for stress, anxiety, and mood
- Fast feedback loop: analyze -> practice -> re-check
- Visual-first experience instead of plain text-only reporting
- Local-first storage for user and session history

## Core Features

- AI-powered emotional metric extraction (anxiety, mood, stress)
- Gameplay-based mental state detection (reaction + behavior signals)
- **Optional webcam face capture with facial emotion analysis**
- **Multimodal fusion: text + face signals combined for richer wellness indicator**
- 3D mental garden that adapts to emotional metrics
- Personalized recommendations from a 20-technique wellness library
- Guided exercise sessions with animated, technique-specific widgets
- Journey mode with 3D historical progress map and trend indicators
- Gemini API support with demo fallback when API key is unavailable

## Face Capture Feature

### How it works

1. On the input screen, an optional **Face Analysis** panel appears on the right.
2. Click **▶ Start** to open your laptop camera.
3. Click **📸 Capture** to freeze the frame (camera is released immediately).
4. Check **Use face analysis** to include your facial expression in the analysis.
5. Click **ANALYZE MY STATE** — the captured image is sent to the backend alongside your text.
6. The backend analyzes the face with **Gemini Vision API** (primary) or **DeepFace** (fallback).
7. Text and face emotion scores are **fused** (default: 70% text + 30% face) into the final wellness metrics.
8. If camera is unavailable or face not detected, the app falls back to text-only mode automatically.

### Camera permission requirements

- The app requests access to your default system camera (index 0).
- No images are stored on disk; only the derived emotion scores are kept.
- You must explicitly check **Use face analysis** to enable the feature.

### Running with face analysis enabled

Install the extra dependency for both backend and frontend:

```bash
pip install opencv-python
```

Then start the app as usual:

```bash
cd backend && python server.py    # terminal 1
cd frontend && python main.py     # terminal 2
```

### Running without face analysis (text-only)

If `opencv-python` is not installed the camera section shows an informational message and the rest of the app works exactly as before — no code changes needed.

### Privacy note

- Captured images are sent only to the Gemini API (if configured) for analysis.
- Images are **never written to disk**.
- Only derived emotion scores and timestamps are saved in session history.
- Face analysis uses only the image you explicitly capture; the camera stops as soon as you click Capture.

> ⚠️ Disclaimer: Face analysis is a wellness support feature, not a medical diagnosis.  
> Do not use this application as a substitute for professional mental health care.

## Project Architecture

- Frontend: PyQt5 + PyOpenGL + OpenCV (optional, for webcam)
- Backend: FastAPI + Uvicorn
- Analysis: Gemini API (text + vision) or fallback analyzer
- Storage: local JSON files under data/

### Runtime Flow

1. User chooses text mode or game mode
2. Frontend sends payload to backend (optionally includes face image)
3. Backend computes emotional metrics (text + optional face fusion)
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
│       ├── face_analyzer.py        ← new: face emotion analysis
│       ├── game_analyzer.py
│       ├── rag_system.py
│       └── visualizer.py
├── frontend/
│   ├── main.py
│   ├── requirements.txt
│   ├── screens/
│   │   ├── welcome_screen.py
│   │   ├── auth_screen.py
│   │   ├── input_screen.py         ← updated: webcam capture panel added
│   │   ├── game_mode_screen.py
│   │   ├── game_screen.py
│   │   ├── loading_screen.py       ← updated: forwards face image to backend
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
├── tests/
│   └── test_face_feature.py        ← new: unit tests for face feature
├── run_mindviz.bat
├── run_mindviz.ps1
└── test_api.py
```

## Prerequisites

- Python 3.10+ (recommended)
- Windows for one-click launcher scripts
- OpenGL-capable graphics driver for best visual experience
- `opencv-python` for face capture (optional — app works without it)

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

Welcome -> Sign in or Guest -> Describe feelings -> (optionally capture face) -> Analyze -> Result -> Start recommended session

### Game Mode

Welcome -> Play a Game Instead -> Select duration -> Play bubble game -> Analyze gameplay -> Result

## API Endpoints

- GET /
  - Health check
- POST /analyze
  - Text-based emotional analysis (accepts optional `face_image_base64`)
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
- Face images are never stored; only derived emotion scores are saved

## Testing and Validation

Unit tests (no server needed):

```bash
python -m pytest tests/test_face_feature.py -v
```

Backend smoke test (requires running server):

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

### Camera not working

- Make sure `opencv-python` is installed: `pip install opencv-python`
- Check that your system camera is not in use by another application
- If camera access is denied, the app continues in text-only mode

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
