from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from modules.gemini_analyzer import analyze_with_gemini
from modules.game_analyzer import analyze_game_metrics
from modules.rag_system import get_recommendations
from modules.visualizer import map_to_visualization
import json
import os
from datetime import datetime

app = FastAPI(title="MindViz API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeRequest(BaseModel):
    user_input: str
    username: str

class GameAnalyzeRequest(BaseModel):
    username: str
    game_data: dict
    duration_minutes: int

class SessionSaveRequest(BaseModel):
    username: str
    initial_metrics: dict
    final_metrics: dict
    technique: str
    duration: int

@app.get("/")
def read_root():
    return {"message": "MindViz API is running!", "status": "healthy"}

@app.post("/analyze")
async def analyze(request: AnalyzeRequest):
    try:
        print("\n" + "="*60)
        print(f"[ANALYZE] Request from user: {request.username}")
        print(f"[ANALYZE] Input text: {request.user_input[:100]}...")
        print("="*60)
        
        # Step 1: AI Analysis (Gemini)
        print("[STEP 1] Starting Gemini analysis...")
        metrics = analyze_with_gemini(request.user_input)
        print(f"[STEP 1] ✓ Metrics received: {metrics}")
        
        # Step 2: Get recommendations
        print("[STEP 2] Getting recommendations based on metrics...")
        recommendations = get_recommendations(metrics)
        print(f"[STEP 2] ✓ Generated {len(recommendations)} recommendations")
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec['name']} (relevance: {rec.get('relevance_score', 'N/A')})")
        
        # Step 3: Map to visualization
        print("[STEP 3] Mapping to visualization parameters...")
        visualization = map_to_visualization(metrics)
        print(f"[STEP 3] ✓ Visualization params: wellbeing={visualization['wellbeing']}, sky_color={visualization['sky_color'][:2]}...")
        
        result = {
            "metrics": metrics,
            "recommendations": recommendations,
            "visualization": visualization,
            "timestamp": datetime.now().isoformat()
        }
        print("[SUCCESS] Analysis complete! Sending response to frontend.")
        print("="*60 + "\n")
        return result
    
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze-game")
async def analyze_game(request: GameAnalyzeRequest):
    try:
        print("\n" + "="*60)
        print(f"[ANALYZE-GAME] Request from user: {request.username}")
        print(f"[ANALYZE-GAME] Duration: {request.duration_minutes} minute(s)")
        print("="*60)

        # Step 1: Gameplay metrics analysis
        print("[STEP 1] Starting game behavior analysis...")
        metrics = analyze_game_metrics(request.game_data)
        print(f"[STEP 1] ✓ Metrics received: {metrics}")

        # Step 2: Get recommendations
        print("[STEP 2] Getting recommendations based on metrics...")
        recommendations = get_recommendations(metrics)
        print(f"[STEP 2] ✓ Generated {len(recommendations)} recommendations")
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec['name']} (relevance: {rec.get('relevance_score', 'N/A')})")

        # Step 3: Map to visualization
        print("[STEP 3] Mapping to visualization parameters...")
        visualization = map_to_visualization(metrics)
        print(f"[STEP 3] ✓ Visualization params: wellbeing={visualization['wellbeing']}, sky_color={visualization['sky_color'][:2]}...")

        result = {
            "metrics": metrics,
            "recommendations": recommendations,
            "visualization": visualization,
            "timestamp": datetime.now().isoformat(),
            "source": "game"
        }
        print("[SUCCESS] Game analysis complete! Sending response to frontend.")
        print("="*60 + "\n")
        return result

    except Exception as e:
        print(f"[ERROR] {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/save-session")
async def save_session(request: SessionSaveRequest):
    try:
        session_dir = f"../data/sessions/{request.username}"
        os.makedirs(session_dir, exist_ok=True)
        
        session_file = f"{session_dir}/sessions.json"
        
        # Load existing sessions
        sessions = []
        if os.path.exists(session_file):
            with open(session_file, 'r') as f:
                sessions = json.load(f)
        
        # Add new session
        new_session = {
            "date": datetime.now().isoformat(),
            "initial_metrics": request.initial_metrics,
            "final_metrics": request.final_metrics,
            "technique": request.technique,
            "duration": request.duration,
            "improvement": {
                "anxiety": request.initial_metrics.get('anxiety', 0) - request.final_metrics.get('anxiety', 0),
                "mood": request.final_metrics.get('mood', 0) - request.initial_metrics.get('mood', 0),
                "stress": request.initial_metrics.get('stress', 0) - request.final_metrics.get('stress', 0)
            }
        }
        
        sessions.append(new_session)
        
        # Save
        with open(session_file, 'w') as f:
            json.dump(sessions, f, indent=2)
        
        return {"message": "Session saved successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get-sessions/{username}")
async def get_sessions(username: str):
    try:
        session_file = f"../data/sessions/{username}/sessions.json"
        
        if not os.path.exists(session_file):
            return {"sessions": []}
        
        with open(session_file, 'r') as f:
            sessions = json.load(f)
        
        return {"sessions": sessions}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    print("=" * 60)
    print("🌱 MindViz Backend Server")
    print("=" * 60)
    print("Starting server at: http://localhost:8000")
    print("API Docs at: http://localhost:8000/docs")
    print("=" * 60)
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
