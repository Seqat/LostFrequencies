# LostFrequencies Backend

This FastAPI service receives normalized potentiometer values from the Pico W, asks a local LM Studio model for a compact historical/emotional interpretation, passes that interpretation into a separate symbolic music generator that returns a strict playable note sequence, and uses a Hugging Face model (`google/flan-t5-small`) to generate a thematic poetic sentence.

## Technical Architecture

### Components

| Component | Description |
|-----------|-------------|
| `server.py` | FastAPI application, endpoint definitions |
| `llm_client.py` | LM Studio API client |
| `music_generator.py` | Symbolic music generator |
| `nlp_poetry.py` | NLP poetry generator (Hugging Face Transformers) |
| `response_schema.py` | Pydantic data schemas |

### Data Flow

```
Pot values (pot1, pot2)
        ↓
   LM Studio Client
   (Emotional interpretation)
        ↓
Sembolik Müzik Generatoru & NLP Poetry Generator
   (Note sequence and poetry generation)
        ↓
   PhraseResponse JSON
   (Send to Pico W)
```

### Internal AI Prompts (Example Requests)

#### 1. Semantic Interpretation (LM Studio)

**System Prompt:**

```text
You are the semantic interpretation stage for an interactive generative music installation called LostFrequencies. Return only compact JSON with keys: mood, imagery, mode_hint, density, tension, contour, ornament, station_character, poetry_station_hint, poetry_mood_tone. Context: 1973, farewell, transition, mortality, legacy, dusty western atmosphere, restrained Dylan-era mood. Pot1 is a radio tuning dial scanning ghost stations of memory, so it should affect station identity, register, motif flavor, and which emotional channel is found. Pot2 is mood depth, so it should control darkness, emotional weight, density, and intensity. Avoid direct song quotation, cheerful pop, futuristic language, and long prose. poetry_station_hint should be a short cinematic station scene for a lyric model. poetry_mood_tone should be a short emotional tone phrase for a lyric model.
```

**User Prompt Example:**

```text
pot1=0.410, pot2=0.730. Interpret pot1 as FM tuning across fragile stations and pot2 as mood depth. Return a restrained musical intention for a short symbolic phrase.
```

#### 2. NLP Poetry Generation (Hugging Face)

**Prompt Example:**

```text
Write exactly one short poetic sentence in English.Style: dusty 1970's western, cinematic, tender, lonely. This sentence is in radio. Return only the sentence, with NO LABELS ORE PREFACE. Do not repeat words or phrases. Do not use bullet points. Keep it under 12 words. Station mood: a dust road station at dusk. Emotional intensity: heavy, grief-struck, dim. Core mood: farewell. Signal character: clear signal. Motion contour: descending. Imagery: dust road dusk.
```

## Setup

### Requirements

- Python 3.10+
- LM Studio (optional, fallback available)

### Steps

```bash
# 1. Create virtual environment
python3 -m venv .venv

# 2. Activate virtual environment
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. LM Studio configuration (optional)
export LM_STUDIO_BASE_URL=http://127.0.0.1:1234/v1
export LM_STUDIO_MODEL=your-model-name
export LM_STUDIO_TIMEOUT_S=2.0

# 5. Start backend
uvicorn server:app --host 0.0.0.0 --port 8000 --reload
```

## Endpoints

### `GET /health`

Checks system status.

**Response:**

```json
{
  "status": "ok",
  "service": "lostfrequencies-backend"
}
```

### `POST /generate`

Generates music phrase from potentiometer values.

**Request:**

```json
{
  "pot1": 0.33,
  "pot2": 0.78,
  "device_id": "pico-w-01",
  "current_phrase_id": "lf-previous"
}
```

**Response:**

```json
{
  "phrase_id": "lf-a1b2c3d4e5",
  "mode_label": "farewell",
  "context_label": "dusty western",
  "tempo_bpm": 77,
  "total_duration_s": 10.0,
  "backend_status": "ok",
  "ai2_generated_poetry": "The fading light leaves a heavy silence on the old dusty road.",
  "notes": [
    {
      "frequency_hz": 293.66,
      "duration_s": 1.01,
      "velocity": 0.61,
      "waveform": "triangle",
      "rest": false
    }
  ],
  "debug": {
    "llm_source": "lmstudio",
    "generator": "symbolic_hybrid"
  }
}
```

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `pot1` | float | 0-1 range, tension/tempo |
| `pot2` | float | 0-1 range, density/mood |
| `device_id` | string | Device identifier |
| `current_phrase_id` | string | Current phrase ID (optional) |

## LM Studio Configuration

### Model Recommendations

- Use stable instruct/chat models that are stable at short JSON outputs
- Uses LM Studio's OpenAI-compatible `/v1/chat/completions` API
- Keep temperature low for consistency during live demos

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `LM_STUDIO_BASE_URL` | `http://127.0.0.1:1234/v1` | API base URL |
| `LM_STUDIO_MODEL` | - | Loaded model name |
| `LM_STUDIO_TIMEOUT_S` | `2.0` | Timeout duration |

## Fallback Behavior

The system is designed with three-layer fallback:

1. **If LM Studio unavailable**: deterministic emotional interpretation from pot values
2. **If symbolic generation fails**: valid fallback phrase is emitted
3. **Invalid note fields**: clamped by response schema

## Development

```bash
# Test mode
python -m pytest

# Code formatting
black .

# Lint
ruff check .
```
