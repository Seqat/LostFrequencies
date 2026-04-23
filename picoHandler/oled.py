from machine import I2C, Pin

import config
from ssd1306 import SSD1306_I2C


class OLEDStatus:
    def __init__(self):
        self.i2c = I2C(0, sda=Pin(config.I2C_SDA), scl=Pin(config.I2C_SCL), freq=config.I2C_FREQ)
        self.display = None
        self._last_state = None
        try:
            self._init_display()
        except OSError:
            self.display = None

    def _init_display(self):
        self.display = SSD1306_I2C(config.OLED_WIDTH, config.OLED_HEIGHT, self.i2c, addr=0x3C)

    def render(self, wifi_status, backend_status, station_freq, mood_depth, label, play_state):
        if self.display is None:
            try:
                self._init_display()
            except OSError:
                return

        connected = wifi_status == "connected"
        state = (
            connected,
            self._fit(wifi_status, 10),
            self._fit(backend_status, 10),
            round(station_freq, 1),
            round(mood_depth, 2),
            self._fit(label, 16),
            self._fit(play_state, 16),
        )
        if state == self._last_state:
            return

        try:
            if connected:
                self._draw_main_screen(state)
            else:
                self._draw_status_screen(state)
            self._last_state = state
        except OSError:
            # I2C OLEDs can briefly timeout during noisy updates; retry once and
            # keep the rest of the controller alive.
            self._last_state = None
            try:
                self._init_display()
                if connected:
                    self._draw_main_screen(state)
                else:
                    self._draw_status_screen(state)
                self._last_state = state
            except OSError:
                self.display = None
                return

    def _draw_status_screen(self, state):
        _, wifi_status, backend_status, station_freq, mood_depth, label, play_state = state
        d = self.display
        d.fill(0)
        d.text("LOSTFREQUENCIES", 0, 0)
        d.text("WiFi:{}".format(wifi_status), 0, 14)
        d.text("API :{}".format(backend_status), 0, 26)
        d.text("Tune:{:.1f}".format(station_freq), 0, 40)
        d.text(self._fit(play_state, 16), 0, 52)
        d.show()

    def _draw_main_screen(self, state):
        _, _, backend_status, station_freq, mood_depth, label, play_state = state
        d = self.display
        d.fill(0)
        d.text("FM FREQUENCY", 18, 0)

        track_left = 8
        track_right = 120
        track_y = 18
        track_w = track_right - track_left
        d.hline(track_left, track_y, track_w, 1)
        for index in range(0, 17):
            x = track_left + int((track_w * index) / 16)
            tick_h = 8 if index in (0, 4, 8, 12, 16) else 4
            d.vline(x, track_y - 2, tick_h, 1)

        freq_ratio = (station_freq - config.FM_FREQ_MIN) / (config.FM_FREQ_MAX - config.FM_FREQ_MIN)
        freq_ratio = max(0.0, min(1.0, freq_ratio))
        pointer_x = track_left + int(track_w * freq_ratio)
        d.vline(pointer_x, track_y - 4, 14, 1)
        d.line(pointer_x - 3, track_y - 6, pointer_x, track_y - 2, 1)
        d.line(pointer_x + 3, track_y - 6, pointer_x, track_y - 2, 1)

        d.text(str(int(config.FM_FREQ_MIN)), 4, 28)
        d.text("{:.1f}".format(station_freq), 46, 28)
        d.text(str(int(config.FM_FREQ_MAX)), 98, 28)

        d.text(self._fit(label.upper(), 12), 18, 40)
        bar_x = 10
        bar_y = 54
        bar_w = 108
        bar_h = 8
        fill_w = int((bar_w - 2) * max(0.0, min(1.0, mood_depth)))
        d.rect(bar_x, bar_y, bar_w, bar_h, 1)
        if fill_w > 0:
            d.fill_rect(bar_x + 1, bar_y + 1, fill_w, bar_h - 2, 1)
        d.show()

    @staticmethod
    def _fit(value, limit):
        text = str(value or "")
        return text[:limit]
