import base64
import json
import os
import re

import google.generativeai as genai
from dotenv import load_dotenv


# Load environment variables
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

TEXT_MODEL_CANDIDATES = [
    "gemini-2.5-flash",
    "gemini-1.5-flash",
    "gemini-pro",
]

VISION_MODEL_CANDIDATES = [
    "gemini-2.5-flash",
    "gemini-1.5-flash",
    "gemini-pro-vision",
]

if not GEMINI_API_KEY or GEMINI_API_KEY == "your_api_key_here":
    print("[WARNING] No valid Gemini API key found! Using DEMO MODE.")
    print("[WARNING] Get your free key at: https://aistudio.google.com/app/apikey")
    USE_DEMO_MODE = True
else:
    genai.configure(api_key=GEMINI_API_KEY)
    USE_DEMO_MODE = False
    print("[INFO] ✓ Gemini API configured successfully!")
    print(f"[INFO] Using API key: {GEMINI_API_KEY[:20]}...")


def _clamp01(value, default=0.5):
    try:
        return max(0.0, min(1.0, float(value)))
    except Exception:
        return default


def _default_face_signal(reason):
    return {
        "used": False,
        "emotion": "Not analyzed",
        "confidence": 0.0,
        "summary": reason,
        "fusion_weight": 0.0,
    }


def _generate_with_candidates(parts, candidates):
    last_error = None
    for model_name in candidates:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(parts)
            text = getattr(response, "text", "") or ""
            if text.strip():
                return text, model_name
        except Exception as exc:
            last_error = exc

    raise RuntimeError(f"All candidate models failed: {last_error}")


def _extract_json_object(raw_text):
    text = raw_text.strip()
    text = re.sub(r"^```json\\s*", "", text)
    text = re.sub(r"^```\\s*", "", text)
    text = re.sub(r"\\s*```$", "", text)

    try:
        return json.loads(text)
    except Exception:
        pass

    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        raise ValueError("No JSON object found in model response")

    return json.loads(match.group(0))


def _decode_image_part(face_image):
    if not face_image:
        return None

    data = face_image
    mime = "image/jpeg"

    if face_image.startswith("data:"):
        # Expected format: data:image/jpeg;base64,<payload>
        head, _, payload = face_image.partition(",")
        data = payload
        mime_match = re.search(r"data:([^;]+);base64", head)
        if mime_match:
            mime = mime_match.group(1)

    raw = base64.b64decode(data)
    return {"mime_type": mime, "data": raw}


def _analyze_face_with_gemini(face_image):
    if USE_DEMO_MODE:
        return _default_face_signal("Face analysis skipped in demo mode.")

    if not face_image:
        return _default_face_signal("No face image provided.")

    try:
        image_part = _decode_image_part(face_image)
    except Exception:
        return _default_face_signal("Face image could not be decoded.")

    prompt = (
        "You are analyzing a single human face image for visible emotional cues only. "
        "Do NOT make medical diagnoses. Return strict JSON only with this schema:\n"
        "{\n"
        '  "emotion": "short label",\n'
        '  "confidence": 0.0,\n'
        '  "anxiety_hint": 0.0,\n'
        '  "mood_hint": 0.0,\n'
        '  "stress_hint": 0.0,\n'
        '  "summary": "one concise sentence"\n'
        "}\n"
        "Scale rules: anxiety_hint/mood_hint/stress_hint are each 0..1. "
        "If face is not clearly visible, lower confidence and use neutral hints near 0.5."
    )

    try:
        raw_text, model_name = _generate_with_candidates(
            [prompt, image_part],
            VISION_MODEL_CANDIDATES,
        )
        parsed = _extract_json_object(raw_text)

        signal = {
            "used": True,
            "emotion": str(parsed.get("emotion", "Neutral")).strip().title(),
            "confidence": _clamp01(parsed.get("confidence", 0.0), default=0.0),
            "anxiety_hint": _clamp01(parsed.get("anxiety_hint", 0.5)),
            "mood_hint": _clamp01(parsed.get("mood_hint", 0.5)),
            "stress_hint": _clamp01(parsed.get("stress_hint", 0.5)),
            "summary": str(parsed.get("summary", "Visible expression analyzed from image.")).strip(),
            "fusion_weight": 0.0,
            "model": model_name,
        }

        return signal
    except Exception as exc:
        return {
            **_default_face_signal("Face analysis failed; text-only analysis used."),
            "error": str(exc),
        }


def _blend_text_with_face(anxiety, mood, stress, face_signal):
    if not face_signal or not face_signal.get("used"):
        return anxiety, mood, stress, 0.0

    confidence = _clamp01(face_signal.get("confidence", 0.0), default=0.0)
    # Keep text as primary source and use face cues as a light correction.
    fusion_weight = min(0.30, 0.08 + (0.22 * confidence))

    a_hint = _clamp01(face_signal.get("anxiety_hint", anxiety), default=anxiety)
    m_hint = _clamp01(face_signal.get("mood_hint", mood), default=mood)
    s_hint = _clamp01(face_signal.get("stress_hint", stress), default=stress)

    anxiety = _clamp01((1 - fusion_weight) * anxiety + fusion_weight * a_hint)
    mood = _clamp01((1 - fusion_weight) * mood + fusion_weight * m_hint)
    stress = _clamp01((1 - fusion_weight) * stress + fusion_weight * s_hint)

    return anxiety, mood, stress, fusion_weight


def analyze_with_gemini(user_input, face_image=None):
    """Analyze user input with Gemini and optionally fuse in face-image cues."""

    if USE_DEMO_MODE:
        result = demo_analysis(user_input)
        result["face_signal"] = _default_face_signal("Text-only demo mode active.")
        return result

    print("[GEMINI] Using REAL Gemini API...")

    try:
        # --- STEP 1: Text metrics ---
        metrics_prompt = f"""You are a board-certified clinical psychologist with 20 years of experience in emotional assessment.
Analyze this patient's message with extreme precision and clinical accuracy.

Patient's exact words: \"{user_input}\"

Score these three dimensions. Base scores STRICTLY on what the patient said.

ANXIETY (0.0 to 1.0)
MOOD (0.0 to 1.0)
STRESS (0.0 to 1.0)

Respond EXACTLY in this format:
ANXIETY: [score]
MOOD: [score]
STRESS: [score]
"""

        metrics_text, metrics_model = _generate_with_candidates(
            metrics_prompt,
            TEXT_MODEL_CANDIDATES,
        )
        print(f"[GEMINI] ✓ Metrics response model: {metrics_model}")

        anxiety_match = re.search(r"ANXIETY:\s*(0?\.\d+|1\.0|0|1)", metrics_text)
        mood_match = re.search(r"MOOD:\s*(0?\.\d+|1\.0|0|1)", metrics_text)
        stress_match = re.search(r"STRESS:\s*(0?\.\d+|1\.0|0|1)", metrics_text)

        anxiety = _clamp01(anxiety_match.group(1) if anxiety_match else 0.5)
        mood = _clamp01(mood_match.group(1) if mood_match else 0.5)
        stress = _clamp01(stress_match.group(1) if stress_match else 0.5)

        print(f"[GEMINI] Text metrics → Anxiety: {anxiety:.2f}, Mood: {mood:.2f}, Stress: {stress:.2f}")

        # --- STEP 2: Optional face signal + fusion ---
        face_signal = _analyze_face_with_gemini(face_image)
        anxiety, mood, stress, fusion_weight = _blend_text_with_face(
            anxiety,
            mood,
            stress,
            face_signal,
        )
        face_signal["fusion_weight"] = round(fusion_weight, 3)

        if face_signal.get("used"):
            print(
                "[GEMINI] Face fusion → "
                f"emotion={face_signal.get('emotion')} conf={face_signal.get('confidence', 0):.2f} "
                f"w={fusion_weight:.2f}"
            )

        # --- STEP 3: Detailed narrative analysis ---
        analysis_prompt = f"""You are a compassionate and knowledgeable mental wellness counselor.
Based on this patient's message, provide a detailed but concise analysis.

Patient's words: \"{user_input}\"
Detected metrics - Anxiety: {anxiety:.0%}, Mood: {mood:.0%}, Stress: {stress:.0%}

Return ONLY valid JSON with this schema:
{{
  "summary": "2-3 sentence compassionate summary",
  "primary_emotion": "single dominant emotion",
  "emotional_details": ["detail 1", "detail 2", "detail 3"],
  "mental_state": "1-2 sentence mental-state description",
  "body_connection": "short physical connection note",
  "strength_noted": "one resilience strength",
  "garden_description": "1-2 sentence poetic garden reflection"
}}
"""

        try:
            analysis_text, analysis_model = _generate_with_candidates(
                analysis_prompt,
                TEXT_MODEL_CANDIDATES,
            )
            print(f"[GEMINI] ✓ Analysis response model: {analysis_model}")
            analysis = _extract_json_object(analysis_text)
        except Exception as exc:
            print(f"[GEMINI] Analysis parsing failed: {exc}, using fallback")
            analysis = _generate_fallback_analysis(anxiety, mood, stress, user_input)

        return {
            "anxiety": round(anxiety, 2),
            "mood": round(mood, 2),
            "stress": round(stress, 2),
            "analysis": analysis,
            "face_signal": face_signal,
        }

    except Exception as exc:
        print(f"[ERROR] Gemini analysis failed: {exc}")
        result = demo_analysis(user_input)
        result["face_signal"] = _default_face_signal("Gemini failed; fallback text analysis used.")
        return result


def _generate_fallback_analysis(anxiety, mood, stress, user_input):
    """Generate analysis text when Gemini analysis call fails."""
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

    parts = []
    if anxiety > 0.5:
        parts.append(f"elevated anxiety ({anxiety:.0%})")
    if stress > 0.5:
        parts.append(f"significant stress ({stress:.0%})")
    if mood < 0.5:
        parts.append(f"lowered mood ({mood:.0%})")
    if mood > 0.6:
        parts.append(f"positive mood ({mood:.0%})")

    summary = (
        f"Based on your description, you are experiencing {', '.join(parts) if parts else 'a mixed emotional state'}. "
        "Your words reveal important feelings that deserve attention and care."
    )

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
        details = [
            "Moderate emotional intensity detected",
            "Mixed feelings present",
            "Some underlying tension noted",
        ]

    wellbeing = (1 - anxiety + mood + (1 - stress)) / 3
    if wellbeing > 0.7:
        garden = "Your mental garden is bright and blooming, with clear skies and vibrant flowers swaying gently."
    elif wellbeing > 0.5:
        garden = "Your garden shows patches of sunlight breaking through clouds, with flowers beginning to open."
    elif wellbeing > 0.3:
        garden = "Your garden is under overcast skies with flowers bending under the weight, but green growth persists."
    else:
        garden = "Your garden is weathering a storm - heavy clouds and rain, but the roots remain strong beneath."

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
        "mental_state": (
            f"Currently presenting with {primary.lower()} features. Overall wellbeing assessment: "
            f"{'needs attention' if wellbeing < 0.4 else 'moderate' if wellbeing < 0.6 else 'fair' if wellbeing < 0.75 else 'good'}."
        ),
        "body_connection": body,
        "strength_noted": "Seeking support and self-reflection shows admirable self-awareness and emotional intelligence.",
        "garden_description": garden,
    }


def demo_analysis(user_input):
    """Fallback keyword-based analysis with text descriptions."""
    text = user_input.lower()

    anxiety_keywords = {
        "anxious": 0.25,
        "worried": 0.2,
        "nervous": 0.2,
        "panic": 0.35,
        "fear": 0.25,
        "scared": 0.25,
        "terrified": 0.4,
        "dread": 0.3,
        "restless": 0.15,
        "overthinking": 0.2,
        "racing thoughts": 0.3,
        "can't stop thinking": 0.25,
        "uneasy": 0.15,
        "tense": 0.15,
    }
    anxiety = min(1.0, sum(weight for kw, weight in anxiety_keywords.items() if kw in text))

    positive_keywords = {
        "happy": 0.25,
        "good": 0.15,
        "great": 0.25,
        "excited": 0.25,
        "joy": 0.3,
        "calm": 0.15,
        "grateful": 0.2,
        "wonderful": 0.3,
        "amazing": 0.3,
        "content": 0.2,
        "peaceful": 0.2,
        "love": 0.15,
        "hopeful": 0.15,
        "positive": 0.15,
    }
    negative_keywords = {
        "sad": 0.2,
        "depressed": 0.35,
        "down": 0.15,
        "unhappy": 0.2,
        "bad": 0.15,
        "empty": 0.25,
        "hopeless": 0.35,
        "crying": 0.25,
        "miserable": 0.3,
        "lonely": 0.2,
        "lost": 0.15,
        "worthless": 0.35,
        "numb": 0.25,
        "tired of": 0.2,
    }

    pos_score = sum(weight for kw, weight in positive_keywords.items() if kw in text)
    neg_score = sum(weight for kw, weight in negative_keywords.items() if kw in text)

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

    stress_keywords = {
        "stress": 0.25,
        "stressed": 0.25,
        "overwhelmed": 0.35,
        "pressure": 0.2,
        "deadline": 0.2,
        "busy": 0.15,
        "too much": 0.25,
        "burnout": 0.35,
        "exhausted": 0.3,
        "can't cope": 0.35,
        "overloaded": 0.3,
        "breaking point": 0.4,
        "can't handle": 0.3,
        "drowning": 0.3,
    }
    stress = min(1.0, sum(weight for kw, weight in stress_keywords.items() if kw in text))

    if anxiety == 0 and stress == 0 and abs(mood - 0.5) < 0.01:
        anxiety = 0.4
        mood = 0.5
        stress = 0.4

    print(f"[DEMO MODE] Anxiety: {anxiety:.2f}, Mood: {mood:.2f}, Stress: {stress:.2f}")

    analysis = _generate_fallback_analysis(anxiety, mood, stress, user_input)

    return {
        "anxiety": round(anxiety, 2),
        "mood": round(mood, 2),
        "stress": round(stress, 2),
        "analysis": analysis,
    }
