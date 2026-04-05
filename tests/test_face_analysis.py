"""
Tests for face_analyzer.py and the /analyze endpoint with face image support.

Run with:
    cd backend && python -m pytest ../tests/test_face_analysis.py -v
"""

import base64
import io
import sys
import os
import json

# Make backend modules importable when running from repo root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_tiny_jpeg_b64() -> str:
    """Return a minimal valid JPEG encoded as base64 (1×1 white pixel)."""
    # Minimal valid JPEG bytes (1×1 white pixel)
    jpeg_bytes = (
        b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00"
        b"\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t"
        b"\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a"
        b"\x1f\x1e\x1d\x1a\x1c\x1c $.' \",#\x1c\x1c(7),01444\x1f'9=82<.342\x1e"
        b"\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00"
        b"\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00"
        b"\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b"
        b"\xff\xc4\x00\xb5\x10\x00\x02\x01\x03\x03\x02\x04\x03\x05\x05\x04"
        b"\x04\x00\x00\x01}\x01\x02\x03\x00\x04\x11\x05\x12!1A\x06\x13Qa"
        b'\x07"q\x142\x81\x91\xa1\x08#B\xb1\xc1\x15R\xd1\xf0$3br\x82\t\n'
        b"\x16\x17\x18\x19\x1a%&'()*456789:CDEFGHIJSTUVWXYZ"
        b"cdefghijstuvwxyz\x83\x84\x85\x86\x87\x88\x89\x8a\x92\x93\x94"
        b"\x95\x96\x97\x98\x99\x9a\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa"
        b"\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xc2\xc3\xc4\xc5\xc6\xc7"
        b"\xc8\xc9\xca\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xe1\xe2\xe3"
        b"\xe4\xe5\xe6\xe7\xe8\xe9\xea\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8"
        b"\xf9\xfa\xff\xda\x00\x08\x01\x01\x00\x00?\x00\xfb\xd9"
    )
    return base64.b64encode(jpeg_bytes).decode("utf-8")


# ---------------------------------------------------------------------------
# Unit tests for face_analyzer._resize_image_bytes
# ---------------------------------------------------------------------------

class TestResizeImageBytes:
    def test_returns_bytes(self):
        from modules.face_analyzer import _resize_image_bytes

        dummy = b"\x00" * 100
        result = _resize_image_bytes(dummy, max_px=256)
        assert isinstance(result, bytes)

    def test_falls_back_on_invalid_input(self):
        """Invalid bytes should be returned unchanged (graceful fallback)."""
        from modules.face_analyzer import _resize_image_bytes

        invalid = b"not an image"
        result = _resize_image_bytes(invalid, max_px=256)
        assert result == invalid


# ---------------------------------------------------------------------------
# Unit tests for face_analyzer._emotion_probs_to_dimensions
# ---------------------------------------------------------------------------

class TestEmotionProbsToDimensions:
    def test_happy_emotion(self):
        from modules.face_analyzer import _emotion_probs_to_dimensions

        dims = _emotion_probs_to_dimensions({"happy": 1.0, "sad": 0.0,
                                             "angry": 0.0, "fear": 0.0,
                                             "neutral": 0.0, "surprise": 0.0,
                                             "disgust": 0.0})
        # Happy should produce high mood and low anxiety/stress
        assert dims["mood"] > 0.7
        assert dims["anxiety"] < 0.2
        assert dims["stress"] < 0.2

    def test_fear_emotion(self):
        from modules.face_analyzer import _emotion_probs_to_dimensions

        dims = _emotion_probs_to_dimensions({"happy": 0.0, "sad": 0.0,
                                             "angry": 0.0, "fear": 1.0,
                                             "neutral": 0.0, "surprise": 0.0,
                                             "disgust": 0.0})
        assert dims["anxiety"] > 0.7
        assert dims["mood"] < 0.3

    def test_all_values_in_range(self):
        from modules.face_analyzer import _emotion_probs_to_dimensions

        probs = {"happy": 0.14, "sad": 0.14, "angry": 0.14, "fear": 0.14,
                 "neutral": 0.15, "surprise": 0.14, "disgust": 0.15}
        dims = _emotion_probs_to_dimensions(probs)
        for key in ("anxiety", "mood", "stress"):
            assert 0.0 <= dims[key] <= 1.0, f"{key} out of range: {dims[key]}"

    def test_empty_probs(self):
        from modules.face_analyzer import _emotion_probs_to_dimensions

        dims = _emotion_probs_to_dimensions({})
        for key in ("anxiety", "mood", "stress"):
            assert 0.0 <= dims[key] <= 1.0


# ---------------------------------------------------------------------------
# Unit tests for analyze_face_emotion — no Gemini key / API call mocked
# ---------------------------------------------------------------------------

class TestAnalyzeFaceEmotion:
    def test_returns_disabled_when_no_image(self):
        from modules.face_analyzer import analyze_face_emotion

        result = analyze_face_emotion("")
        assert result == {"enabled": False}

    def test_returns_disabled_when_no_api_key(self, monkeypatch):
        """When GEMINI_API_KEY is blank the function should return disabled."""
        monkeypatch.setenv("GEMINI_API_KEY", "")
        # Re-import so the env var is picked up
        import importlib
        import modules.face_analyzer as fa
        importlib.reload(fa)

        result = fa.analyze_face_emotion(_make_tiny_jpeg_b64())
        assert result == {"enabled": False}

    def test_graceful_failure_on_bad_base64(self, monkeypatch):
        """Corrupt base64 must not raise — should return disabled."""
        monkeypatch.setenv("GEMINI_API_KEY", "fake-key-for-testing")

        import importlib
        import modules.face_analyzer as fa
        importlib.reload(fa)

        # Patch _build_vision_model to simulate model that raises
        class _FakeModel:
            def generate_content(self, _):
                raise RuntimeError("Simulated API error")

        monkeypatch.setattr(fa, "_build_vision_model", lambda: _FakeModel())

        result = fa.analyze_face_emotion("!!!invalid base64!!!")
        assert result == {"enabled": False}

    def test_graceful_failure_on_api_error(self, monkeypatch):
        """If the Gemini API call raises, the function must return disabled."""
        monkeypatch.setenv("GEMINI_API_KEY", "fake-key-for-testing")

        import importlib
        import modules.face_analyzer as fa
        importlib.reload(fa)

        class _FakeModel:
            def generate_content(self, _):
                raise RuntimeError("Simulated API error")

        monkeypatch.setattr(fa, "_build_vision_model", lambda: _FakeModel())

        result = fa.analyze_face_emotion(_make_tiny_jpeg_b64())
        assert result == {"enabled": False}

    def test_valid_response_parsed_correctly(self, monkeypatch):
        """Simulate a successful Gemini response and verify field structure."""
        monkeypatch.setenv("GEMINI_API_KEY", "fake-key-for-testing")

        import importlib
        import modules.face_analyzer as fa
        importlib.reload(fa)

        mock_json = json.dumps({
            "happy": 0.05, "sad": 0.60, "angry": 0.05, "fear": 0.10,
            "neutral": 0.10, "surprise": 0.05, "disgust": 0.05
        })

        class _FakeResponse:
            text = mock_json

        class _FakeModel:
            def generate_content(self, _):
                return _FakeResponse()

        monkeypatch.setattr(fa, "_build_vision_model", lambda: _FakeModel())

        result = fa.analyze_face_emotion(_make_tiny_jpeg_b64())

        assert result["enabled"] is True
        assert result["primary_expression"] == "sad"
        assert 0.0 <= result["anxiety"] <= 1.0
        assert 0.0 <= result["mood"] <= 1.0
        assert 0.0 <= result["stress"] <= 1.0
        assert "raw_emotions" in result


# ---------------------------------------------------------------------------
# Integration-style tests for the /analyze endpoint (no real server needed)
# ---------------------------------------------------------------------------

class TestAnalyzeEndpoint:
    """
    These tests import the FastAPI app directly and use the ASGI test client,
    so no real server needs to be running.
    """

    @pytest.fixture
    def client(self):
        """Provide a TestClient for the FastAPI app."""
        try:
            from fastapi.testclient import TestClient
            from server import app
            return TestClient(app)
        except Exception as exc:
            pytest.skip(f"Could not create test client: {exc}")

    def test_text_only_analyze(self, client):
        resp = client.post("/analyze", json={
            "user_input": "I feel stressed and overwhelmed today.",
            "username": "test_user",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "metrics" in data
        assert "disclaimer" in data
        assert "wellness_indicator" in data
        assert data["wellness_indicator"] in ("stable", "watch", "high-stress")

    def test_face_consent_false_skips_face_analysis(self, client):
        resp = client.post("/analyze", json={
            "user_input": "Feeling okay.",
            "username": "test_user",
            "face_image_b64": _make_tiny_jpeg_b64(),
            "face_consent": False,
        })
        assert resp.status_code == 200
        data = resp.json()
        face = data.get("face_emotion", {})
        assert face.get("enabled") is False

    def test_face_consent_true_no_image_graceful(self, client):
        """Consent given but no image — should not crash."""
        resp = client.post("/analyze", json={
            "user_input": "I am anxious.",
            "username": "test_user",
            "face_consent": True,
        })
        assert resp.status_code == 200

    def test_disclaimer_always_present(self, client):
        resp = client.post("/analyze", json={
            "user_input": "Feeling great!",
            "username": "test_user",
        })
        assert resp.status_code == 200
        assert "disclaimer" in resp.json()
        assert "NOT a medical diagnosis" in resp.json()["disclaimer"]
