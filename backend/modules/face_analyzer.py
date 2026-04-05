"""Face emotion analysis module for MindViz.

Primary analysis path  : Gemini Vision API (uses existing API key)
Secondary fallback     : DeepFace library (if installed)
Graceful degradation   : returns unavailable state when neither works

Usage
-----
from modules.face_analyzer import analyze_face_emotion

result = analyze_face_emotion(image_base64)
# result keys: top_emotion, scores, face_detected, wellness_contribution, source
"""

import base64
import json
import re
import os
import io
import sys

# ── Shared emotion categories ──────────────────────────────────────────────────
EMOTION_LABELS = ["happy", "neutral", "surprise", "sad", "angry", "fear", "disgust"]

# How much each facial emotion contributes to wellness (0 = very low, 1 = very high)
EMOTION_WELLNESS_MAP = {
    "happy": 0.90,
    "neutral": 0.60,
    "surprise": 0.55,
    "sad": 0.30,
    "fear": 0.20,
    "angry": 0.20,
    "disgust": 0.15,
}


def _default_scores():
    return {label: round(1.0 / len(EMOTION_LABELS), 3) for label in EMOTION_LABELS}


def _unavailable_result(reason=""):
    return {
        "top_emotion": "unknown",
        "scores": _default_scores(),
        "face_detected": False,
        "wellness_contribution": 0.5,
        "source": "unavailable",
        "note": reason or "Face analysis not available",
    }


def _wellness_from_scores(scores: dict) -> float:
    """Compute a 0-1 wellness score from emotion probability scores."""
    total = 0.0
    for emotion, prob in scores.items():
        total += prob * EMOTION_WELLNESS_MAP.get(emotion, 0.5)
    return round(min(1.0, max(0.0, total)), 3)


# ── Gemini Vision path ─────────────────────────────────────────────────────────

def _analyze_with_gemini_vision(image_base64: str) -> dict:
    """Use Gemini Vision API to extract facial emotion probabilities."""
    try:
        import google.generativeai as genai
        from dotenv import load_dotenv

        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY", "")
        if not api_key or api_key == "your_api_key_here":
            return None  # Signal caller to try next method

        genai.configure(api_key=api_key)

        # Decode image bytes
        img_bytes = base64.b64decode(image_base64)

        # Build image part for Gemini Vision
        image_part = {"mime_type": "image/jpeg", "data": img_bytes}

        prompt = (
            "You are an expert in facial expression analysis.\n"
            "Look at this face image and estimate the probability (0.0 to 1.0) for each emotion.\n"
            "The probabilities must sum to exactly 1.0.\n\n"
            "Return ONLY valid JSON in this exact format (no markdown, no explanation):\n"
            '{"happy": 0.xx, "neutral": 0.xx, "surprise": 0.xx, '
            '"sad": 0.xx, "angry": 0.xx, "fear": 0.xx, "disgust": 0.xx}\n\n'
            "If no human face is visible, return:\n"
            '{"no_face": true}'
        )

        # Try gemini-1.5-flash first (supports vision), then gemini-pro-vision
        vision_model = None
        for model_name in ("gemini-1.5-flash", "gemini-pro-vision"):
            try:
                vision_model = genai.GenerativeModel(model_name)
                response = vision_model.generate_content([prompt, image_part])
                raw = response.text.strip()
                break
            except Exception:
                vision_model = None
                continue

        if vision_model is None:
            return None

        # Strip markdown fences if present
        raw = re.sub(r"^```[a-z]*\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)

        parsed = json.loads(raw)

        if parsed.get("no_face"):
            return {
                "top_emotion": "unknown",
                "scores": _default_scores(),
                "face_detected": False,
                "wellness_contribution": 0.5,
                "source": "gemini",
                "note": "No face detected in image",
            }

        # Normalize scores to sum to 1.0
        total = sum(parsed.get(e, 0) for e in EMOTION_LABELS)
        if total <= 0:
            total = 1.0
        scores = {e: round(parsed.get(e, 0) / total, 3) for e in EMOTION_LABELS}
        top_emotion = max(scores, key=scores.get)

        return {
            "top_emotion": top_emotion,
            "scores": scores,
            "face_detected": True,
            "wellness_contribution": _wellness_from_scores(scores),
            "source": "gemini",
        }

    except json.JSONDecodeError as exc:
        print(f"[FACE] Gemini JSON parse error: {exc}")
        return None
    except Exception as exc:
        print(f"[FACE] Gemini Vision error: {exc}")
        return None


# ── DeepFace fallback path ─────────────────────────────────────────────────────

def _analyze_with_deepface(image_base64: str) -> dict:
    """Use DeepFace library to extract facial emotion probabilities."""
    try:
        import numpy as np
        import cv2
        from deepface import DeepFace

        img_bytes = base64.b64decode(image_base64)
        img_array = np.frombuffer(img_bytes, dtype=np.uint8)
        frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

        if frame is None:
            return None

        results = DeepFace.analyze(
            frame,
            actions=["emotion"],
            enforce_detection=False,
            silent=True,
        )

        # DeepFace may return a list or a single dict depending on version
        if isinstance(results, list):
            results = results[0]

        raw_emotions = results.get("emotion", {})
        total = sum(raw_emotions.values()) or 1.0

        # Map DeepFace labels to our canonical set
        label_map = {
            "happy": "happy",
            "neutral": "neutral",
            "surprise": "surprise",
            "surprised": "surprise",
            "sad": "sad",
            "angry": "angry",
            "anger": "angry",
            "fear": "fear",
            "disgust": "disgust",
        }
        scores = {e: 0.0 for e in EMOTION_LABELS}
        for df_label, value in raw_emotions.items():
            canonical = label_map.get(df_label.lower())
            if canonical:
                scores[canonical] += value / total

        # Renormalize after mapping
        total2 = sum(scores.values()) or 1.0
        scores = {e: round(v / total2, 3) for e, v in scores.items()}

        face_detected = results.get("dominant_emotion") not in (None, "")
        top_emotion = max(scores, key=scores.get) if face_detected else "unknown"

        return {
            "top_emotion": top_emotion,
            "scores": scores,
            "face_detected": face_detected,
            "wellness_contribution": _wellness_from_scores(scores),
            "source": "deepface",
        }

    except ImportError:
        return None  # DeepFace not installed
    except Exception as exc:
        print(f"[FACE] DeepFace error: {exc}")
        return None


# ── Public API ─────────────────────────────────────────────────────────────────

def analyze_face_emotion(image_base64: str) -> dict:
    """Analyze facial emotion from a base64-encoded JPEG image.

    Returns a dict with the following keys:
      top_emotion          : str  — dominant emotion label
      scores               : dict — per-emotion probabilities (sum ≈ 1.0)
      face_detected        : bool — whether a face was found
      wellness_contribution: float — 0-1 wellness indicator from face alone
      source               : str  — "gemini" | "deepface" | "unavailable"
      note (optional)      : str  — human-readable status message
    """
    if not image_base64:
        return _unavailable_result("No image data provided")

    print("[FACE] Starting face emotion analysis...")

    # 1. Try Gemini Vision
    result = _analyze_with_gemini_vision(image_base64)
    if result is not None:
        print(f"[FACE] Gemini Vision result — top: {result['top_emotion']}, "
              f"face_detected: {result['face_detected']}, "
              f"wellness: {result['wellness_contribution']}")
        return result

    # 2. Try DeepFace
    result = _analyze_with_deepface(image_base64)
    if result is not None:
        print(f"[FACE] DeepFace result — top: {result['top_emotion']}, "
              f"face_detected: {result['face_detected']}, "
              f"wellness: {result['wellness_contribution']}")
        return result

    # 3. Graceful degradation
    print("[FACE] Face analysis unavailable — using text-only mode")
    return _unavailable_result(
        "Face analysis unavailable (install DeepFace or configure Gemini API key)"
    )


def fuse_text_and_face(text_metrics: dict, face_result: dict,
                       text_weight: float = 0.7,
                       face_weight: float = 0.3) -> dict:
    """Combine text-based metrics with face emotion result.

    If the face was not detected or analysis was unavailable the function
    returns the original text metrics unchanged (text-only fallback).

    Parameters
    ----------
    text_metrics  : dict with keys anxiety, mood, stress (0-1 floats)
    face_result   : return value of analyze_face_emotion()
    text_weight   : weight for text-based scores (default 0.7)
    face_weight   : weight for face-based scores (default 0.3)

    Returns
    -------
    A copy of text_metrics with adjusted scores and added face_analysis key.
    """
    import copy
    fused = copy.deepcopy(text_metrics)

    if not face_result.get("face_detected", False):
        fused["face_analysis"] = face_result
        fused["fusion_used"] = False
        return fused

    wellness = face_result.get("wellness_contribution", 0.5)

    # Translate face wellness into anxiety/mood/stress contributions:
    #   high wellness  → low anxiety, high mood, low stress
    #   low wellness   → high anxiety, low mood, high stress
    face_anxiety = max(0.0, min(1.0, 1.0 - wellness))
    face_mood = wellness
    face_stress = max(0.0, min(1.0, 1.0 - wellness))

    fused["anxiety"] = round(
        text_weight * text_metrics.get("anxiety", 0.5) + face_weight * face_anxiety, 2
    )
    fused["mood"] = round(
        text_weight * text_metrics.get("mood", 0.5) + face_weight * face_mood, 2
    )
    fused["stress"] = round(
        text_weight * text_metrics.get("stress", 0.5) + face_weight * face_stress, 2
    )

    # Keep original analysis text, just add face info
    fused["face_analysis"] = face_result
    fused["fusion_used"] = True

    print(
        f"[FACE] Fused metrics — anxiety: {fused['anxiety']}, "
        f"mood: {fused['mood']}, stress: {fused['stress']} "
        f"(text×{text_weight} + face×{face_weight})"
    )
    return fused
