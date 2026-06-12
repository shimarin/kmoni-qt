#!/usr/bin/env python3
"""強震モニタ Qt6 WebEngine ビューア"""

import os
import socket
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn

# QApplication 生成前にChromiumフラグを設定（オーディオ自動再生を許可）
os.environ.setdefault(
    "QTWEBENGINE_CHROMIUM_FLAGS",
    "--autoplay-policy=no-user-gesture-required",
)

import requests
from PyQt6.QtCore import QUrl
from PyQt6.QtWebEngineCore import QWebEngineSettings
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import QApplication, QMainWindow

TARGET = "http://www.kmoni.bosai.go.jp"
SESSION = requests.Session()

INJECT_STYLE = b"""<style>
#loading, #header,
#main-layerctrl, #main-infolink-ctrl,
#main-smallmessage, #main-message,
#main-timectrl, #footer { display: none !important; }
body { margin: 0; padding: 0; background: #000; overflow: hidden; }
div#main-map { position: relative !important; overflow: hidden !important; }
div#main-map img:not(#map-scale) {
    position: absolute !important; top: 0 !important; left: 0 !important;
}
#map-scale {
    position: absolute !important;
    top: 101px !important;
    left: 305px !important;
}
::-webkit-scrollbar { display: none; }
</style>"""


def patch_html(content: bytes) -> bytes:
    tag = b"</head>"
    pos = content.lower().find(tag)
    if pos != -1:
        return content[:pos] + INJECT_STYLE + content[pos:]
    return content + INJECT_STYLE


class ProxyHandler(BaseHTTPRequestHandler):
    def do_request(self):
        target_url = TARGET + self.path
        headers = {k: v for k, v in self.headers.items()
                   if k.lower() not in ("host", "connection")}
        headers["Host"] = "www.kmoni.bosai.go.jp"

        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length > 0 else None

        last_exc = None
        for attempt in range(3):
            try:
                resp = SESSION.request(
                    method=self.command,
                    url=target_url,
                    headers=headers,
                    data=body,
                    allow_redirects=False,
                    stream=True,
                    timeout=30,
                )
                body_bytes = resp.content
                content_type = resp.headers.get("Content-Type", "")
                if "text/html" in content_type:
                    body_bytes = patch_html(body_bytes)

                self.send_response(resp.status_code)
                for key, value in resp.headers.items():
                    if key.lower() not in ("transfer-encoding", "connection", "content-length"):
                        self.send_header(key, value)
                self.send_header("Content-Length", str(len(body_bytes)))
                self.end_headers()
                self.wfile.write(body_bytes)
                return
            except Exception as e:
                last_exc = e
                if attempt < 2:
                    time.sleep(0.5 * (attempt + 1))
        self.send_error(502, "Bad Gateway")

    do_GET = do_request
    do_POST = do_request
    do_PUT = do_request
    do_DELETE = do_request
    do_HEAD = do_request
    do_OPTIONS = do_request
    do_PATCH = do_request

    def log_message(self, fmt, *args):
        pass  # アクセスログを抑制


class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True


def start_proxy() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
    server = ThreadingHTTPServer(("127.0.0.1", port), ProxyHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return port


class MainWindow(QMainWindow):
    def __init__(self, port: int):
        super().__init__()
        self.setWindowTitle("強震モニタ")

        view = QWebEngineView()

        settings = view.page().settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.PlaybackRequiresUserGesture, False)
        settings.setAttribute(QWebEngineSettings.WebAttribute.AllowRunningInsecureContent, True)

        view.load(QUrl(f"http://127.0.0.1:{port}/"))
        self.setCentralWidget(view)
        self.resize(365, 415)


def main():
    port = start_proxy()

    app = QApplication(sys.argv)
    app.setApplicationName("kmoni-qt")
    app.setDesktopFileName("kmoni-qt")
    window = MainWindow(port)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
