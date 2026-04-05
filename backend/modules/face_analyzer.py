"""
Face emotion analysis using the Gemini Vision API.

This module is entirely optional — when called it uses the same free Gemini key
already configured in gemini_analyzer.py.  All failures are swallowed and an
explicit `enabled=False` result is returned so the rest of the pipeline can
continue with text-only data.

DISCLAIMER: Results are wellness indicators only and NOT medical diagnoses.
"""

import base64
import io
import json
import os
import re

from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
_VISION_MODEL_NAME = "gemini-1.5-flash"   # fallback: "gemini-pro-vision"

# Raw emotion → wellness dimension mapping
# Emotion weights chosen to map to anxiety (0-1), mood (0-1), stress (0-1)
_EMOTION_TO_DIMENSIONS = {
    "happy":    {"anxiety": 0.05, "mood": 0.85, "stress": 0.05},
    "neutral":  {"anxiety": 0.25, "mood": 0.55, "stress": 0.25},
    "surprise": {"anxiety": 0.35, "mood": 0.60, "stress": 0.30},
    "sad":      {"anxiety": 0.45, "mood": 0.20, "stress": 0.45},
    "fear":     {"anxiety": 0.80, "mood": 0.20, "stress": 0.65},
    "angry":    {"anxiety": 0.55, "mood": 0.25, "stress": 0.75},
    "disgust":  {"anxiety": 0.45, "mood": 0.25, "stress": 0.55},
}

_DISABLED = {"enabled": False}


def _resize_image_bytes(image_bytes: bytes, max_px: int = 512) -> bytes:
    """Resize image bytes (JPEG/PNG) to at most *max_px* on each side."""
    try:
        from PIL import Image  # type: ignore

        img = Image.open(io.BytesIO(image_bytes))
        img.thumbnail((max_px, max_px))
        if img.mode not in ("RGB", "L"):
            img = img.convert("RGB")
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=85)
        return buf.getvalue()
    except Exception:
        return image_bytes  # return original if resizing fails


def _build_vision_model():
    """Lazy-import and configure Gemini; return model or None."""
    if not GEMINI_API_KEY or GEMINI_API_KEY == "your_api_key_here":
        print("[FACE] No valid Gemini API key — face analysis disabled.")
        return None
    try:
        import google.generativeai as genai  # type: ignore

        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel(_VISION_MODEL_NAME)
        return model
    except Exception as exc:
        print(f"[FACE] Could not load Gemini vision model: {exc}")
        return None


def _emotion_probs_to_dimensions(raw: dict) -> dict:
    """
    Convert raw emotion probabilities (happy, sad, …) to
    wellness dimensions (anxiety, mood, stress) via a weighted blend.
    """
    anxiety = mood = stress = 0.0
    total = sum(raw.values()) or 1.0  # avoid /0

    for emotion, prob in raw.items():
        dims = _EMOTION_TO_DIMENSIONS.get(emotion.lower(), _EMOTION_TO_DIMENSIONS["neutral"])
        w = prob / total
        anxiety += dims["anxiety"] * w
        mood    += dims["mood"]    * w
        stress  += dims["stress"]  * w

    return {
        "anxiety": round(min(1.0, max(0.0, anxiety)), 2),
        "mood":    round(min(1.0, max(0.0, mood)),    2),
        "stress":  round(min(1.0, max(0.0, stress)),  2),
    }


def analyze_face_emotion(image_b64: str) -> dict:
    """
    Analyze facial emotion from a base64-encoded JPEG/PNG image.

    Returns a dict:
        {
          "enabled": True,
          "anxiety": float,   # 0–1
          "mood":    float,   # 0–1
          "stress":  float,   # 0–1
          "primary_expression": str,
          "raw_emotions": {emotion: probability, ...}
        }

    On any failure returns {"enabled": False}.
    """
    if not image_b64:
        return _DISABLED

    model = _build_vision_model()
    if model is None:
        return _DISABLED

    try:
        # Decode and optionally resize
        image_bytes = base64.b64decode(image_b64)
        image_bytes = _resize_image_bytes(image_bytes)

        prompt = (
            "You are a facial expression recognition system. "
            "Look only at the visible facial expression in this image. "
            "Do NOT attempt medical or psychological diagnosis. "
            "Return ONLY valid JSON — no prose, no markdown — with this exact schema:\n"
            '{"happy": 0.0, "sad": 0.0, "angry": 0.0, "fear": 0.0, '
            '"neutral": 0.0, "surprise": 0.0, "disgust": 0.0}\n'
            "Each value is a probability in [0.0, 1.0] and all values must sum to 1.0. "
            "If no face is visible return neutral=1.0 and all others 0.0."
        )

        # Build image part for the API
        try:
            from PIL import Image as PILImage  # type: ignore

            pil_img = PILImage.open(io.BytesIO(image_bytes))
            contents = [prompt, pil_img]
        except Exception:
            # Fallback: pass raw bytes as inline_data blob dict
            import google.generativeai as genai  # type: ignore

            blob = {"mime_type": "image/jpeg", "data": image_bytes}
            contents = [prompt, blob]

        response = model.generate_content(contents)
        text = response.text.strip()
        print(f"[FACE] Gemini vision response: {text[:200]}")

        # Strip markdown code fences if present
        text = re.sub(r"^```[a-z]*\s*", "", text)
        text = re.sub(r"\s*```$", "", text)

        raw_emotions = json.loads(text)

        # Validate keys; fill missing with 0
        valid_keys = {"happy", "sad", "angry", "fear", "neutral", "surprise", "disgust"}
        raw_emotions = {k: float(v) for k, v in raw_emotions.items() if k in valid_keys}
        for k in valid_keys:
            raw_emotions.setdefault(k, 0.0)

        primary = max(raw_emotions, key=raw_emotions.get)
        dims = _emotion_probs_to_dimensions(raw_emotions)

        print(
            f"[FACE] Primary={primary}  "
            f"anxiety={dims['anxiety']}  mood={dims['mood']}  stress={dims['stress']}"
        )

        return {
            "enabled": True,
            "primary_expression": primary,
            "raw_emotions": {k: round(v, 3) for k, v in raw_emotions.items()},
            **dims,
        }

    except Exception as exc:
        print(f"[FACE] Face analysis failed: {exc}")
        return _DISABLED
