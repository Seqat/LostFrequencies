# LostFrequencies Backend

This FastAPI service receives normalized potentiometer values from the Pico W, asks a local LM Studio model for a compact historical/emotional interpretation, and passes that interpretation into a separate symbolic music generator that returns a strict playable note sequence.

## Technical Architecture

### Components

| Component | Description |
|-----------|-------------|
| `server.py` | FastAPI application, endpoint definitions |
| `llm_client.py` | LM Studio API client |
| `music_generator.py` | Symbolic music generator |
| `response_schema.py` | Pydantic data schemas |

### Data Flow

```
Pot values (pot1, pot2)
        ↓
   LM Studio Client
   (Emotional interpretation)
        ↓
Sembolik Müzik Generatoru
   (Note sequence generation)
        ↓
   PhraseResponse JSON
   (Send to Pico W)
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

---

# LostFrequencies Backend

Bu FastAPI servisi, Pico W'den normalize edilmiş potansiyometre değerlerini alır, yerel bir LM Studio modelinden kompakt tarihsel/duygusal bir yorumlama ister ve bu yorumlamayı kesin çalınabilir bir nota dizisi döndüren ayrı bir sembolik müzik generator'una aktarır.

## Teknik Mimari

### Bileşenler

| Bileşen | Açıklama |
|---------|----------|
| `server.py` | FastAPI uygulaması, endpoint tanımları |
| `llm_client.py` | LM Studio API istemcisi |
| `music_generator.py` | Sembolik müzik üretici |
| `response_schema.py` | Pydantic veri şemaları |

### Veri Akışı

```
Pot değerleri (pot1, pot2)
        ↓
   LM Studio Client
   (Duygusal yorumlama)
        ↓
Sembolik Müzik Generatoru
   (Nota dizisi üretimi)
        ↓
   PhraseResponse JSON
   (Pico W'ye gönderim)
```

## Kurulum

### Gereksinimler

- Python 3.10+
- LM Studio (opsiyonel, fallback mevcut)

### Adımlar

```bash
# 1. Sanal ortam oluştur
python3 -m venv .venv

# 2. Sanal ortamı aktif et
source .venv/bin/activate

# 3. Bağımlılıkları yükle
pip install -r requirements.txt

# 4. LM Studio yapılandırması (opsiyonel)
export LM_STUDIO_BASE_URL=http://127.0.0.1:1234/v1
export LM_STUDIO_MODEL=model-adiniz
export LM_STUDIO_TIMEOUT_S=2.0

# 5. Backend'i başlat
uvicorn server:app --host 0.0.0.0 --port 8000 --reload
```

## Endpoint'ler

### `GET /health`

Sistem durumunu kontrol eder.

**Yanıt:**

```json
{
  "status": "ok",
  "service": "lostfrequencies-backend"
}
```

### `POST /generate`

Potansiyometre değerlerinden müzik cümlesi üretir.

**İstek:**

```json
{
  "pot1": 0.33,
  "pot2": 0.78,
  "device_id": "pico-w-01",
  "current_phrase_id": "lf-previous"
}
```

**Yanıt:**

```json
{
  "phrase_id": "lf-a1b2c3d4e5",
  "mode_label": "farewell",
  "context_label": "dusty western",
  "tempo_bpm": 77,
  "total_duration_s": 10.0,
  "backend_status": "ok",
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

### Parametreler

| Parametre | Tip | Açıklama |
|-----------|-----|----------|
| `pot1` | float | 0-1 arası, gerilim/tempo |
| `pot2` | float | 0-1 arası, yoğunluk/mood |
| `device_id` | string | Cihaz tanımlayıcı |
| `current_phrase_id` | string | Mevcut cümle ID (opsiyonel) |

## LM Studio Yapılandırması

### Model Önerileri

- Kısa JSON çıktılarında stable instruct/chat modelleri kullanın
- `/v1/chat/completions` API'sini kullanır
- Canlı demo'lar için düşük sıcaklık (temperature) ayarı kullanın

### Ortam Değişkenleri

| Değişken | Varsayılan | Açıklama |
|----------|------------|----------|
| `LM_STUDIO_BASE_URL` | `http://127.0.0.1:1234/v1` | API base URL |
| `LM_STUDIO_MODEL` | - | Yüklü model adı |
| `LM_STUDIO_TIMEOUT_S` | `2.0` | Timeout süresi |

## Yedek Davranış

Sistem üç katmanlı yedekleme ile tasarlanmıştır:

1. **LM Studio yoksa**: Pot değerlerinden deterministik duygusal yorumlama
2. **Sembolik üretim başarısızsa**: Geçerli yedek cümle döndürülür
3. **Geçersiz nota alanları**: Yanıt şeması tarafından sınırlandırılır

## Geliştirme

```bash
# Test modu
python -m pytest

# Kod formatlama
black .

# Lint
ruff check .
```
