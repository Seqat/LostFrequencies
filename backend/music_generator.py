from __future__ import annotations

import hashlib
import math
import random
from typing import Any, Dict, List, Tuple

from response_schema import NoteEvent


SCALES = {
    "aeolian": [0, 2, 3, 5, 7, 8, 10],
    "dorian": [0, 2, 3, 5, 7, 9, 10],
    "mixolydian": [0, 2, 4, 5, 7, 9, 10],
}

CONTEXT_LABELS = [
    (0.25, "release"),
    (0.5, "farewell"),
    (0.75, "transition"),
    (1.0, "dusty western"),
]

RHYTHM_CELLS = {
    "sparse": [1.5, 1.0, 0.5, 1.0],
    "steady": [1.0, 0.5, 0.5, 1.0, 1.0],
    "driving": [0.5, 0.5, 0.25, 0.25, 0.5, 1.0],
}


class SymbolicMusicGenerator:
    def generate(self, interpretation: Dict[str, Any], pot1: float, pot2: float) -> Dict[str, Any]:
        seed = self._seed_for(interpretation, pot1, pot2)
        rng = random.Random(seed)

        station = self._clamp(pot1)
        mood_depth = self._clamp(pot2)
        tension = self._clamp(interpretation.get("tension", mood_depth))
        density = self._clamp(interpretation.get("density", mood_depth))
        mode_name = self._choose_mode(interpretation.get("mode_hint"), tension, density)
        tempo = int(round(54 + density * 18 + mood_depth * 10))
        base_midi = 45 + int(station * 12)
        total_target = 10.0

        rhythm_name = "sparse" if density < 0.34 else "steady" if density < 0.68 else "driving"
        rhythm_pattern = self._expand_rhythm(RHYTHM_CELLS[rhythm_name], total_target, rng)
        contour = str(interpretation.get("contour", "descending"))
        notes = self._compose_notes(rhythm_pattern, mode_name, base_midi, contour, tension, density, rng)
        notes = self._fit_total_duration(notes, total_target)

        mode_label = str(interpretation.get("mood") or "farewell")[:32]
        context_label = self._context_label(tension, density)

        return {
            "tempo_bpm": max(40, min(140, tempo)),
            "mode_label": mode_label,
            "context_label": context_label,
            "notes": [NoteEvent(**note) for note in notes],
            "debug": {
                "generator": "symbolic_hybrid",
                "mode_name": mode_name,
                "rhythm_name": rhythm_name,
                "seed": seed,
                "station": round(station, 3),
                "tension": round(tension, 3),
                "density": round(density, 3),
                "imagery": interpretation.get("imagery", ""),
                "ornament": interpretation.get("ornament", ""),
                "station_character": interpretation.get("station_character", ""),
            },
        }

    def fallback_phrase(self, pot1: float, pot2: float) -> Dict[str, Any]:
        fallback = {
            "tension": pot2,
            "density": pot2,
            "mood": "farewell",
            "mode_hint": "aeolian",
            "contour": "descending",
            "imagery": "dusty western horizon",
            "ornament": "sparse",
            "station_character": "clear signal",
        }
        return self.generate(fallback, pot1, pot2)

    @staticmethod
    def _seed_for(interpretation: Dict[str, Any], pot1: float, pot2: float) -> int:
        joined = f"{pot1:.3f}|{pot2:.3f}|{interpretation.get('mood','')}|{interpretation.get('mode_hint','')}"
        digest = hashlib.sha256(joined.encode("utf-8")).hexdigest()
        return int(digest[:8], 16)

    @staticmethod
    def _clamp(value: Any) -> float:
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            numeric = 0.0
        return max(0.0, min(1.0, numeric))

    @staticmethod
    def _choose_mode(mode_hint: Any, tension: float, density: float) -> str:
        if isinstance(mode_hint, str) and mode_hint.lower() in SCALES:
            return mode_hint.lower()
        if tension > 0.7:
            return "aeolian"
        if density > 0.55:
            return "dorian"
        return "mixolydian"

    @staticmethod
    def _expand_rhythm(cell: List[float], target: float, rng: random.Random) -> List[float]:
        values: List[float] = []
        while sum(values) < target - 0.25:
            for duration in cell:
                jitter = 0.0 if duration >= 1.0 else rng.choice([0.0, 0.0, 0.25])
                values.append(max(0.25, duration + jitter))
                if sum(values) >= target - 0.25:
                    break
        return values

    def _compose_notes(
        self,
        rhythm_pattern: List[float],
        mode_name: str,
        base_midi: int,
        contour: str,
        tension: float,
        density: float,
        rng: random.Random,
    ) -> List[Dict[str, Any]]:
        scale = SCALES[mode_name]
        step_pattern = self._contour_steps(contour, density, rng)
        waveforms = ["triangle", "sine"] if tension < 0.55 else ["triangle", "square"]
        notes: List[Dict[str, Any]] = []
        degree_index = rng.randint(1, 3)

        for idx, duration in enumerate(rhythm_pattern):
            if idx % 5 == 4 and density < 0.55:
                notes.append(
                    {"frequency_hz": None, "duration_s": duration, "velocity": 0.0, "waveform": "triangle", "rest": True}
                )
                continue

            degree_index = max(0, min(len(scale) - 1, degree_index + step_pattern[idx % len(step_pattern)]))
            octave_offset = -12 if tension > 0.7 and idx < len(rhythm_pattern) // 2 else 0
            midi = base_midi + scale[degree_index] + octave_offset

            if idx == len(rhythm_pattern) - 1:
                midi = base_midi + scale[0]
            elif idx == len(rhythm_pattern) - 2 and tension > 0.6:
                midi = base_midi + scale[4]

            frequency = 440.0 * math.pow(2.0, (midi - 69) / 12.0)
            velocity = max(0.35, min(0.9, 0.52 + density * 0.22 - tension * 0.08 + rng.uniform(-0.05, 0.07)))
            notes.append(
                {
                    "frequency_hz": round(frequency, 2),
                    "duration_s": duration,
                    "velocity": round(velocity, 2),
                    "waveform": rng.choice(waveforms),
                    "rest": False,
                }
            )
        return notes

    @staticmethod
    def _contour_steps(contour: str, density: float, rng: random.Random) -> List[int]:
        if contour == "descending":
            base = [-1, 0, -1, 1]
        elif contour == "arched":
            base = [1, 1, -1, -1]
        else:
            base = [0, 1, -1, 0]
        if density > 0.65:
            base = [step + rng.choice([-1, 0, 1]) for step in base]
        return base

    @staticmethod
    def _fit_total_duration(notes: List[Dict[str, Any]], target: float) -> List[Dict[str, Any]]:
        total = sum(note["duration_s"] for note in notes)
        if not notes:
            return notes
        scale = target / total if total else 1.0
        clamped_total = 0.0
        for note in notes:
            note["duration_s"] = round(max(0.1, min(2.5, note["duration_s"] * scale)), 2)
            clamped_total += note["duration_s"]
        delta = round(target - clamped_total, 2)
        notes[-1]["duration_s"] = round(max(0.1, min(3.0, notes[-1]["duration_s"] + delta)), 2)
        return notes

    @staticmethod
    def _context_label(tension: float, density: float) -> str:
        combined = (tension * 0.65) + (density * 0.35)
        for threshold, label in CONTEXT_LABELS:
            if combined <= threshold:
                return label
        return "dusty western"
