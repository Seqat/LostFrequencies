import math
import time

from machine import PWM, Pin

import config


class PhrasePlayer:
    def __init__(self):
        self.pwm = PWM(Pin(config.AUDIO_PWM_PIN))
        self.current_phrase = self._normalize_phrase(config.STARTUP_MELODY)
        self.pending_phrase = None
        self.note_index = 0
        self.note_started_ms = time.ticks_ms()
        self.loop_count = 0
        self.is_startup_phrase = True

    def set_phrase(self, notes):
        notes = self._normalize_phrase(notes)
        if not notes:
            return
        if not self.current_phrase:
            self.current_phrase = notes
            self.note_index = 0
            self.note_started_ms = time.ticks_ms()
            self.is_startup_phrase = False
        elif self.is_startup_phrase and self.note_index == 0:
            self.current_phrase = notes
            self.pending_phrase = None
            self.note_started_ms = time.ticks_ms()
            self.is_startup_phrase = False
        else:
            self.pending_phrase = notes

    def play_state(self):
        if self.pending_phrase:
            return "queued"
        if self.is_startup_phrase:
            return "waiting"
        if self.current_phrase:
            return "playing"
        return "idle"

    def update(self):
        if not self.current_phrase:
            self.pwm.duty_u16(0)
            return

        now_ms = time.ticks_ms()
        note = self.current_phrase[self.note_index]
        duration_ms = int(note["duration_s"] * 1000)

        if time.ticks_diff(now_ms, self.note_started_ms) >= duration_ms:
            self.note_index += 1
            self.note_started_ms = now_ms
            if self.note_index >= len(self.current_phrase):
                self.note_index = 0
                self.loop_count += 1
                if self.pending_phrase:
                    self.current_phrase = self.pending_phrase
                    self.pending_phrase = None
                    self.is_startup_phrase = False
            note = self.current_phrase[self.note_index]
            duration_ms = int(note["duration_s"] * 1000)

        if note.get("rest") or not note.get("frequency_hz"):
            self.pwm.duty_u16(0)
            return

        progress = min(1.0, time.ticks_diff(now_ms, self.note_started_ms) / max(1, duration_ms))
        envelope = self._envelope(progress, note["duration_s"])
        self._drive_note(note["frequency_hz"], note["velocity"] * envelope, note["waveform"])

    @staticmethod
    def _envelope(progress, duration_s):
        attack = min(0.2, config.AUDIO_ATTACK_MS / max(1.0, duration_s * 1000.0))
        release = min(0.25, config.AUDIO_RELEASE_MS / max(1.0, duration_s * 1000.0))
        if progress < attack:
            return progress / max(0.001, attack)
        if progress > 1.0 - release:
            return max(0.0, (1.0 - progress) / max(0.001, release))
        return 1.0

    def _drive_note(self, frequency_hz, amplitude, waveform):
        freq = max(80, min(2000, int(frequency_hz)))
        self.pwm.freq(freq)

        if waveform == "sine":
            duty_scale = 0.22
        elif waveform == "square":
            duty_scale = 0.42
        else:
            duty_scale = 0.30

        duty = int(65535 * amplitude * duty_scale)
        duty = max(0, min(32767, duty))
        self.pwm.duty_u16(duty)

    @staticmethod
    def _normalize_phrase(notes):
        clean = []
        for note in notes or []:
            try:
                duration = max(0.05, min(3.0, float(note.get("duration_s", 0.25))))
                velocity = max(0.0, min(1.0, float(note.get("velocity", 0.5))))
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
