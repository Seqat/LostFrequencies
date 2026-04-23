import json
import socket
import time

import network

import config


class WiFiManager:
    def __init__(self):
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)
        self.last_attempt_ms = 0
        self.last_error = ""
        self._addr = None

    def ensure_connected(self):
        if self.wlan.isconnected():
            return True

        now = time.ticks_ms()
        if time.ticks_diff(now, self.last_attempt_ms) < config.WIFI_RETRY_MS:
            return False

        self.last_attempt_ms = now
        self.last_error = "connecting"
        try:
            self.wlan.connect(config.WIFI_SSID, config.WIFI_PASSWORD)
        except Exception as exc:
            self.last_error = "wifi err"
            self._addr = None
            return False
        return False

    def status_label(self):
        if self.wlan.isconnected():
            return "connected"
        return self.last_error or "offline"

    def post_json(self, payload):
        if not self.wlan.isconnected():
            raise OSError("wifi disconnected")

        if self._addr is None:
            self._addr = socket.getaddrinfo(config.BACKEND_HOST, config.BACKEND_PORT)[0][-1]

        body = json.dumps(payload)
        request = (
            "POST {path} HTTP/1.1\r\n"
            "Host: {host}:{port}\r\n"
            "Content-Type: application/json\r\n"
            "Connection: close\r\n"
            "Content-Length: {length}\r\n\r\n{body}"
        ).format(
            path=config.BACKEND_PATH,
            host=config.BACKEND_HOST,
            port=config.BACKEND_PORT,
            length=len(body),
            body=body,
        )

        sock = socket.socket()
        sock.settimeout(config.BACKEND_TIMEOUT_S)
        try:
            sock.connect(self._addr)
            sock.send(request.encode("utf-8"))
            chunks = []
            while True:
                data = sock.recv(512)
                if not data:
                    break
                chunks.append(data)
        except Exception:
            self._addr = None
            self.last_error = "backend err"
            raise
        finally:
            sock.close()

        raw = b"".join(chunks)
        if b"\r\n\r\n" not in raw:
            raise ValueError("bad response")
        header, body = raw.split(b"\r\n\r\n", 1)
        if b"200" not in header.splitlines()[0]:
            raise ValueError("backend status")
        self.last_error = ""
        return json.loads(body.decode("utf-8"))
