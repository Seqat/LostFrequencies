import time
from machine import ADC

import config
from audio import PhrasePlayer
from oled import OLEDStatus
from wifi import WiFiManager


def clamp(value, low=0.0, high=1.0):
    return max(low, min(high, value))


class LostFrequenciesController:
    def __init__(self):
        self.pot1 = ADC(config.POT1_ADC)
        self.pot2 = ADC(config.POT2_ADC)
        try:
            self.oled = OLEDStatus()
        except Exception:
            self.oled = None
        self.audio = PhrasePlayer()
        self.wifi = WiFiManager()
        self.filtered_p1 = 0.0
        self.filtered_p2 = 0.0
        self.last_post_ms = 0
        self.last_oled_ms = 0
        self.current_label = "searching"
        self.backend_status = "idle"
        self.current_phrase_id = None

    def run(self):
        while True:
            self.audio.update()
            self.wifi.ensure_connected()
            self._read_controls()
            self._maybe_post()
            self._maybe_refresh_oled()
            time.sleep_ms(2)

    def _read_controls(self):
        p1 = self.pot1.read_u16() / 65535
        p2 = self.pot2.read_u16() / 65535
        alpha = config.ADC_SMOOTHING
        self.filtered_p1 = clamp((alpha * p1) + ((1 - alpha) * self.filtered_p1))
        self.filtered_p2 = clamp((alpha * p2) + ((1 - alpha) * self.filtered_p2))

    def _maybe_post(self):
        now = time.ticks_ms()
        if time.ticks_diff(now, self.last_post_ms) < config.POST_INTERVAL_MS:
            return
        self.last_post_ms = now

        payload = {
            "pot1": round(self.filtered_p1, 3),
            "pot2": round(self.filtered_p2, 3),
            "device_id": config.DEVICE_ID,
            "current_phrase_id": self.current_phrase_id,
        }

        try:
            response = self.wifi.post_json(payload)
        except Exception:
            self.backend_status = "offline"
            return

        self.backend_status = response.get("backend_status", "ok")[:10]
        self.current_label = response.get("context_label", "farewell")[:16]
        phrase_id = response.get("phrase_id")
        if phrase_id and phrase_id != self.current_phrase_id:
            notes = self._sanitize_notes(response.get("notes", []))
            if notes:
                self.audio.set_phrase(notes)
                self.current_phrase_id = phrase_id

    def _maybe_refresh_oled(self):
        if self.oled is None:
            return
        now = time.ticks_ms()
        if time.ticks_diff(now, self.last_oled_ms) < config.OLED_REFRESH_MS:
            return
        self.last_oled_ms = now
        self.oled.render(
            self.wifi.status_label(),
            self.backend_status,
            self._station_frequency(),
            round(self.filtered_p2, 2),
            self.current_label,
            self.audio.play_state(),
        )

    def _station_frequency(self):
        span = config.FM_FREQ_MAX - config.FM_FREQ_MIN
        return config.FM_FREQ_MIN + (self.filtered_p1 * span)

    @staticmethod
    def _sanitize_notes(notes):
        clean = []
        for note in notes:
            try:
                duration = max(0.05, min(3.0, float(note.get("duration_s", 0.25))))
                velocity = max(0.0, min(1.0, float(note.get("velocity", 0.7))))
                waveform = note.get("waveform", "triangle")
                if waveform not in ("sine", "square", "triangle"):
                    waveform = "triangle"
                frequency = note.get("frequency_hz")
                rest = bool(note.get("rest")) or frequency in (None, 0, "0")
                frequency = None if rest else max(110.0, min(1174.66, float(frequency)))
                clean.append(
                    {
                        "duration_s": duration,
                        "velocity": 0.0 if rest else velocity,
                        "waveform": waveform,
                        "frequency_hz": frequency,
                        "rest": rest,
                    }
                )
            except Exception:
                continue
        return clean


controller = LostFrequenciesController()
controller.run()
