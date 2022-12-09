import os
import subprocess
from PySide6.QtCore import *
from PySide6.QtWebEngineCore import *
from PySide6.QtWebEngineWidgets import *
from PySide6.QtWebChannel import *


class TerminalWidget(QWebEngineView):
    
    on_hand_event = Signal(object)

    def __init__(self, parent, command, theme="default", font_name="Monospace"):
        super().__init__(parent)
        self.command = command
        self.port = None
        self.theme = theme
        self.font_name = font_name
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
            self.main_window.setWindowTitle(f"{self.page().title()} at {self.port}")
        return self
    
    def spawn(self, port:int=9990):
        self.port = port
        self.session = subprocess.Popen(
            [
                os.path.join(os.environ["QtxTermRootPath"], "bin", "pyuxterm"),
                f"--command={self.command}",
                f"--port={port}", #f"--theme={self.theme}"
            ],
            stdout = subprocess.PIPE, 
            stderr = subprocess.PIPE,
        )
        self.qurl = QUrl(f"http://127.0.0.1:{port}") 
        QTimer().singleShot(4000, self.loaded)
        return self

    def loaded(self):
        self.setUrl(self.qurl)
        return self
    
    def terminate(self):
        self.session.terminate()
        return self
    
    def enterEvent(self, event:QEvent) -> None:
        super().enterEvent(event)
        self.on_hand_event.emit(self)
        self.main_window.setWindowTitle(f"{self.page().title()} at {self.port}")
