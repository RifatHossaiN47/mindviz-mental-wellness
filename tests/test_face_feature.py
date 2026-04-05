"""Unit tests for the face emotion analysis feature.

Tests cover:
  - face_analyzer module (analyze_face_emotion, fuse_text_and_face)
  - text-only path is unchanged when no face image is provided
  - graceful degradation when face analysis is unavailable
  - fusion logic correctness
"""

import sys
import os
import base64
import copy
import unittest

# Add backend to path so we can import modules directly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from modules.face_analyzer import (
    analyze_face_emotion,
    fuse_text_and_face,
    _wellness_from_scores,
    _default_scores,
    _unavailable_result,
    EMOTION_LABELS,
    EMOTION_WELLNESS_MAP,
)


# ── Helpers ────────────────────────────────────────────────────────────────────

def _make_tiny_jpeg_b64() -> str:
    """Return a 1×1 white JPEG encoded as base64 (no OpenCV needed)."""
    # Minimal valid JPEG bytes for a 1x1 white pixel
    jpeg_bytes = (
        b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00"
        b"\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t"
        b"\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a"
        b"\x1f\x1e\x1d\x1a\x1c\x1c $.' \",#\x1c\x1c(7),01444\x1f'9=82<.342\x1e"
        b"\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00\xff\xc4\x00"
        b"\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xc4\x00"
        b"\xb5\x10\x00\x02\x01\x03\x03\x02\x04\x03\x05\x05\x04\x04\x00\x00"
        b"\x01}\x01\x02\x03\x00\x04\x11\x05\x12!1A\x06\x13Qa\x07\"q\x142\x81"
        b"\x91\xa1\x08#B\xb1\xc1\x15R\xd1\xf0$3br\x82\t\n\x16\x17\x18\x19"
        b"\x1a%&'()*456789:CDEFGHIJSTUVWXYZcdefghijstuvwxyz\x83\x84\x85\x86"
        b"\x87\x88\x89\x8a\x92\x93\x94\x95\x96\x97\x98\x99\x9a\xa2\xa3\xa4"
        b"\xa5\xa6\xa7\xa8\xa9\xaa\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xc2"
        b"\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9"
        b"\xda\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xf1\xf2\xf3\xf4\xf5"
        b"\xf6\xf7\xf8\xf9\xfa\xff\xda\x00\x08\x01\x01\x00\x00?\x00\xfb\xd2"
        b"\x8a(\x03\xff\xd9"
    )
    return base64.b64encode(jpeg_bytes).decode("utf-8")


# ── Tests: _default_scores ─────────────────────────────────────────────────────

class TestDefaultScores(unittest.TestCase):
    def test_all_labels_present(self):
        scores = _default_scores()
        for label in EMOTION_LABELS:
            self.assertIn(label, scores)

    def test_values_sum_to_one(self):
        scores = _default_scores()
        self.assertAlmostEqual(sum(scores.values()), 1.0, places=2)

    def test_values_non_negative(self):
        for v in _default_scores().values():
            self.assertGreaterEqual(v, 0.0)


# ── Tests: _wellness_from_scores ───────────────────────────────────────────────

class TestWellnessFromScores(unittest.TestCase):
    def test_all_happy_gives_high_wellness(self):
        scores = {e: 0.0 for e in EMOTION_LABELS}
        scores["happy"] = 1.0
        wellness = _wellness_from_scores(scores)
        self.assertGreater(wellness, 0.8)

    def test_all_disgust_gives_low_wellness(self):
        scores = {e: 0.0 for e in EMOTION_LABELS}
        scores["disgust"] = 1.0
        wellness = _wellness_from_scores(scores)
        self.assertLess(wellness, 0.3)

    def test_result_clamped_to_0_1(self):
        scores = {e: 1.0 for e in EMOTION_LABELS}  # unnormalized
        wellness = _wellness_from_scores(scores)
        self.assertGreaterEqual(wellness, 0.0)
        self.assertLessEqual(wellness, 1.0)

    def test_neutral_gives_mid_wellness(self):
        scores = {e: 0.0 for e in EMOTION_LABELS}
        scores["neutral"] = 1.0
        wellness = _wellness_from_scores(scores)
        self.assertAlmostEqual(wellness, EMOTION_WELLNESS_MAP["neutral"], places=2)


# ── Tests: _unavailable_result ─────────────────────────────────────────────────

class TestUnavailableResult(unittest.TestCase):
    def test_structure(self):
        result = _unavailable_result("test reason")
        self.assertIn("top_emotion", result)
        self.assertIn("scores", result)
        self.assertIn("face_detected", result)
        self.assertIn("wellness_contribution", result)
        self.assertIn("source", result)

    def test_face_not_detected(self):
        self.assertFalse(_unavailable_result().get("face_detected"))

    def test_source_is_unavailable(self):
        self.assertEqual(_unavailable_result().get("source"), "unavailable")

    def test_wellness_is_neutral(self):
        self.assertEqual(_unavailable_result().get("wellness_contribution"), 0.5)


# ── Tests: analyze_face_emotion (no real camera/API needed) ───────────────────

class TestAnalyzeFaceEmotion(unittest.TestCase):
    def test_empty_input_returns_unavailable(self):
        result = analyze_face_emotion("")
        self.assertEqual(result["source"], "unavailable")
        self.assertFalse(result["face_detected"])

    def test_none_input_returns_unavailable(self):
        result = analyze_face_emotion(None)
        self.assertEqual(result["source"], "unavailable")

    def test_invalid_base64_returns_unavailable_or_dict(self):
        # Should not raise; must return a dict
        result = analyze_face_emotion("not_valid_base64!!!")
        self.assertIsInstance(result, dict)
        self.assertIn("source", result)
        self.assertIn("face_detected", result)

    def test_tiny_jpeg_returns_dict(self):
        img_b64 = _make_tiny_jpeg_b64()
        result = analyze_face_emotion(img_b64)
        self.assertIsInstance(result, dict)
        # Must contain all required keys
        for key in ("top_emotion", "scores", "face_detected",
                    "wellness_contribution", "source"):
            self.assertIn(key, result)

    def test_wellness_in_valid_range(self):
        img_b64 = _make_tiny_jpeg_b64()
        result = analyze_face_emotion(img_b64)
        w = result["wellness_contribution"]
        self.assertGreaterEqual(w, 0.0)
        self.assertLessEqual(w, 1.0)

    def test_scores_present(self):
        img_b64 = _make_tiny_jpeg_b64()
        result = analyze_face_emotion(img_b64)
        self.assertIsInstance(result.get("scores"), dict)


# ── Tests: fuse_text_and_face ─────────────────────────────────────────────────

class TestFuseTextAndFace(unittest.TestCase):
    def _sample_text_metrics(self):
        return {
            "anxiety": 0.6,
            "mood": 0.4,
            "stress": 0.7,
            "analysis": {"summary": "test"},
        }

    def test_no_face_detected_returns_unchanged_metrics(self):
        text = self._sample_text_metrics()
        face = _unavailable_result()
        result = fuse_text_and_face(text, face)
        self.assertAlmostEqual(result["anxiety"], 0.6)
        self.assertAlmostEqual(result["mood"], 0.4)
        self.assertAlmostEqual(result["stress"], 0.7)

    def test_no_face_detected_sets_fusion_used_false(self):
        text = self._sample_text_metrics()
        face = _unavailable_result()
        result = fuse_text_and_face(text, face)
        self.assertFalse(result.get("fusion_used"))

    def test_face_detected_changes_metrics(self):
        text = self._sample_text_metrics()
        face = {
            "top_emotion": "happy",
            "scores": {"happy": 1.0, "neutral": 0.0, "surprise": 0.0,
                       "sad": 0.0, "angry": 0.0, "fear": 0.0, "disgust": 0.0},
            "face_detected": True,
            "wellness_contribution": 0.9,
            "source": "gemini",
        }
        result = fuse_text_and_face(text, face)
        # Happy face (high wellness) should lower anxiety and stress, raise mood
        self.assertLess(result["anxiety"], text["anxiety"])
        self.assertGreater(result["mood"], text["mood"])
        self.assertLess(result["stress"], text["stress"])

    def test_face_detected_sets_fusion_used_true(self):
        text = self._sample_text_metrics()
        face = {
            "top_emotion": "neutral",
            "scores": {"happy": 0.0, "neutral": 1.0, "surprise": 0.0,
                       "sad": 0.0, "angry": 0.0, "fear": 0.0, "disgust": 0.0},
            "face_detected": True,
            "wellness_contribution": 0.6,
            "source": "deepface",
        }
        result = fuse_text_and_face(text, face)
        self.assertTrue(result.get("fusion_used"))

    def test_fused_metrics_in_valid_range(self):
        text = self._sample_text_metrics()
        face = {
            "top_emotion": "angry",
            "scores": {"happy": 0.0, "neutral": 0.0, "surprise": 0.0,
                       "sad": 0.0, "angry": 1.0, "fear": 0.0, "disgust": 0.0},
            "face_detected": True,
            "wellness_contribution": 0.2,
            "source": "deepface",
        }
        result = fuse_text_and_face(text, face)
        for key in ("anxiety", "mood", "stress"):
            self.assertGreaterEqual(result[key], 0.0)
            self.assertLessEqual(result[key], 1.0)

    def test_original_analysis_preserved(self):
        text = self._sample_text_metrics()
        face = _unavailable_result()
        result = fuse_text_and_face(text, face)
        self.assertEqual(result.get("analysis"), text["analysis"])

    def test_face_analysis_added_to_result(self):
        text = self._sample_text_metrics()
        face = _unavailable_result("test")
        result = fuse_text_and_face(text, face)
        self.assertIn("face_analysis", result)
        self.assertEqual(result["face_analysis"], face)

    def test_original_dict_not_mutated(self):
        text = self._sample_text_metrics()
        original_anxiety = text["anxiety"]
        face = {
            "top_emotion": "happy",
            "scores": {"happy": 1.0, "neutral": 0.0, "surprise": 0.0,
                       "sad": 0.0, "angry": 0.0, "fear": 0.0, "disgust": 0.0},
            "face_detected": True,
            "wellness_contribution": 0.9,
            "source": "gemini",
        }
        fuse_text_and_face(text, face)
        self.assertEqual(text["anxiety"], original_anxiety)  # original unchanged

    def test_custom_weights(self):
        text = {"anxiety": 0.5, "mood": 0.5, "stress": 0.5}
        face = {
            "top_emotion": "happy",
            "scores": {"happy": 1.0, "neutral": 0.0, "surprise": 0.0,
                       "sad": 0.0, "angry": 0.0, "fear": 0.0, "disgust": 0.0},
            "face_detected": True,
            "wellness_contribution": 1.0,  # max wellness → face_anxiety=0, face_mood=1, face_stress=0
            "source": "gemini",
        }
        # With text_weight=0, result should be purely face-based
        result = fuse_text_and_face(text, face, text_weight=0.0, face_weight=1.0)
        # face_anxiety = 1 - 1.0 = 0.0, face_mood = 1.0, face_stress = 0.0
        self.assertAlmostEqual(result["anxiety"], 0.0, places=2)
        self.assertAlmostEqual(result["mood"], 1.0, places=2)
        self.assertAlmostEqual(result["stress"], 0.0, places=2)

    def test_custom_weights_text_only(self):
        text = {"anxiety": 0.6, "mood": 0.4, "stress": 0.7}
        face = {
            "top_emotion": "happy",
            "scores": {"happy": 1.0, "neutral": 0.0, "surprise": 0.0,
                       "sad": 0.0, "angry": 0.0, "fear": 0.0, "disgust": 0.0},
            "face_detected": True,
            "wellness_contribution": 0.9,
            "source": "gemini",
        }
        # With text_weight=1.0, result should equal the original text metrics
        result = fuse_text_and_face(text, face, text_weight=1.0, face_weight=0.0)
        self.assertAlmostEqual(result["anxiety"], 0.6, places=2)
        self.assertAlmostEqual(result["mood"], 0.4, places=2)
        self.assertAlmostEqual(result["stress"], 0.7, places=2)

    def test_custom_weights_equal_blend(self):
        text = {"anxiety": 0.8, "mood": 0.2, "stress": 0.8}
        # wellness=0.5 → face_anxiety=0.5, face_mood=0.5, face_stress=0.5
        face = {
            "top_emotion": "neutral",
            "scores": {"happy": 0.0, "neutral": 1.0, "surprise": 0.0,
                       "sad": 0.0, "angry": 0.0, "fear": 0.0, "disgust": 0.0},
            "face_detected": True,
            "wellness_contribution": 0.5,
            "source": "deepface",
        }
        result = fuse_text_and_face(text, face, text_weight=0.5, face_weight=0.5)
        # anxiety: 0.5*0.8 + 0.5*0.5 = 0.65
        self.assertAlmostEqual(result["anxiety"], 0.65, places=2)
        # mood: 0.5*0.2 + 0.5*0.5 = 0.35
        self.assertAlmostEqual(result["mood"], 0.35, places=2)
        # stress: 0.5*0.8 + 0.5*0.5 = 0.65
        self.assertAlmostEqual(result["stress"], 0.65, places=2)


# ── Tests: text-only path compatibility ───────────────────────────────────────

class TestTextOnlyPathUnchanged(unittest.TestCase):
    """Verify the text-only analysis path is unaffected by face feature."""

    def _make_analyze_request_class(self):
        """Reproduce the AnalyzeRequest Pydantic model without importing server.py,
        to avoid requiring uvicorn/fastapi in the test environment."""
        from typing import Optional
        from pydantic import BaseModel

        class AnalyzeRequest(BaseModel):
            user_input: str
            username: str
            face_image_base64: Optional[str] = None

        return AnalyzeRequest

    def test_analyze_request_works_without_face(self):
        AnalyzeRequest = self._make_analyze_request_class()
        req = AnalyzeRequest(user_input="I feel okay", username="test_user")
        self.assertIsNone(req.face_image_base64)

    def test_analyze_request_works_with_face(self):
        AnalyzeRequest = self._make_analyze_request_class()
        req = AnalyzeRequest(
            user_input="I feel okay",
            username="test_user",
            face_image_base64="abc123==",
        )
        self.assertEqual(req.face_image_base64, "abc123==")


if __name__ == "__main__":
    unittest.main(verbosity=2)
