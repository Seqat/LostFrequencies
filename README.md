# LostFrequencies

LostFrequencies is an interactive generative music installation built for the CSE 358 "Knock! Design Your Door" project. A Raspberry Pi Pico W reads two potentiometers, shows live system state on a 0.96-inch OLED, sends expressive control values to a MacBook backend over Wi-Fi, and plays short loopable phrases through a PAM8406 amplifier and 3W speaker.

The piece is designed around a 1973 farewell atmosphere: transition, mortality, legacy, dusty-western space, and the emotional shadow of "Knockin' on Heaven's Door." Rather than building a generic music toy, the system turns physical interaction into small symbolic musical ideas that feel restrained, reflective, and final-ride cinematic.

## Artistic Statement

The installation treats the door as a threshold. Turning the pots does not just change pitch and speed; it shifts emotional gravity. One control leans the piece toward darkness, tension, and harmonic weight. The other increases motion, density, and brightness. Together they move the listener across a narrow expressive landscape shaped by 1973-era farewell imagery: dusty horizon lines, endings without spectacle, and a sense of passage rather than climax.

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

## Two AI Techniques

This project uses two distinct AI techniques, not two prompts to the same model:

1. **Local LLM semantic interpretation**
   - Implemented through LM Studio's local OpenAI-compatible API.
   - Interprets the pot values in a historically grounded emotional frame.
   - Produces a compact JSON description of mood, imagery, tension, density, and contour.

2. **Separate symbolic music generation**
   - Implemented as an independent symbolic phrase generator in `backend/music_generator.py`.
   - Uses the LLM's structured interpretation as conditioning.
   - Produces the final note sequence, cadence, rhythmic density, and playable waveform assignments.

This separation is deliberate so the system is fast, modular, and easy to explain during the demo.

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

---

# LostFrequencies

LostFrequencies, CSE 358 "Knock! Design Your Door" projesi için geliştirilmiş etkileşimli bir generatif müzik enstalasyonudur. Bir Raspberry Pi Pico W iki potansiyometreyi okur, canlı sistem durumunu 0.96 inç OLED'de gösterir, ifadesel kontrol değerlerini Wi-Fi üzerinden bir MacBook backend'ine gönderir ve bir PAM8406 amplifikatörü ve 3W hoparlör aracılığıyla kısa döngüsel cümleler çalar.

Sistem, 1973 veda atmosferi etrafında tasarlanmıştır: geçiş, ölümlülük, miras, tozlu-batı mekânı ve "Knockin' on Heaven's Door"nun duygusal gölgesi. Sıradan bir müzik oyuncağı inşa etmek yerine, sistem fiziksel etkileşimi kısıtlı, yansıtıcı ve son-yeğit cinematik hissettiren küçük sembolik müzik fikirlerine dönüştürür.

## Sanatçı İfadesi

Kurulum, kapıyı bir eşik olarak ele alır. Potları çevirmek sadece perdeyi ve hızı değiştirmez; duygusal ağırlığı kaydırır. Bir kontrol parçayı karanlığa, gerilime ve harmonik ağırlığa yönlendirir. Diğeri hareket yoğunluğunu ve parlaklığı artırır. Birlikte, 1973 veda imgeleri şekillenmiş dar bir ifade manzarasında dinleyiciyi taşır: tozlu ufuk çizgileri, gösterişsiz sonlar ve zirve yerine geçiş hissi.

## Teknik Özellikler

### Backend API

| Özellik | Değer |
|---------|-------|
| Framework | FastAPI |
| Port | 8000 |
| LLM Entegrasyonu | LM Studio (OpenAI uyumlu) |
| Müzik Üretimi | Sembolik generator |
| Önbellek | Cacheli yanıtlar (1.2s cooldown) |

### Donanım Bağlantıları

| Pico Pin | Bileşen |
|----------|---------|
| GP26 (ADC0) | Potansiyometre 1 |
| GP27 (ADC1) | Potansiyometre 2 |
| GP0 | OLED SDA |
| GP1 | OLED SCL |
| GP15 | PWM ses çıkışı |

### Yazılım Mimarisi

```
Pico W (MicroPython)
    ↓ HTTP POST (/generate)
FastAPI Backend (Python)
    ↓
LM Studio (Local LLM)
    ↓ JSON yorumlama
Sembolik Müzik Generatoru
    ↓ Nota dizisi JSON
Pico W (PWM Synth)
    ↓
PAM8406 → Hoparlör
```

## İki Yapay Zeka Tekniği

Bu proje, aynı modele iki prompt değil, iki farklı yapay zeka tekniği kullanır:

1. **Yerel LLM semantik yorumlama**
   - LM Studio'nun yerel OpenAI uyumlu API'si aracılığıyla uygulanır.
   - Pot değerlerini tarihsel olarak temellendirilmiş duygusal çerçevede yorumlar.
   - Mood, imgeler, gerilim, yoğunluk ve kontür hakkında kompakt JSON açıklaması üretir.

2. **Ayrı sembolik müzik üretimi**
   - `backend/music_generator.py`'da bağımsız sembolik cümle generatoru olarak uygulanır.
   - LLM'nin yapılandırılmış yorumlamasını koşullama olarak kullanır.
   - Son nota dizisini, kadansı, ritmik yoğunluğu ve çalınabilir dalga formu atamalarını üretir.

Bu ayrım, sistemin hızlı, modüler ve demo sırasında açıklanması kolay olması için bilinçli yapılmıştır.

## Tarihsel Bağlam Entegrasyonu

Tarihsel ve kültürel bağlam üç katmana gömülüdür:

- İstem tasarımı, semantik katmanı 1973, veda, geçiş, ölümlülük ve tozlu-batı imgelerine yönlendirir.
- Müzik kuralları çıktıyı sessiz modal renklere, seyrek cümlelemeye, alçalan jestlere ve parlak generik melodiler yerine döngüsel kadanslara yönlendirir.
- OLED, `farewell`, `transition`, `release` ve `dusty western` gibi kısa bağlamsal etiketler gösterir, böylece enstalasyon çalışırken mood'u iletir.

## Depo Yapısı

```
backend/
  server.py
  llm_client.py
  music_generator.py
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

## Donanım Kurulumu

Hedef donanım:

- Raspberry Pi Pico W
- 2 potansiyometre
- 0.96 inç SSD1306 uyumlu OLED (I2C üzerinden)
- PAM8406 amplifikatör
- 3W hoparlör

Önerilen Pico bağlantıları:

- `GP26 / ADC0` -> potansiyometre 1
- `GP27 / ADC1` -> potansiyometre 2
- `GP0` -> OLED SDA
- `GP1` -> OLED SCL
- `GP15` -> PWM ses çıkışı (PAM8406 girişi)
- Ortak toprak paylaşılır

Bağlantı pinlerini [config.py](picoHandler/config.py)'da güncelleyin.

## Kurulum Talimatları

### 1. Backend Kurulumu

```bash
# Proje dizinine git
cd LostFrequencies/backend

# Sanal ortam oluştur
python3 -m venv .venv

# Sanal ortamı aktif et
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate  # Windows

# Bağımlılıkları yükle
pip install -r requirements.txt

# LM Studio yapılandırması (opsiyonel)
export LM_STUDIO_BASE_URL=http://127.0.0.1:1234/v1
export LM_STUDIO_MODEL=model-adiniz
export LM_STUDIO_TIMEOUT_S=2.0

# Backend'i başlat
uvicorn server:app --host 0.0.0.0 --port 8000 --reload
```

### 2. LM Studio Kurulumu

1. LM Studio'yu indirin ve başlatın
2. Yerel bir instruct/chat modeli yükleyin
3. Local server'ı etkinleştirin
4. Düşük sıcaklık (temperature) ayarı kullanın

### 3. Pico W Kurulumu

1. MicroPython'u Pico W'ye flash'layın
2. `picoHandler/` klasöründeki tüm dosyaları kopyalayın
3. `config.py` dosyasında Wi-Fi kimlik bilgilerini düzenleyin
4. Pico'yu resetleyin

## Örnek İstek / Yanıt

İstek:

```json
{
  "pot1": 0.41,
  "pot2": 0.73,
  "device_id": "pico-w-01",
  "current_phrase_id": "lf-current"
}
```

Yanıt:

```json
{
  "phrase_id": "lf-a1b2c3d4e5",
  "mode_label": "farewell",
  "context_label": "dusty western",
  "tempo_bpm": 78,
  "total_duration_s": 10.0,
  "backend_status": "ok",
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

## Sorun Giderme

### Backend Çalışmıyor

```bash
# Port kontrolü
lsof -i :8000

# LM Studio bağlantısı testi
curl http://127.0.0.1:1234/v1/models
```

### Pico W Bağlantı Sorunları

- Wi-Fi kimlik bilgilerini kontrol edin
- Backend IP adresinin doğru olduğundan emin olun
- Ağ erişim kontrolü (firewall) kurallarını gözden geçirin

### Ses Çıkmıyor

- PWM pin bağlantılarını kontrol edin
- Amplifikatör güç bağlantılarını doğrulayın
- Ses seviyesi ayarlarını kontrol edin

## Görsel Dokümantasyon

- Bağlantı fotoğrafı buraya
- Çalışan OLED fotoğrafı buraya
- Backend terminal ekran görüntüsü buraya
