import google.generativeai as genai
import os
from dotenv import load_dotenv
import re
import json

# Load environment variables
load_dotenv()

# Configure Gemini
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

if not GEMINI_API_KEY or GEMINI_API_KEY == 'your_api_key_here':
    print("[WARNING] No valid Gemini API key found! Using DEMO MODE.")
    print("[WARNING] Get your free key at: https://aistudio.google.com/app/apikey")
    USE_DEMO_MODE = True
else:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-pro')
    USE_DEMO_MODE = False
    print("[INFO] ✓ Gemini API configured successfully!")
    print(f"[INFO] Using API key: {GEMINI_API_KEY[:20]}...")


def analyze_with_gemini(user_input):
    """Analyze user's feelings using Gemini AI - returns metrics + detailed text analysis"""
    
    if USE_DEMO_MODE:
        print("[GEMINI] Using DEMO MODE (keyword-based analysis)")
        return demo_analysis(user_input)
    
    print("[GEMINI] Using REAL Gemini API...")
    
    try:
        # --- STEP 1: Get precise emotional metrics ---
        metrics_prompt = f"""You are a board-certified clinical psychologist with 20 years of experience in emotional assessment.
Analyze this patient's message with extreme precision and clinical accuracy.

Patient's exact words: "{user_input}"

Score these three dimensions. Base scores STRICTLY on what the patient said - every word matters.

ANXIETY (0.0 to 1.0):
  0.0-0.1 = Completely peaceful, zero worry
  0.1-0.3 = Slight unease, minor concerns ("a bit nervous", "slightly worried")
  0.3-0.5 = Moderate anxiety, noticeable worry ("feeling anxious", "can't stop thinking")
  0.5-0.7 = High anxiety, significant distress ("very anxious", "heart racing", "panic")
  0.7-0.9 = Severe anxiety, near panic ("overwhelming fear", "can't breathe", "losing control")
  0.9-1.0 = Extreme crisis-level anxiety ("full panic attack", "feel like dying")
  
  Key signals: worry, nervousness, fear, panic, uncertainty, racing thoughts, dread, 
  restlessness, overthinking, catastrophizing, physical symptoms (shaking, sweating)

MOOD (0.0 to 1.0):
  0.0-0.1 = Severely depressed, hopeless, suicidal ideation
  0.1-0.3 = Very low mood, persistent sadness, loss of interest ("feel empty", "nothing matters")
  0.3-0.5 = Low-moderate mood, down but functional ("feeling down", "not great")
  0.5-0.6 = Neutral/mixed feelings ("okay", "not bad not good")
  0.6-0.7 = Mildly positive ("pretty good", "doing alright")
  0.7-0.85 = Good mood, genuine happiness ("feeling great", "happy", "grateful")
  0.85-1.0 = Exceptionally positive, euphoric ("best day ever", "absolutely wonderful")
  
  Key signals: sadness, hopelessness, emptiness, joy, excitement, contentment, gratitude,
  enthusiasm, crying, laughter, motivation, energy levels

STRESS (0.0 to 1.0):
  0.0-0.1 = Completely relaxed, no responsibilities weighing
  0.1-0.3 = Mild pressure, manageable tasks ("a bit busy", "some work to do")
  0.3-0.5 = Moderate stress, feeling stretched ("lots on my plate", "busy schedule")
  0.5-0.7 = High stress, struggling to cope ("overwhelmed", "too much", "can't keep up")
  0.7-0.9 = Severe stress, near burnout ("crumbling under pressure", "breaking point")
  0.9-1.0 = Crisis-level stress, complete overwhelm ("everything falling apart")
  
  Key signals: pressure, deadlines, overwhelm, workload, exhaustion, burnout, tension,
  sleep issues, irritability, inability to relax, physical tension

CRITICAL RULES:
- If patient mentions physical symptoms (insomnia, headaches, fatigue), factor them into ALL scores
- Compound emotions: "stressed AND anxious" = both scores elevated
- Contradictions: "I'm fine but..." = look deeper, likely deflecting
- Severity modifiers matter: "a little" vs "very" vs "extremely" = different scores
- Context matters: work stress vs relationship stress vs health anxiety = different patterns
- NEVER default to 0.5 - commit to a precise assessment

Respond EXACTLY in this format:
ANXIETY: [score]
MOOD: [score]
STRESS: [score]
"""
        
        response = model.generate_content(metrics_prompt)
        text = response.text
        print(f"[GEMINI] ✓ Metrics response: {text[:200]}")
        
        # Parse metrics
        anxiety_match = re.search(r'ANXIETY:\s*(0?\.\d+|1\.0|0|1)', text)
        mood_match = re.search(r'MOOD:\s*(0?\.\d+|1\.0|0|1)', text)
        stress_match = re.search(r'STRESS:\s*(0?\.\d+|1\.0|0|1)', text)
        
        anxiety = float(anxiety_match.group(1)) if anxiety_match else 0.5
        mood = float(mood_match.group(1)) if mood_match else 0.5
        stress = float(stress_match.group(1)) if stress_match else 0.5
        
        anxiety = max(0.0, min(1.0, anxiety))
        mood = max(0.0, min(1.0, mood))
        stress = max(0.0, min(1.0, stress))
        
        print(f"[GEMINI] Anxiety: {anxiety:.2f}, Mood: {mood:.2f}, Stress: {stress:.2f}")
        
        # --- STEP 2: Get detailed text analysis ---
        analysis_prompt = f"""You are a compassionate and knowledgeable mental wellness counselor.
Based on this patient's message, provide a detailed but concise analysis.

Patient's words: "{user_input}"
Detected metrics - Anxiety: {anxiety:.0%}, Mood: {mood:.0%}, Stress: {stress:.0%}

Provide your analysis in this EXACT JSON format (no markdown, no code blocks, ONLY the JSON):
{{
  "summary": "A 2-3 sentence compassionate summary of their current emotional state. Be specific about what emotions you detected and why. Reference their actual words.",
  "primary_emotion": "The single dominant emotion (e.g., 'Anxious', 'Stressed', 'Sad', 'Overwhelmed', 'Hopeful', 'Content', 'Frustrated', 'Fearful', 'Calm')",
  "emotional_details": [
    "First specific emotional observation based on their words",
    "Second specific emotional observation",
    "Third specific emotional observation"
  ],
  "mental_state": "A 1-2 sentence clinical-style description of their mental state (e.g., 'Experiencing acute anxiety with rumination patterns. Stress response appears work-related with physical manifestations.')",
  "body_connection": "How their emotional state may be affecting them physically (e.g., 'Likely experiencing muscle tension, shallow breathing, and difficulty sleeping.')",
  "strength_noted": "One positive strength or resilience factor you notice (e.g., 'Seeking help shows self-awareness and proactive coping.')",
  "garden_description": "A poetic 1-2 sentence description of what their mental garden looks like right now (e.g., 'Your garden is under heavy clouds with wilting flowers, but strong roots remain beneath the surface.')"
}}
"""
        
        try:
            analysis_response = model.generate_content(analysis_prompt)
            analysis_text = analysis_response.text.strip()
            print(f"[GEMINI] ✓ Analysis response received")
            
            # Clean up response - remove markdown code blocks if present
            analysis_text = re.sub(r'^```json\s*', '', analysis_text)
            analysis_text = re.sub(r'^```\s*', '', analysis_text)
            analysis_text = re.sub(r'\s*```$', '', analysis_text)
            
            analysis = json.loads(analysis_text)
        except Exception as e:
            print(f"[GEMINI] Analysis parsing failed: {e}, using fallback")
            analysis = _generate_fallback_analysis(anxiety, mood, stress, user_input)
        
        return {
            "anxiety": round(anxiety, 2),
            "mood": round(mood, 2),
            "stress": round(stress, 2),
            "analysis": analysis
        }
    
    except Exception as e:
        print(f"[ERROR] Gemini analysis failed: {e}")
        return demo_analysis(user_input)


def _generate_fallback_analysis(anxiety, mood, stress, user_input):
    """Generate analysis text when Gemini analysis call fails"""
    # Determine primary emotion
    if anxiety > 0.6:
        primary = "Anxious"
    elif stress > 0.6:
        primary = "Stressed"
    elif mood < 0.3:
        primary = "Sad"
    elif mood < 0.5:
        primary = "Low"
    elif mood > 0.7:
        primary = "Content"
    else:
        primary = "Mixed"
    
    # Build contextual summary
    parts = []
    if anxiety > 0.5:
        parts.append(f"elevated anxiety ({anxiety:.0%})")
    if stress > 0.5:
        parts.append(f"significant stress ({stress:.0%})")
    if mood < 0.5:
        parts.append(f"lowered mood ({mood:.0%})")
    if mood > 0.6:
        parts.append(f"positive mood ({mood:.0%})")
    
    summary = f"Based on your description, you are experiencing {', '.join(parts) if parts else 'a mixed emotional state'}. "
    summary += "Your words reveal important feelings that deserve attention and care."
    
    details = []
    if anxiety > 0.5:
        details.append("Noticeable worry and unease detected in your description")
    if stress > 0.5:
        details.append("Signs of pressure and feeling overwhelmed are present")
    if mood < 0.5:
        details.append("Your mood appears lower than baseline, which affects overall wellbeing")
    if mood > 0.6:
        details.append("Positive emotional energy is coming through in your words")
    if len(details) == 0:
        details = ["Moderate emotional intensity detected", "Mixed feelings present", "Some underlying tension noted"]
    
    # Garden description
    wellbeing = (1 - anxiety + mood + (1 - stress)) / 3
    if wellbeing > 0.7:
        garden = "Your mental garden is bright and blooming, with clear skies and vibrant flowers swaying gently."
    elif wellbeing > 0.5:
        garden = "Your garden shows patches of sunlight breaking through clouds, with flowers beginning to open."
    elif wellbeing > 0.3:
        garden = "Your garden is under overcast skies with flowers bending under the weight, but green growth persists."
    else:
        garden = "Your garden is weathering a storm - heavy clouds and rain, but the roots remain strong beneath."
    
    # Body connection
    if anxiety > 0.6 or stress > 0.6:
        body = "You may be experiencing muscle tension, shallow breathing, restlessness, or difficulty concentrating."
    elif mood < 0.4:
        body = "Low mood can manifest as fatigue, low energy, changes in appetite, and heaviness in the body."
    else:
        body = "Your body is likely in a relatively balanced state, though regular check-ins help maintain awareness."
    
    return {
        "summary": summary,
        "primary_emotion": primary,
        "emotional_details": details[:3],
        "mental_state": f"Currently presenting with {primary.lower()} features. Overall wellbeing assessment: {'needs attention' if wellbeing < 0.4 else 'moderate' if wellbeing < 0.6 else 'fair' if wellbeing < 0.75 else 'good'}.",
        "body_connection": body,
        "strength_noted": "Seeking support and self-reflection shows admirable self-awareness and emotional intelligence.",
        "garden_description": garden
    }


def demo_analysis(user_input):
    """Fallback keyword-based analysis with text descriptions"""
    text = user_input.lower()
    
    # Calculate anxiety with weighted keywords
    anxiety_keywords = {
        'anxious': 0.25, 'worried': 0.2, 'nervous': 0.2, 'panic': 0.35,
        'fear': 0.25, 'scared': 0.25, 'terrified': 0.4, 'dread': 0.3,
        'restless': 0.15, 'overthinking': 0.2, 'racing thoughts': 0.3,
        'can\'t stop thinking': 0.25, 'uneasy': 0.15, 'tense': 0.15
    }
    anxiety = min(1.0, sum(w for kw, w in anxiety_keywords.items() if kw in text))
    
    # Calculate mood with weighted keywords
    positive_keywords = {
        'happy': 0.25, 'good': 0.15, 'great': 0.25, 'excited': 0.25,
        'joy': 0.3, 'calm': 0.15, 'grateful': 0.2, 'wonderful': 0.3,
        'amazing': 0.3, 'content': 0.2, 'peaceful': 0.2, 'love': 0.15,
        'hopeful': 0.15, 'positive': 0.15
    }
    negative_keywords = {
        'sad': 0.2, 'depressed': 0.35, 'down': 0.15, 'unhappy': 0.2,
        'bad': 0.15, 'empty': 0.25, 'hopeless': 0.35, 'crying': 0.25,
        'miserable': 0.3, 'lonely': 0.2, 'lost': 0.15, 'worthless': 0.35,
        'numb': 0.25, 'tired of': 0.2
    }
    
    pos_score = sum(w for kw, w in positive_keywords.items() if kw in text)
    neg_score = sum(w for kw, w in negative_keywords.items() if kw in text)
    
    if pos_score > 0 and neg_score == 0:
        mood = min(1.0, 0.6 + pos_score)
    elif neg_score > 0 and pos_score == 0:
        mood = max(0.0, 0.4 - neg_score)
    elif pos_score > neg_score:
        mood = min(1.0, 0.5 + (pos_score - neg_score))
    elif neg_score > pos_score:
        mood = max(0.0, 0.5 - (neg_score - pos_score))
    else:
        mood = 0.5
    
    mood = max(0.0, min(1.0, mood))
    
    # Calculate stress with weighted keywords
    stress_keywords = {
        'stress': 0.25, 'stressed': 0.25, 'overwhelmed': 0.35, 'pressure': 0.2,
        'deadline': 0.2, 'busy': 0.15, 'too much': 0.25, 'burnout': 0.35,
        'exhausted': 0.3, 'can\'t cope': 0.35, 'overloaded': 0.3,
        'breaking point': 0.4, 'can\'t handle': 0.3, 'drowning': 0.3
    }
    stress = min(1.0, sum(w for kw, w in stress_keywords.items() if kw in text))
    
    # If no keywords found, use moderate values
    if anxiety == 0 and stress == 0 and abs(mood - 0.5) < 0.01:
        anxiety = 0.4
        mood = 0.5
        stress = 0.4
    
    print(f"[DEMO MODE] Anxiety: {anxiety:.2f}, Mood: {mood:.2f}, Stress: {stress:.2f}")
    
    # Generate analysis text
    analysis = _generate_fallback_analysis(anxiety, mood, stress, user_input)
    
    return {
        "anxiety": round(anxiety, 2),
        "mood": round(mood, 2),
        "stress": round(stress, 2),
        "analysis": analysis
    }
