# Survey Insights & Implemented Features in MindViz

**Survey Respondents:** 14 students (primarily from CUET, CSE department, undergraduate level)  
**Average likelihood to use MindViz:** 7.71 / 10

---

## Key Insights from the Survey → What Was Already Implemented

---

### 1. How Should the System Know Your Mental State?

**Survey Finding:**

- 42.9% wanted **all input options** (text, emoji, questions)
- 28.6% specifically wanted **free-text input analyzed by AI**

**What's Implemented in MindViz:**

- The `input_screen.py` provides a **free-text input box** where users type their feelings in natural language
- **Quick emoji presets** (Anxious / Sad / Stressed / Good) are available as one-click shortcuts
- The **Gemini AI** (`gemini_analyzer.py`) performs AI-powered analysis of the typed text
- **Fallback keyword analysis** exists when no API key is available — keeping it accessible

**Direct survey-to-feature match: ✅ Text input + emoji shortcuts = covers the top two survey preferences**

---

### 2. The 3D Garden Visualization

**Survey Finding:**

- 35.7% cared most about **rain and clouds** as stress indicators
- Equal votes (~21.4% each) for sky color, wind/movement, and flower health
- 35.7% wanted **all elements together**

**What's Implemented in MindViz:**

- `garden_renderer.py` renders a full 3D scene with:
  - **Sky color and brightness** — mapped from `mood` score (blue/orange/dark)
  - **Rain and clouds** — cloud darkness, cloud count, and rain intensity mapped from `stress` and `anxiety`
  - **Flower health and drooping** — `flower_health` and `flower_droop` mapped from `mood`
  - **Wind and grass swaying** — `wind_speed` mapped from `anxiety`
  - **Butterflies and fireflies** — appear based on wellness level
- `visualizer.py` maps all three metrics (anxiety, mood, stress) to every visual parameter

**Direct survey-to-feature match: ✅ All garden elements the survey asked for are implemented**

---

### 3. Should the System Show Specific Numbers?

**Survey Finding:**

- 42.9% wanted **both numbers and visualization**
- 21.4% wanted numbers with **visual bars**
- 0% wanted _only_ the garden without any numbers

**What's Implemented in MindViz:**

- `result_screen.py` shows a **split layout**:
  - Left 60%: 3D garden visualization (OpenGL)
  - Right 40%: **Exact percentage bars** for Anxiety, Mood, and Stress with labels
- Users see both the garden AND the numbers simultaneously

**Direct survey-to-feature match: ✅ Both visualization + numeric bars are shown side by side**

---

### 4. Guided Breathing as a Training Technique

**Survey Finding:**

- **Guided breathing exercises (5 mins)** was the most popular technique — 50% selected it
- 28.6% wanted **animated circle** showing when to breathe in/out
- 28.6% wanted **real-time improvement feedback** (e.g., "Anxiety dropping...")

**What's Implemented in MindViz:**

- `session_screen.py` contains a full **guided breathing session**:
  - `BreathingCircle` widget draws an animated circle that expands/contracts for inhale → hold → exhale
  - Phase text ("INHALE", "HOLD", "EXHALE") displayed live
  - **Real-time metric improvement simulation** shown during the session (anxiety/mood/stress bars updating live)
  - Cycle counter tracks progress
  - Sessions are saved to backend on completion

**Direct survey-to-feature match: ✅ Animated breathing circle + real-time feedback both implemented**

---

### 5. Would Real-Time Feedback Motivate You?

**Survey Finding:**

- **57.1% said YES** — seeing improvement would keep them going

**What's Implemented in MindViz:**

- During the guided session in `session_screen.py`, the metrics (Anxiety %, Mood %, Stress %) update in real-time as the session progresses — simulating live improvement feedback
- Users visually see their numbers changing while they practice breathing

**Direct survey-to-feature match: ✅ Real-time improvement feedback is a core feature of the session screen**

---

### 6. Progress Tracking Over Time

**Survey Finding:**

- **64.3% absolutely need progress tracking** or want it simple
- 35.7% each preferred a **3D path map** and having **all options available**
- Most frequent check-in: weekly or when feeling down

**What's Implemented in MindViz:**

- `journey_screen.py` provides a full **3D session journey visualization**:
  - 3D OpenGL path with **colored spheres** (red → green based on wellbeing) for each session
  - Connecting tubes and ribbon path showing improvement over time
  - Stats panel: total sessions, average improvement %, favorite technique, and trend
- Sessions are saved locally via the backend to `data/sessions/` (per-user JSON files)

**Direct survey-to-feature match: ✅ 3D path map was the #1 preference and it is exactly what was built**

---

### 7. Privacy — Local Data Storage

**Survey Finding:**

- **50% said it is "Extremely important" or "Important"** that data stays on their computer
- Only 1 person said it was not important

**What's Implemented in MindViz:**

- All sessions are stored in `data/sessions/<username>/sessions.json` — **100% local files**
- No cloud, no third-party server, no data upload
- The only external call is to Gemini API for text analysis, with a **local keyword fallback** when no API key is present

**Direct survey-to-feature match: ✅ Full local storage, no cloud dependency**

---

### 8. AI Trust Concern

**Survey Finding:**

- 50% were "Maybe" or "Concerned but willing to try" — they want to see how it works first

**What's Implemented in MindViz:**

- The result screen shows the AI's reasoning transparently — users see the exact anxiety/mood/stress scores
- `gemini_analyzer.py` includes a keyword-based fallback — so the system works and is usable without trusting AI blindly
- Users have control: they can input text manually and see exactly what scores are generated

**Direct survey-to-feature match: ✅ Transparent scoring + fallback mode addresses trust concerns**

---

### 9. Personalized Technique Recommendations

**Survey Finding:**

- One of the top open-ended requests: _"Personalized technique for reducing stress or other mental health issues"_

**What's Implemented in MindViz:**

- `rag_system.py` implements a **RAG (Retrieval-Augmented Generation) system** that:
  - Scores 6 techniques against the user's specific anxiety/mood/stress profile
  - Returns the **top 3 most relevant techniques** with full descriptions
  - Technique content is loaded from 20 evidence-based files in `data/techniques/`
- Result screen shows these as scrollable **recommendation cards** with a "START NOW" button

**Direct survey-to-feature match: ✅ Personalized recommendations based on individual emotional scores**

---

### 10. Simple, Engaging, Not Just Numbers

**Survey Finding:**

- Top open-ended feedback: _"Make them simple, engaging, and not just numbers or text — visuals and interactive elements matter more"_
- _"Keep it simplest"_
- _"Nice animation throughout"_

**What's Implemented in MindViz:**

- Full 3D animated garden with ~60 FPS rendering (butterflies, rain splashes, swaying grass, fireflies)
- Animated breathing circle during sessions
- 3D journey path with rotating camera, glowing particles, aura effects
- Animated loading screen while waiting for AI analysis
- Simple, clean PyQt5 UI with color-coded feedback

**Direct survey-to-feature match: ✅ Visual-first, animation-heavy design aligns with student feedback**

---

## Summary Table

| Survey Insight                                 | Feature Implemented in MindViz                           |
| ---------------------------------------------- | -------------------------------------------------------- |
| Free-text AI input (28.6%) + Emoji shortcuts   | `input_screen.py` — text box + Quick emoji buttons       |
| All garden elements (rain, sky, wind, flowers) | `garden_renderer.py` — full 3D garden with all elements  |
| Both numbers AND visualization (42.9%)         | `result_screen.py` — side-by-side bars + 3D garden       |
| Guided breathing as top technique (50%)        | `session_screen.py` — animated breathing circle          |
| Real-time improvement feedback (57.1%)         | `session_screen.py` — live metric updates during session |
| 3D progress path map (top choice)              | `journey_screen.py` — 3D colored sphere journey          |
| Local data privacy (50%+ cared)                | `data/sessions/` — fully local JSON storage, no cloud    |
| Personalized technique recommendations         | `rag_system.py` — RAG scoring for top 3 techniques       |
| Simple, visual, engaging design                | Full OpenGL 3D rendering + animations throughout         |
| AI trust transparency                          | Score breakdown shown + keyword fallback available       |

---

## What the Survey Confirmed About the Project Direction

1. **The core concept was validated** — 78.6% said "Yes definitely" or "Maybe" to using a 3D garden visualization app
2. **The breathing exercise focus was correct** — it was the single most-wanted technique
3. **The privacy-first approach was the right call** — majority of users consider local storage important
4. **Real-time feedback was essential** — the majority would be motivated by seeing live improvement
5. **The 3D journey map was exactly what users wanted** — tied as the #1 progress visualization preference

---

_Average likelihood to use MindViz if it had all features: **7.71 / 10** — a strong validation score from the target audience (CUET CSE students)_
