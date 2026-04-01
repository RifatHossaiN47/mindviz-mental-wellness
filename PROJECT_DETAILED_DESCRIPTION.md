# MindViz: Complete Project Description

## 1. Project Overview

MindViz is a desktop mental wellness application that combines:

- Free-text emotional check-ins
- AI-based emotional metric extraction (anxiety, mood, stress)
- Personalized coping-technique recommendations
- Rich OpenGL visualizations (garden state, guided exercises, progress journey)
- Local session history tracking per user

The user experience is designed as a full loop:

1. User describes current feelings.
2. Backend analyzes text and computes emotional metrics.
3. System recommends top techniques.
4. User runs a guided 1-minute exercise session.
5. Session effect is simulated and saved.
6. User can review longitudinal progress on a 3D journey map.

## 2. Tech Stack and Architecture

### Frontend

- Python + PyQt5 UI
- OpenGL (PyOpenGL) for real-time visual scenes
- Synchronous HTTP calls to backend via requests

### Backend

- FastAPI + Uvicorn
- Gemini API integration for analysis (with keyword-based demo fallback)
- Local JSON file storage for users and session history

### Data Storage

- Local files only under data/
- No database server
- Per-user session history stored in JSON

## 3. Directory Structure (Functional View)

- frontend/: Desktop application and all UI screens
- frontend/screens/: Screen-level workflows (welcome, auth, input, loading, result, session, journey)
- frontend/opengl/: Visual renderers (garden, journey, exercise-specific widgets)
- frontend/utils/: API client helper
- backend/: FastAPI app and analysis/recommendation/visual mapping modules
- backend/modules/: Core intelligence modules
- data/users.json: Auth records (username + SHA-256 password hash)
- data/sessions/<username>/sessions.json: Session timeline
- data/techniques/: Technique instruction text corpus
- setup_project.py: Bootstrap utility for folders/templates/content
- run_mindviz.bat / run_mindviz.ps1: Startup automation
- test_api.py: Backend endpoint smoke test

## 4. End-to-End Runtime Flow

1. Frontend starts (QMainWindow + QStackedWidget).
2. User navigates welcome -> auth (or guest) -> input.
3. Input text is sent to backend /analyze.
4. Backend pipeline:
   - Analyze text with Gemini or demo fallback
   - Select top recommendations via RAG scoring over technique corpus
   - Map metrics to detailed visual parameters
5. Frontend loads result screen:
   - Left: 3D garden based on visual parameters
   - Right: textual analysis, metric bars, recommendation cards
6. User starts one recommendation session.
7. Session screen runs 1-minute guided animation + metric updates.
8. Session is posted to /save-session.
9. Journey screen can later fetch all sessions from /get-sessions/{username} and render a 3D historical path.

## 5. Frontend Screen-by-Screen Detailed Behavior

## 5.1 Screen Manager (frontend/main.py)

MindVizApp is the central navigation controller.

- Uses QStackedWidget to switch screens.
- clear_and_add keeps only last 3 screens in memory (older widgets removed with deleteLater).
- Exposes methods:
  - show_welcome_screen
  - show_auth_screen(mode)
  - show_input_screen(username)
  - show_loading_screen(text, username)
  - show_result_screen(result, username)
  - show_session_screen(technique, initial_metrics, username)
  - show_journey_screen(username)

This creates a predictable single-window flow with stack-based transitions.

## 5.2 Welcome Screen (frontend/screens/welcome_screen.py)

Purpose: App entry and route selection.

UI elements:

- Title + subtitle + short description
- Buttons:
  - Sign In -> auth screen in signin mode
  - Create Account -> auth screen in signup mode
  - Continue as Guest -> input screen with username Guest
- Static developer credits block at bottom

Behavior:

- No backend calls.
- Pure routing screen.

## 5.3 Auth Screen (frontend/screens/auth_screen.py)

Purpose: Local account creation and sign-in.

Modes:

- signin
- signup (adds confirm password input)

Validation:

- Non-empty username/password
- Username length >= 3
- Password length >= 4
- Signup requires matching confirm password

Storage behavior:

- users loaded from data/users.json
- Passwords stored as SHA-256 hashes
- On signup, creates user session directory data/sessions/<username>/

Actions:

- Back -> welcome
- Toggle link switches signin/signup
- Successful signin -> input screen with username

## 5.4 Input Screen (frontend/screens/input_screen.py)

Purpose: Capture current emotional state.

UI elements:

- Header with app title and Welcome, <username>
- Large QTextEdit with placeholder examples
- Quick preset buttons:
  - Anxious
  - Sad
  - Stressed
  - Good
- Main CTA: ANALYZE MY STATE
- Secondary actions:
  - View My Journey
  - Logout

Behavior:

- analyze_state requires non-empty text.
- On valid text -> loading screen with user text and username.
- View My Journey -> journey screen.
- Logout -> welcome screen.

## 5.5 Loading Screen (frontend/screens/loading_screen.py)

Purpose: Transitional status while analysis runs.

UI/animation:

- Title Analyzing
- Subtitle with animated trailing dots every 500ms
- Progress bar increments up to 85% with staged status text:
  - Connecting to AI
  - Analyzing emotional content
  - Generating recommendations

Backend call:

- Sends POST to http://localhost:8000/analyze with:
  - user_input
  - username
- On success:
  - Sets progress to 100%
  - Stops timers
  - Delays 800ms
  - Navigates to result screen with response payload
- On failure:
  - Shows error dialog
  - Returns user to input screen

## 5.6 Result Screen (frontend/screens/result_screen.py)

Purpose: Display full analysis and offer next actions.

Layout:

- Left panel (~55%): GardenWidget OpenGL visualization
- Right panel (~45%): Scrollable analysis and controls

Right-panel sections:

1. Heading and divider
2. AI analysis cards (if analysis exists):
   - Primary emotion badge
   - Summary card
   - Mental state card
   - Emotional details list card
   - Body connection card
   - Strength noted card
   - Garden description card
3. Emotional metrics:
   - Anxiety, Mood, Stress bars
   - Severity labels:
     - Mood: Very Positive -> Very Low
     - Anxiety/Stress: Minimal -> Severe
4. Explanation box (analysis summary or fallback explanation)
5. Recommendation cards for top techniques:
   - Technique name
   - Duration
   - Effects summary
   - START NOW button
6. Bottom actions:
   - New Assessment
   - View Journey

Actions:

- START NOW -> session screen with chosen technique and initial metrics.
- New Assessment -> input screen.
- View Journey -> journey screen.

## 5.7 Session Screen (frontend/screens/session_screen.py)

Purpose: Run guided 1-minute intervention with live feedback.

Session model:

- Duration fixed to 60 seconds.
- Progress updates every second.
- Exercise visualization widget selected by technique id.

UI elements:

- Header with technique name and Exit Session button
- Progress label + progress bar
- Technique-specific animated widget (from get_exercise_widget)
- Real-time metric feedback text block

Live metric simulation:

- Every 10 seconds, apply partial effect from technique effects.
- improvement_rate = 0.18 each update.
- Metrics clamped to [0, 1].
- Text shows before -> current with status arrows.

Completion behavior:

- Stop timer and exercise animation
- POST session to /save-session with:
  - username
  - initial_metrics
  - final_metrics
  - technique id
  - duration=1
- Show completion dialog with summarized improvements
- Return to input screen

Exit behavior:

- Stop timer and animation
- Return to input screen without completion dialog

## 5.8 Journey Screen (frontend/screens/journey_screen.py)

Purpose: Show historical progress and summary stats.

Data load:

- GET /get-sessions/{username}
- sessions list stored in memory

Layout:

- Left (70%): 3D JourneyWidget if at least 2 sessions, else placeholder
- Right (30%): Stats, point detail panel, explanation, back button

Stats computed:

- Total sessions
- Average improvement (mean of anxiety/stress/mood improvement entries)
- Favorite technique (most frequent technique id)
- Recent trend from last 3 sessions (based on wellbeing delta)

Interactive detail panel:

- JourneyWidget emits point_clicked(index)
- Screen updates selected session detail with:
  - session number and technique
  - date
  - anxiety/mood/stress before/after with arrows

Back action:

- Returns to input screen.

## 6. Backend API Detailed Behavior

## 6.1 API App (backend/server.py)

Framework: FastAPI with permissive CORS (\*).

Request models:

- AnalyzeRequest:
  - user_input: str
  - username: str
- SessionSaveRequest:
  - username: str
  - initial_metrics: dict
  - final_metrics: dict
  - technique: str
  - duration: int

Endpoints:

1. GET /

- Health message/status payload.

2. POST /analyze

- Pipeline:
  1. metrics = analyze_with_gemini(user_input)
  2. recommendations = get_recommendations(metrics)
  3. visualization = map_to_visualization(metrics)
- Returns:
  - metrics
  - recommendations
  - visualization
  - timestamp

3. POST /save-session

- Ensures user session directory exists.
- Loads existing sessions.json if present.
- Appends new session object with improvement values:
  - anxiety improvement = initial anxiety - final anxiety
  - mood improvement = final mood - initial mood
  - stress improvement = initial stress - final stress
- Writes updated sessions list back to file.

4. GET /get-sessions/{username}

- Returns sessions list if file exists.
- Returns empty list otherwise.

## 7. Emotional Analysis Module (backend/modules/gemini_analyzer.py)

Startup mode selection:

- Reads GEMINI_API_KEY from environment.
- If missing or placeholder value, enables demo mode.
- Else configures google.generativeai with model gemini-pro.

analyze_with_gemini(user_input):

1. If demo mode -> demo_analysis(user_input).
2. Else:
   - Sends detailed scoring prompt for anxiety/mood/stress in [0,1].
   - Parses model response with regex.
   - Clamps values to [0,1].
   - Sends second prompt requesting structured JSON analysis text.
   - If second parse fails, uses fallback generator.
3. Returns dict:
   - anxiety
   - mood
   - stress
   - analysis: summary, primary_emotion, emotional_details, mental_state, body_connection, strength_noted, garden_description

Fallback components:

- \_generate_fallback_analysis builds narrative from metrics.
- demo_analysis computes keyword-weighted scores for anxiety/mood/stress and then uses fallback narrative generation.

## 8. Recommendation/RAG Module (backend/modules/rag_system.py)

Core data:

- TECHNIQUES dictionary contains 21 recommendation entries (includes both 07_deep_breathing and 07_mindful_walking as separate ids).
- Each entry defines:
  - id/key
  - display name
  - duration
  - source text file
  - good_for tags
  - expected effects on metrics

Scoring strategy in get_recommendations(metrics):

1. Load all technique text files.
2. For each technique, compute score from:
   - Primary metric/tag alignment (anxiety/stress/mood thresholds)
   - Content keyword matches in loaded technique text
   - Effect magnitude weighting for needed dimensions
   - General effectiveness bonus
3. Sort descending by score.
4. Return top 3 with:
   - id
   - name
   - duration
   - effects
   - full content text
   - relevance_score

## 9. Visualization Mapping Module (backend/modules/visualizer.py)

Function: map_to_visualization(metrics)

Inputs:

- anxiety
- mood
- stress

Core computed index:

- wellbeing = (1 - anxiety + mood + (1 - stress)) / 3

Output includes a rich set of visual parameters used by GardenWidget, for example:

- Sky and lighting: sky_color, horizon_color, sun_intensity, sun_color, time_of_day
- Weather: cloud_darkness, cloud_count, rain_intensity, lightning, show_rainbow, fog_density
- Motion: wind_speed
- Flora: flower_droop, flower_health, flower_count, flower_bloom, tree_health, leaf_density, leaf_fall_rate, grass_color
- Water: water_clarity, water_ripple_speed
- Creatures/effects: butterfly_count, bird_count, firefly_count, god_rays, star_count, sparkle_intensity
- Terrain/meta: path_visibility, mountain_snow, mountain_color, wellbeing

This is the bridge between abstract emotional metrics and concrete render-time scene behavior.

## 10. OpenGL Visualization Modules

## 10.1 Garden Renderer (frontend/opengl/garden_renderer.py)

GardenWidget is a full 3D scene renderer with dynamic animation.

Scene composition:

- Sky dome gradient
- Stars (for low mood/night states)
- Sun or moon
- Optional rainbow and god rays
- Mountains and ground tiles
- Path, pond, border stones, optional lily pads
- Trees, bushes, rocks, flowers, grass
- Clouds, rain, falling leaves
- Butterflies, birds, fireflies
- Sparkles and atmosphere particles

Animation:

- QTimer tick ~16ms (about 60 FPS)
- Updates particle positions, wing flaps, leaf fall, rain recycling, etc.
- Slight camera sway over time

Overlay:

- Draws semi-transparent 2D status cards on top using QPainter:
  - Overall wellbeing score and bar
  - Anxiety/mood/stress mini bars
  - Primary emotion + garden description snippets

## 10.2 Journey Renderer (frontend/opengl/journey_renderer.py)

JourneyWidget is an interactive 3D timeline.

Point generation:

- One point per saved session
- X-axis progresses by session index
- Y-axis represents final wellbeing
- Z-axis sinusoidal offset for curved path
- Color based on final wellbeing (red -> green)
- Size increases for newer sessions

Rendered layers:

- Sky background
- Grid floor and wellbeing zones
- Multi-layer glowing path between sessions
- Vertical bars and ground circles per point
- Spheres with glow, sparkles, selection ring
- Connecting cylinders/beams
- Particle trail along the path
- Start/latest markers

Interaction:

- mousePressEvent performs point picking via gluProject
- Emits point_clicked(index) for selected or deselected point

2D overlay panel:

- Top summary bar with session count
- Right-side detail panel for selected session with:
  - Technique/date
  - Before/after bars for each metric
  - Change percentages and color cues
  - Overall wellbeing and delta vs start

## 10.3 Exercise Widget System (frontend/opengl/exercise_widgets.py)

BaseExerciseWidget:

- Shared timer-driven animation loop (~30 FPS)
- Common text drawing helpers

Factory:

- get_exercise_widget(technique_id) maps recommendation id to widget class
- Unknown id falls back to Breathing478Widget

Implemented guided widgets (21):

1. breathing_478: 4-7-8 breathing cycle animation
2. progressive_relaxation: body/muscle tense-relax guide
3. cognitive_reframe: negative-to-positive thought transformation flow
4. box_breathing: square-trace inhale/hold/exhale/hold cycle
5. grounding_54321: senses countdown (5-4-3-2-1)
6. body_scan: scan beam moving through body regions
7. deep_breathing: diaphragm-focused inhale/exhale guide
8. mindful_walking: footsteps + attention cues
9. gratitude_practice: gratitude prompts + heart visuals
10. visualization: peaceful scene gradually built over time
11. positive_affirmations: rotating affirmation prompts
12. journaling: writing-themed guided prompt flow
13. music_therapy: waveform/equalizer calming animation
14. physical_exercise: exercise movement + heart-rate style indicators
15. social_connection: connection-network visual metaphor
16. sleep_hygiene: night scene and sleep habit cues
17. time_in_nature: nature-growth style animation
18. digital_detox: phone fade-out to calmer visuals
19. healthy_eating: nutrition/mindful-eating guidance visuals
20. stretching: posture/stretch cue animation
21. professional_support: help-seeking informational guidance visuals

## 11. Data Model and Persistence

## 11.1 Users (data/users.json)

Structure:

- Top-level object keyed by username
- Each user contains:
  - password: SHA-256 hash string
  - created_at: ISO timestamp

## 11.2 Sessions (data/sessions/<username>/sessions.json)

Each session entry includes:

- date
- initial_metrics
- final_metrics
- technique (id)
- duration
- improvement object:
  - anxiety
  - mood
  - stress

Notes:

- Some historical sample records use older duration values (e.g., 5 or 10), while current session flow stores duration=1 (minute).

## 11.3 Technique Corpus (data/techniques/\*.txt)

Technique files are human-readable instruction guides used by recommendation logic and UI content display.

Current library titles include:

- 4-7-8 breathing
- Progressive relaxation
- Cognitive reframing
- Box breathing
- 5-4-3-2-1 grounding
- Body scan
- Deep breathing
- Mindful walking
- Gratitude practice
- Visualization
- Positive affirmations
- Stress journaling
- Music for relaxation
- Physical activity
- Social connection
- Sleep hygiene
- Nature therapy
- Digital detox
- Nutrition for mental health
- Gentle stretching
- Professional support

## 12. Launch, Setup, and Testing Utilities

## 12.1 run_mindviz.bat

- Starts backend in one terminal window.
- Waits 3 seconds.
- Starts frontend in another window.
- Prints backend/docs URLs.

## 12.2 run_mindviz.ps1

- PowerShell equivalent launcher.
- Same two-process startup pattern.

## 12.3 setup_project.py

- Creates standard folder structure.
- Generates additional technique text files.
- Creates backend/.env.example.
- Can generate README template.

## 12.4 test_api.py

- Checks backend availability.
- Calls /analyze with sample input.
- Prints metrics/recommendations/visualization summary.
- Saves full payload to test_response.json.

## 13. Dependency Snapshot

Backend requirements:

- fastapi
- uvicorn
- google-generativeai
- python-multipart
- pydantic
- python-dotenv

Frontend requirements:

- PyQt5
- PyOpenGL
- requests

## 14. Important Behavioral Characteristics

- App is local-first for storage (users/sessions in local JSON files).
- Analysis call can work in two modes:
  - Real Gemini API mode
  - Demo keyword fallback mode
- Screen navigation is controlled centrally by the stacked-widget manager.
- Recommendation and session subsystems use technique ids consistently to map:
  - recommendation data
  - technique content
  - exercise visualization widget
- Journey visualization is interactive and supports click-to-inspect per session point.

## 15. Practical Summary

MindViz is a complete local desktop workflow for emotional check-in, AI-guided interpretation, personalized short intervention, and historical reflection.

The project is not just a static UI: it has a full data and behavior loop across frontend rendering, backend inference/recommendation logic, session persistence, and interactive longitudinal analytics.
