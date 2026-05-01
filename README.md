# LostFrequencies

LostFrequencies is an interactive generative music installation built for the CSE 358 "Knock! Design Your Door" project. A Raspberry Pi Pico W reads two potentiometers, shows live system state on a 0.96-inch OLED, sends expressive control values to a MacBook backend over Wi-Fi, and plays short loopable phrases through a PAM8406 amplifier and 3W speaker.

The piece is designed around a 1973 farewell atmosphere: transition, mortality, legacy, dusty-western space, and the emotional shadow of "Knockin' on Heaven's Door." Rather than building a generic music toy, the system turns physical interaction into small symbolic musical ideas that feel restrained, reflective, and final-ride cinematic.


## Technical Specifications

### Backend API

| Feature | Value |
|---------|-------|
| Framework | FastAPI |
| Port | 8000 |
| LLM Integration | LM Studio (OpenAI compatible) |
| Music Generation | Symbolic generator |
| Cache | Cached responses (1.2s cooldown) |

### Hardware Connections

| Pico Pin | Component |
|----------|-----------|
| GP26 (ADC0) | Potentiometer 1 |
| GP27 (ADC1) | Potentiometer 2 |
| GP0 | OLED SDA |
| GP1 | OLED SCL |
| GP15 | PWM audio out |

### Software Architecture

```
Pico W (MicroPython)
    ↓ HTTP POST (/generate)
FastAPI Backend (Python)
    ↓
LM Studio (Local LLM)
    ↓ JSON interpretation
Sembolik Müzik Generatoru
    ↓ Note sequence JSON
Pico W (PWM Synth)
    ↓
PAM8406 → Speaker
```

## Three AI Techniques

This project uses three distinct AI techniques, not just one prompt to the same model:

1. **Local LLM semantic interpretation**
   - Implemented through LM Studio's local OpenAI-compatible API.
   - Interprets the pot values in a historically grounded emotional frame.
   - Produces a compact JSON description of mood, imagery, tension, density, and contour.

2. **Separate symbolic music generation**
   - Implemented as an independent symbolic phrase generator in `backend/music_generator.py`.
   - Uses the LLM's structured interpretation as conditioning.
   - Produces the final note sequence, cadence, rhythmic density, and playable waveform assignments.

3. **NLP Poetry generation**
   - Implemented using Hugging Face Transformers and the `google/flan-t5-small` model in `backend/nlp_poetry.py`.
   - Generates a short, thematic, dusty-western style poetic sentence based on the imagery, mood, and signal character interpreted by the semantic LLM.

This separation is deliberate so the system is fast, modular, and easy to explain during the demo.

## Internal AI Prompts (Example Requests)

### 1. Semantic Interpretation (LM Studio)

**System Prompt:**
```text
You are the semantic interpretation stage for an interactive generative music installation called LostFrequencies. Return only compact JSON with keys: mood, imagery, mode_hint, density, tension, contour, ornament, station_character, poetry_station_hint, poetry_mood_tone. Context: 1973, farewell, transition, mortality, legacy, dusty western atmosphere, restrained Dylan-era mood. Pot1 is a radio tuning dial scanning ghost stations of memory, so it should affect station identity, register, motif flavor, and which emotional channel is found. Pot2 is mood depth, so it should control darkness, emotional weight, density, and intensity. Avoid direct song quotation, cheerful pop, futuristic language, and long prose. poetry_station_hint should be a short cinematic station scene for a lyric model. poetry_mood_tone should be a short emotional tone phrase for a lyric model.
```

**User Prompt Example:**
```text
pot1=0.410, pot2=0.730. Interpret pot1 as FM tuning across fragile stations and pot2 as mood depth. Return a restrained musical intention for a short symbolic phrase.
```

### 2. NLP Poetry Generation (Hugging Face)

**Prompt Example:**
```text
Write exactly one short poetic sentence in English.Style: dusty 1970's western, cinematic, tender, lonely. This sentence is in radio. Return only the sentence, with NO LABELS ORE PREFACE. Do not repeat words or phrases. Do not use bullet points. Keep it under 12 words. Station mood: a dust road station at dusk. Emotional intensity: heavy, grief-struck, dim. Core mood: farewell. Signal character: clear signal. Motion contour: descending. Imagery: dust road dusk.
```

## Historical Context Integration

The historical and cultural context is embedded in three layers:

- Prompt design steers the semantic layer toward 1973, farewell, transition, mortality, and dusty-western imagery.
- Musical rules bias the output toward somber modal colors, sparse phrasing, descending gestures, and loopable cadences instead of bright generic melodies.
- The OLED shows short contextual labels like `farewell`, `transition`, `release`, and `dusty western` so the installation communicates mood while it runs.

## Repository Layout

```
backend/
  server.py
  llm_client.py
  music_generator.py
  nlp_poetry.py
  response_schema.py
  requirements.txt
  README.md

picoHandler/
  main.py
  config.py
  wifi.py
  oled.py
  audio.py
  ssd1306.py
```

## Hardware Setup

Target hardware:

- Raspberry Pi Pico W
- 2 potentiometers
- 0.96-inch SSD1306-compatible OLED over I2C
- PAM8406 amplifier
- 3W speaker

Suggested Pico wiring:

- `GP26 / ADC0` -> potentiometer 1
- `GP27 / ADC1` -> potentiometer 2
- `GP0` -> OLED SDA
- `GP1` -> OLED SCL
- `GP15` -> PWM audio out to PAM8406 input
- Common ground shared between Pico, OLED, and amplifier

Update the exact pins in [config.py](picoHandler/config.py) if your wiring differs.

## Setup Instructions

### 1. Backend Setup

```bash
# Go to project directory
cd LostFrequencies/backend

# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# LM Studio configuration (optional)
export LM_STUDIO_BASE_URL=http://127.0.0.1:1234/v1
export LM_STUDIO_MODEL=your-model-name
export LM_STUDIO_TIMEOUT_S=2.0

# Start backend
uvicorn server:app --host 0.0.0.0 --port 8000 --reload
```

### 2. LM Studio Setup

1. Download and start LM Studio
2. Load a local instruct/chat model
3. Enable local server
4. Keep temperature low for consistent behavior

### 3. Pico W Setup

1. Flash MicroPython to the Pico W
2. Copy everything in `picoHandler/` onto the board
3. Edit Wi-Fi credentials in [config.py](picoHandler/config.py)
4. Reset the Pico

## Example Request / Response

Request:

```json
{
  "pot1": 0.41,
  "pot2": 0.73,
  "device_id": "pico-w-01",
  "current_phrase_id": "lf-current"
}
```

Response:

```json
{
  "phrase_id": "lf-a1b2c3d4e5",
  "mode_label": "farewell",
  "context_label": "dusty western",
  "tempo_bpm": 78,
  "total_duration_s": 10.0,
  "backend_status": "ok",
  "ai2_generated_poetry": "The fading light leaves a heavy silence on the old dusty road.",
  "notes": [
    {"frequency_hz": 293.66, "duration_s": 1.0, "velocity": 0.61, "waveform": "triangle", "rest": false},
    {"frequency_hz": 329.63, "duration_s": 0.5, "velocity": 0.58, "waveform": "sine", "rest": false},
    {"frequency_hz": null, "duration_s": 0.5, "velocity": 0.0, "waveform": "triangle", "rest": true}
  ],
  "debug": {
    "llm_source": "lmstudio",
    "generator": "symbolic_hybrid",
    "tension": 0.41,
    "density": 0.73
  }
}
```

## Troubleshooting

### Backend Not Working

```bash
# Port check
lsof -i :8000

# LM Studio connection test
curl http://127.0.0.1:1234/v1/models
```

### Pico W Connection Issues

- Check Wi-Fi credentials
- Verify backend IP address
- Review network access control (firewall) rules

### No Sound Output

- Check PWM pin connections
- Verify amplifier power connections
- Check volume settings

## Visual Documentation

- Add a wiring photo here
- Add an OLED-in-operation photo here
- Add a backend terminal screenshot here


