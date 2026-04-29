from __future__ import annotations

import json
import os
from typing import Any, Dict

import httpx


DEFAULT_INTERPRETATION = {
    "mood": "farewell",
    "imagery": "dusty western horizon",
    "mode_hint": "aeolian",
    "density": 0.35,
    "tension": 0.45,
    "contour": "descending",
    "ornament": "sparse",
    "station_character": "faded signal",
    "poetry_station_hint": "a half-lost roadside station at dusk",
    "poetry_mood_tone": "restrained grief, tender and weathered",
}


class LMStudioClient:
    def __init__(
        self,
        base_url: str | None = None,
        model: str | None = None,
        timeout_s: float | None = None,
    ) -> None:
        self.base_url = (base_url or os.getenv("LM_STUDIO_BASE_URL") or "http://127.0.0.1:1234/v1").rstrip("/")
        self.model = model or os.getenv("LM_STUDIO_MODEL") or "local-model"
        self.timeout_s = timeout_s or float(os.getenv("LM_STUDIO_TIMEOUT_S", "2.0"))

    def interpret(self, pot1: float, pot2: float) -> Dict[str, Any]:
        payload = {
            "model": self.model,
            "temperature": 0.3,
            "max_tokens": 180,
            "response_format": {"type": "json_object"},
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are the semantic interpretation stage for an interactive generative "
                        "music installation called LostFrequencies. Return only compact JSON with "
                        "keys: mood, imagery, mode_hint, density, tension, contour, ornament, "
                        "station_character, poetry_station_hint, poetry_mood_tone. Context: 1973, farewell, transition, mortality, "
                        "legacy, dusty western atmosphere, restrained Dylan-era mood. Pot1 is a "
                        "radio tuning dial scanning ghost stations of memory, so it should affect "
                        "station identity, register, motif flavor, and which emotional channel is "
                        "found. Pot2 is mood depth, so it should control darkness, emotional "
                        "weight, density, and intensity. Avoid direct song quotation, cheerful pop, "
                        "futuristic language, and long prose. "
                        "poetry_station_hint should be a short cinematic station scene for a lyric model. "
                        "poetry_mood_tone should be a short emotional tone phrase for a lyric model."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"pot1={pot1:.3f}, pot2={pot2:.3f}. "
                        "Interpret pot1 as FM tuning across fragile stations and pot2 as mood "
                        "depth. Return a restrained musical intention for a short symbolic phrase."
                    ),
                },
            ],
        }

        try:
            with httpx.Client(timeout=self.timeout_s) as client:
                response = client.post(f"{self.base_url}/chat/completions", json=payload)
                response.raise_for_status()
                body = response.json()
        except Exception:
            return self.fallback(pot1, pot2, source="fallback_unreachable")

        content = self._extract_content(body)
        parsed = self._parse_json(content)
        if not parsed:
            return self.fallback(pot1, pot2, source="fallback_parse_error")

        parsed["density"] = self._clamp_float(parsed.get("density", pot2), pot2)
        parsed["tension"] = self._clamp_float(parsed.get("tension", pot2), pot2)
        parsed["mood"] = self._safe_label(parsed.get("mood"), DEFAULT_INTERPRETATION["mood"])
        parsed["imagery"] = self._safe_label(parsed.get("imagery"), DEFAULT_INTERPRETATION["imagery"], 48)
        parsed["mode_hint"] = self._safe_label(parsed.get("mode_hint"), DEFAULT_INTERPRETATION["mode_hint"])
        parsed["contour"] = self._safe_label(parsed.get("contour"), DEFAULT_INTERPRETATION["contour"])
        parsed["ornament"] = self._safe_label(parsed.get("ornament"), DEFAULT_INTERPRETATION["ornament"])
        parsed["station_character"] = self._safe_label(
            parsed.get("station_character"), DEFAULT_INTERPRETATION["station_character"], 24
        )
        parsed["poetry_station_hint"] = self._safe_label(
            parsed.get("poetry_station_hint"), DEFAULT_INTERPRETATION["poetry_station_hint"], 64
        )
        parsed["poetry_mood_tone"] = self._safe_label(
            parsed.get("poetry_mood_tone"), DEFAULT_INTERPRETATION["poetry_mood_tone"], 64
        )
        parsed["source"] = "lmstudio"
        return parsed

    def fallback(self, pot1: float, pot2: float, source: str = "fallback") -> Dict[str, Any]:
        station = max(0.0, min(1.0, pot1))
        mood_depth = max(0.0, min(1.0, pot2))
        tension = mood_depth
        density = max(0.15, min(1.0, (mood_depth * 0.75) + (0.15 if station > 0.55 else 0.0)))
        if station < 0.2:
            mood = "static prayer"
            imagery = "faded chapel air"
            station_character = "thin static"
        elif station < 0.4:
            mood = "farewell"
            imagery = "dust road dusk"
            station_character = "clear signal"
        elif station < 0.7:
            mood = "transition"
            imagery = "last ride horizon"
            station_character = "warm band"
        else:
            mood = "final ride"
            imagery = "midnight county line"
            station_character = "ghost station"
        mode_hint = "aeolian" if mood_depth > 0.66 else "dorian" if mood_depth > 0.33 else "mixolydian"
        contour = "descending" if mood_depth > 0.5 else "arched"
        ornament = "sparse" if mood_depth < 0.45 else "pulsed"
        return {
            "mood": mood,
            "imagery": imagery,
            "mode_hint": mode_hint,
            "density": density,
            "tension": tension,
            "contour": contour,
            "ornament": ornament,
            "station_character": station_character,
            "poetry_station_hint": self._fallback_poetry_station_hint(station),
            "poetry_mood_tone": self._fallback_poetry_mood_tone(mood_depth),
            "source": source,
        }

    @staticmethod
    def _extract_content(body: Dict[str, Any]) -> str:
        try:
            return body["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError):
            return ""

    @staticmethod
    def _parse_json(content: str) -> Dict[str, Any] | None:
        if not content:
            return None
        text = content.strip()
        if "```" in text:
            parts = [part for part in text.split("```") if part.strip()]
            text = parts[-1]
            if text.lower().startswith("json"):
                text = text[4:].strip()
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1:
            text = text[start : end + 1]
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            return None
        return parsed if isinstance(parsed, dict) else None

    @staticmethod
    def _clamp_float(value: Any, default: float) -> float:
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            numeric = default
        return max(0.0, min(1.0, numeric))

    @staticmethod
    def _safe_label(value: Any, default: str, max_len: int = 24) -> str:
        if not isinstance(value, str) or not value.strip():
            return default
        return value.strip().lower()[:max_len]

    @staticmethod
    def _fallback_poetry_station_hint(station: float) -> str:
        if station < 0.2:
            return "a chapel station buried in static"
        if station < 0.4:
            return "a dust road station at dusk"
        if station < 0.6:
            return "a highway station near the last horizon"
        if station < 0.8:
            return "a county line station with worn headlights"
        return "a ghost station past midnight"

    @staticmethod
    def _fallback_poetry_mood_tone(mood_depth: float) -> str:
        if mood_depth < 0.2:
            return "barely aching, hushed, almost hopeful"
        if mood_depth < 0.4:
            return "wistful, restrained, tender"
        if mood_depth < 0.6:
            return "melancholic, lonely, worn"
        if mood_depth < 0.8:
            return "heavy, grief-struck, dim"
        return "heavy, grief-soaked, desolate"
