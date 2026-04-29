# Configuration constants 
# Update the Wi-Fi credentials and backend server details as needed.
WIFI_SSID = "YOUR_WIFI_NAME"
WIFI_PASSWORD = "YOUR_WIFI_PASSWORD"

BACKEND_HOST = "192.168.1.2" # IP address of the backend server
BACKEND_PORT = 8000 # Port number of the backend server
BACKEND_PATH = "/generate" 
DEVICE_ID = "pico-w-01"

POT1_ADC = 26
POT2_ADC = 27
I2C_SDA = 4
I2C_SCL = 5
OLED_WIDTH = 128
OLED_HEIGHT = 64
AUDIO_PWM_PIN = 15
I2C_FREQ = 50000

ADC_SMOOTHING = 0.2
ADC_EPSILON = 0.025
POST_INTERVAL_MS = 200
OLED_REFRESH_MS = 100
WIFI_RETRY_MS = 5000
BACKEND_TIMEOUT_S = 1.2
AUDIO_SAMPLE_RATE = 8000
AUDIO_ATTACK_MS = 12
AUDIO_RELEASE_MS = 20
FM_FREQ_MIN = 88.0
FM_FREQ_MAX = 108.0

# A simple startup melody to play on the Pico's speaker when it boots up.
STARTUP_MELODY = [
    {"frequency_hz": 293.66, "duration_s": 0.45, "velocity": 0.42, "waveform": "triangle", "rest": False},
    {"frequency_hz": 349.23, "duration_s": 0.35, "velocity": 0.38, "waveform": "triangle", "rest": False},
    {"frequency_hz": 392.00, "duration_s": 0.35, "velocity": 0.40, "waveform": "sine", "rest": False},
    {"frequency_hz": None, "duration_s": 0.15, "velocity": 0.0, "waveform": "triangle", "rest": True},
    {"frequency_hz": 440.00, "duration_s": 0.55, "velocity": 0.44, "waveform": "triangle", "rest": False},
    {"frequency_hz": 392.00, "duration_s": 0.35, "velocity": 0.36, "waveform": "sine", "rest": False},
    {"frequency_hz": 349.23, "duration_s": 0.45, "velocity": 0.34, "waveform": "triangle", "rest": False},
    {"frequency_hz": 293.66, "duration_s": 0.80, "velocity": 0.32, "waveform": "triangle", "rest": False},
]
