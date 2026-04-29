from __future__ import annotations

import time
from typing import Dict, Tuple
from uuid import uuid4

from fastapi import FastAPI

from llm_client import LMStudioClient
from music_generator import SymbolicMusicGenerator
from nlp_poetry import NLPPoetryGenerator
from response_schema import GenerateRequest, PhraseResponse


app = FastAPI(title="LostFrequencies Backend", version="1.0.0")

llm_client = LMStudioClient()
music_generator = SymbolicMusicGenerator()
nlp_poetry_generator = NLPPoetryGenerator()

_phrase_cache: Dict[Tuple[str, int, int], dict] = {}
_poetry_cache: Dict[Tuple[str, int, int], str] = {}
_cooldowns: Dict[str, Tuple[float, str]] = {}
_REGEN_COOLDOWN_S = 1.2
_POT_BUCKET_STEPS = 20
_POETRY_BUCKET_STEPS = 8


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "lostfrequencies-backend"}


@app.post("/generate", response_model=PhraseResponse)
def generate_phrase(request: GenerateRequest) -> PhraseResponse:
    bucket_key = (
        request.device_id,
        int(request.pot1 * _POT_BUCKET_STEPS),
        int(request.pot2 * _POT_BUCKET_STEPS),
    )
    poetry_bucket_key = (
        request.device_id,
        int(request.pot1 * _POETRY_BUCKET_STEPS),
        int(request.pot2 * _POETRY_BUCKET_STEPS),
    )
    cooldown = _cooldowns.get(request.device_id)
    cached = _phrase_cache.get(bucket_key)
    now = time.time()

    if cached and cooldown and now - cooldown[0] < _REGEN_COOLDOWN_S:
        return PhraseResponse(**cached)

    interpretation = llm_client.interpret(request.pot1, request.pot2)
    imagery_text = interpretation.get("imagery", "")
    poetry_line = _poetry_cache.get(poetry_bucket_key)
    if not poetry_line:
        poetry_line = nlp_poetry_generator.generate_line(
            imagery_text,
            interpretation.get("mood", ""),
            interpretation.get("station_character", ""),
            interpretation.get("contour", ""),
            interpretation.get("poetry_station_hint", ""),
            interpretation.get("poetry_mood_tone", ""),
        )
        _poetry_cache[poetry_bucket_key] = poetry_line
    backend_status = "ok" if interpretation.get("source") == "lmstudio" else "fallback_llm"

    try:
        generated = music_generator.generate(interpretation, request.pot1, request.pot2)
    except Exception:
        generated = music_generator.fallback_phrase(request.pot1, request.pot2)
        backend_status = "fallback_music"

    phrase_id = f"lf-{uuid4().hex[:10]}"
    response = PhraseResponse(
        phrase_id=phrase_id,
        mode_label=generated["mode_label"],
        context_label=generated["context_label"],
        tempo_bpm=generated["tempo_bpm"],
        total_duration_s=round(sum(note.duration_s for note in generated["notes"]), 2),
        backend_status=backend_status,
        ai2_generated_poetry=poetry_line,
        notes=generated["notes"],
        debug={
            "llm_source": interpretation.get("source", "unknown"),
            **generated["debug"],
        },
    )

    payload = response.model_dump()
    _phrase_cache[bucket_key] = payload
    _cooldowns[request.device_id] = (now, phrase_id)
    return response
