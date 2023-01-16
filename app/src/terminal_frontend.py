import os
import subprocess

import requests
from PySide6.QtCore import *
from PySide6.QtNetwork import *
from PySide6.QtWebChannel import *
from PySide6.QtWebEngineCore import *
from PySide6.QtWebEngineWidgets import *


class TerminalWidget(QWebEngineView):

    on_hand_event = Signal(object)

    @staticmethod
    def is_serving(url: str):
        try:
            head = requests.head(url)
            if head.status_code == 200:
                return True
            else:
                return False

        except requests.exceptions.RequestException as e:
            return None

    def __init__(self, parent, command, theme="default", font_name="Monospace", max_tries: int = 3):
        super().__init__(parent)
        self.command = command
        self.port = None
        self.theme = theme
        self.font_name = font_name
        self.max_tries = max_tries
        self.__url = None
        self.__loaded = False
        self.__load_tries = 0
        self.qurl = None
        self.session = None
        self.main_window = None
        self.loadFinished.connect(self.print_title)
        self.show()

    def set_window_api(self, window):
        self.main_window = window
        return self

    def print_title(self):
        if self.main_window is not None:
            self.main_window.setWindowTitle(
                f"{self.page().title()} at {self.port}")
        return self

    def spawn(self, port: int = 9990):
        self.port = port
        self.session = subprocess.Popen(
            [
                os.path.join(os.environ["QtxTermRootPath"], "bin", "pyuxterm"),
                f"--command={self.command}",
                f"--port={port}",  # f"--theme={self.theme}"
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.__url = f"http://127.0.0.1:{port}"
        self.qurl = QUrl(self.__url)
        QTimer().singleShot(4000, self.loaded)
        return self

    def loaded(self):
        if self.__load_tries <= self.max_tries:
            if self.is_serving(self.__url):
                self.__loaded = True
                self.setUrl(self.qurl)
                return self
            else:
                QTimer().singleShot(4000*self.__load_tries, self.loaded)

            self.__load_tries += 1

    def terminate(self):
        self.session.terminate()
        return self

    def enterEvent(self, event: QEvent) -> None:
        super().enterEvent(event)
        self.on_hand_event.emit(self)
        if self.main_window:
            self.main_window.setWindowTitle(
                f"{self.page().title()} at {self.port}")

    def send_post(self, data: QJsonDocument, request: QNetworkRequest) -> None:
        self.nam = QNetworkAccessManager()
        self.nam.finished.connect(lambda response: print(
            str(response.readAll(), 'utf-8')))

        self.nam.post(request, data)

    def send_input(self, text: str) -> None:
        if self.__loaded:
            json = {
                "eval": {
                    ">>>": "PtyInterface.input_(text=" + "'" + text + "'" + ")",
                    "async": False
                }
            }
            payload = QJsonDocument(json)

            url = f"{self.__url}/"
            request = QNetworkRequest(QUrl(url))
            request.setHeader(
                QNetworkRequest.ContentTypeHeader, "application/json")

            self.send_post(payload.toJson(), request)

        else:
            QTimer().singleShot(3600, lambda: self.send_input(text))