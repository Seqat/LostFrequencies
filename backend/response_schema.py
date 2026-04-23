from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator, model_validator


ALLOWED_WAVEFORMS = {"sine", "square", "triangle"}


class GenerateRequest(BaseModel):
    pot1: float = Field(..., description="Normalized control value 0.0-1.0")
    pot2: float = Field(..., description="Normalized control value 0.0-1.0")
    device_id: str = Field(default="pico-w-01", min_length=1, max_length=64)
    current_phrase_id: Optional[str] = Field(default=None, max_length=128)

    @field_validator("pot1", "pot2", mode="before")
    @classmethod
    def clamp_pot(cls, value: Any) -> float:
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            numeric = 0.0
        return max(0.0, min(1.0, numeric))


class NoteEvent(BaseModel):
    frequency_hz: Optional[float] = Field(default=None, description="Null for rests")
    duration_s: float = Field(..., ge=0.05, le=4.0)
    velocity: float = Field(default=0.7, ge=0.0, le=1.0)
    waveform: str = Field(default="triangle")
    rest: bool = Field(default=False)

    @field_validator("frequency_hz", mode="before")
    @classmethod
    def clamp_frequency(cls, value: Any) -> Optional[float]:
        if value in (None, "", False):
            return None
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            return None
        return max(110.0, min(1174.66, numeric))

    @field_validator("waveform", mode="before")
    @classmethod
    def normalize_waveform(cls, value: Any) -> str:
        if isinstance(value, str) and value.lower() in ALLOWED_WAVEFORMS:
            return value.lower()
        return "triangle"

    @model_validator(mode="after")
    def align_rest_and_frequency(self) -> "NoteEvent":
        if self.rest or self.frequency_hz is None:
            self.rest = True
            self.frequency_hz = None
            self.velocity = 0.0
        return self


class PhraseResponse(BaseModel):
    phrase_id: str
    mode_label: str = Field(..., max_length=32)
    context_label: str = Field(..., max_length=32)
    tempo_bpm: int = Field(..., ge=40, le=140)
    total_duration_s: float = Field(..., ge=8.0, le=12.0)
    backend_status: str = Field(default="ok", max_length=32)
    notes: List[NoteEvent]
    debug: Dict[str, Any] = Field(default_factory=dict)

