import sys
import faulthandler
import sys

from qtmd.splitter import MultiSplitter

sys.dont_write_bytecode = True
faulthandler.enable()

import os

if getattr(sys, "frozen", False):
    if hasattr(sys, "_MEIPASS"):
        ROOT_PATH = sys._MEIPASS
    else:
        ROOT_PATH = os.path.dirname(os.path.realpath(sys.executable))
else:
    ROOT_PATH = os.path.dirname(os.path.realpath(__file__))


from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineCore import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWebChannel import *
import subprocess
import random

import qtmodern.styles
import qtmodern.windows

class TerminalWidget(QWebEngineView):

    def __init__(self, parent, command, theme="x", font_name="Monospace"):
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
    
    def set_win(self, window):
        self.main_window = window
    
    def print_title(self):
        if self.main_window is not None:
            self.main_window.setWindowTitle(f"{self.page().title()} at {self.port}")
    
    def spawn(self, port:int=9990):
        self.port = port
        self.session = subprocess.Popen(
            [os.path.join(ROOT_PATH, "bin", "pyuxterm"), f"--command={self.command}", f"--port={port}"],
            stdout = subprocess.PIPE, 
            stderr = subprocess.PIPE,
        )
        self.qurl = QUrl(f"http://127.0.0.1:{port}") 
        QTimer().singleShot(4000, self.loaded)

    def loaded(self):
        self.setUrl(self.qurl)
    
    def terminate(self):
        self.session.terminate()

class MainWindow(QMainWindow):
    
    PORT = random.randint(7000,65530)

    def __init__(self, parent = None):
        super().__init__(parent)
        
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        
        self.main_widget = QWidget(self)
        self.status_bar = QStatusBar(self)
        self.add_term_button = QPushButton("A")
        self.rem_term_button = QPushButton("R")

        self.div = MultiSplitter(self)

        self.emulator = TerminalWidget(self.div, "bash")
        self.emulator.spawn(self.PORT)
        
        #self.emulator2 = TerminalWidget(self.div, "python")
        #self.emulator2.spawn(self.PORT+2)

        #self.emulator3 = TerminalWidget(self.div, "node")
        #self.emulator3.spawn(self.PORT+44)
        
        #self.emulator4 = TerminalWidget(self.div, "sh")
        #self.emulator4.spawn(self.PORT+4)

        self.div.splitAt(None, 1, self.emulator)
        #self.div.splitAt(self.emulator, 3, self.emulator2)
        #self.div.splitAt(self.emulator2, 1, self.emulator3)
        #self.div.splitAt(self.emulator, 2, self.emulator4)

        self.layout.addWidget(self.div)
        self.main_widget.setLayout(self.layout)
        self.setCentralWidget(self.main_widget)
        self.setStatusBar(self.status_bar)

        self.resize(1000, 600)

        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

        self.setStyleSheet("""
        QSizeGrip {
            image: none;
            width: 16px;
            height: 16px;
        }
        """)

    def kill_term(self):
        self.emulator.terminate()

app = QApplication(sys.argv)
app.setApplicationName("UTERM")

window = MainWindow(None)

qtmodern.styles.dark(app)
mw = qtmodern.windows.ModernWindow(
    window,
    extra_buttons_left=[
        window.add_term_button,
        window.rem_term_button
        ]
    )
window.emulator.set_win(mw)
mw.show()

app.lastWindowClosed.connect(lambda: window.kill_term())
app.exec()