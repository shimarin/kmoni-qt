#!/usr/bin/env python3
"""強震モニタ Qt6 WebEngine ビューア"""

import os
import sys

# QApplication 生成前にChromiumフラグを設定（オーディオ自動再生を許可）
os.environ.setdefault(
    "QTWEBENGINE_CHROMIUM_FLAGS",
    "--autoplay-policy=no-user-gesture-required",
)

from PyQt6.QtCore import QUrl
from PyQt6.QtWebEngineCore import QWebEngineScript, QWebEngineSettings
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import QApplication, QMainWindow

TARGET = "http://www.kmoni.bosai.go.jp/"

INJECT_JS_HIDE = "document.documentElement.style.visibility = 'hidden';"

INJECT_JS_STYLE = """(function() {
    var s = document.createElement('style');
    s.textContent = `
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
    `;
    document.head.appendChild(s);
    document.documentElement.style.visibility = '';
})();"""


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("強震モニタ")

        view = QWebEngineView()

        settings = view.page().settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.PlaybackRequiresUserGesture, False)
        settings.setAttribute(QWebEngineSettings.WebAttribute.AllowRunningInsecureContent, True)

        scripts = view.page().scripts()

        hide = QWebEngineScript()
        hide.setName("kmoni-hide")
        hide.setInjectionPoint(QWebEngineScript.InjectionPoint.DocumentCreation)
        hide.setWorldId(QWebEngineScript.ScriptWorldId.MainWorld)
        hide.setSourceCode(INJECT_JS_HIDE)
        scripts.insert(hide)

        style = QWebEngineScript()
        style.setName("kmoni-style")
        style.setInjectionPoint(QWebEngineScript.InjectionPoint.DocumentReady)
        style.setWorldId(QWebEngineScript.ScriptWorldId.MainWorld)
        style.setSourceCode(INJECT_JS_STYLE)
        scripts.insert(style)

        view.load(QUrl(TARGET))
        self.setCentralWidget(view)
        self.resize(365, 415)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("kmoni-qt")
    app.setDesktopFileName("kmoni-qt")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
