import sys
import faulthandler

sys.dont_write_bytecode = True
faulthandler.enable()

import os
from weakref import ref
from functools import partial
from qtmd.splitter import MultiSplitter
from qtmd.qgithubbutton import QGithubButton
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineCore import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWebChannel import *
import subprocess
import random
import hjson

import qtmodern.styles
import qtmodern.windows

if getattr(sys, "frozen", False):
    if hasattr(sys, "_MEIPASS"):
        ROOT_PATH = sys._MEIPASS
    else:
        ROOT_PATH = os.path.dirname(os.path.realpath(sys.executable))
else:
    ROOT_PATH = os.path.dirname(os.path.realpath(__file__))

with open(os.path.join(ROOT_PATH, "resources", "style.qss"), "r") as fp:
    STYLE_SHEET = fp.read()

with open(os.path.join(ROOT_PATH, "settings.json"), "r") as fp:
    QTXTERM_SETTINGS = hjson.load(fp)


class TerminalWidget(QWebEngineView):
    
    on_hand_event = pyqtSignal(object)

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
                os.path.join(ROOT_PATH, "bin", "pyuxterm"),
                f"--command={self.command}",
                f"--port={port}", f"--theme={self.theme}"
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

class TermBinsMenu(QMenu):
    def __init__(self, parent):
        super().__init__(parent)
        self.api_terminals = self.parent().terminals_json_api
        self.build()

    def build(self):
        group_mode = QActionGroup(self)

        current_terminal = self.api_terminals.current

        self.setTitle("Terminals")
        self.setToolTip("Pick a terminal")

        for terminal in self.api_terminals.all:
            action = QAction(terminal["name"], self)
            action.setCheckable(True)

            if terminal["id"] == current_terminal["id"]:
                action.setChecked(True)

            action.triggered.connect(partial(self.parent().select_terminal, terminal))
            self.addAction(action)
            group_mode.addAction(action)

class TerminalsJsonApi:
    def __init__(self, file):
        with open(file, "r") as fp:
            self.json_content = hjson.load(fp)
    
    @property
    def current(self):
        id_current = self.json_content["current"]
        for terminal in self.json_content["emulators"]:
            if terminal["id"] == id_current:
                return terminal
    @property
    def all(self):
        return self.json_content["emulators"]

class MainWindow(QMainWindow):

    def __init__(self, parent = None, qapp=None):
        super().__init__(parent)
        self.terminals = {}
        self.terminals_json_api = TerminalsJsonApi(os.path.join(ROOT_PATH, "terminals.json"))
        self.current_terminal_emulator = self.terminals_json_api.current
        self.index = 0
        self.modern_window = None
        self.terminal_menu = TermBinsMenu(self)
        self._current_terminal_view = None
        self.qapp = qapp
        self.qapp.focusChanged.connect(self._app_focus_changed)
        self.qapp.lastWindowClosed.connect(self.kill_app)
        
        self.PORT = lambda: random.randint(7000,65530)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        
        self.main_widget = QWidget(self)
        self.status_bar = QStatusBar(self)
        
        self.add_term_button = QPushButton()
        self.add_term_button.clicked.connect(self.add_terminal)
        self.add_term_button.setObjectName("TermButton")
        self.add_term_button.setIcon(QIcon(
            os.path.join(ROOT_PATH, "resources", "icons", "icons8-plus-math-48.png")
        ))
        
        self.term_picker = QToolButton(self)
        self.term_picker.setMenu(self.terminal_menu)
        self.term_picker.setObjectName("TermButton")
        self.term_picker.setProperty("min", True)
        self.term_picker.setIcon(QIcon(
            os.path.join(ROOT_PATH, "resources", "icons", "icons8-expand-arrow-16.png")
        ))
        self.term_picker.clicked.connect(lambda: self.term_picker.showMenu())
        self.term_picker.setMaximumSize(16,16)

        self.rem_term_button = QPushButton()
        self.rem_term_button.clicked.connect(self.kill_term)
        self.rem_term_button.setIcon(QIcon(
            os.path.join(ROOT_PATH, "resources", "icons", "icons8-trash-48.png")
        ))
        self.rem_term_button.setObjectName("TermNavItem")
        
        self.term_ghbtn = QGithubButton(self)
        self.term_ghbtn.setObjectName("TermNavItem")
        self.term_ghbtn.setProperty("min", True)
        self.term_ghbtn.set_widget_primary(self.add_term_button)
        self.term_ghbtn.set_widget_secondary(self.term_picker)

        self.cfg_term_button = QPushButton()
        self.cfg_term_button.clicked.connect(self.open_settings)
        self.cfg_term_button.setIcon(QIcon(
            os.path.join(ROOT_PATH, "resources", "icons", "icons8-settings-48.png")
        ))
        self.cfg_term_button.setObjectName("TermNavItem")

        self.div = MultiSplitter(self)
        self.div.setObjectName("Splitter")
        self.div.set_opaque_resize(False)

        self.layout.addWidget(self.div)
        self.main_widget.setLayout(self.layout)
        self.setCentralWidget(self.main_widget)
        self.setStatusBar(self.status_bar)

        self.resize(1000, 600)

        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())
        self.initial_opening()
    
    def initial_opening(self):
        self._new_terminal(self.current_terminal_emulator["bin"], None, 0)
    
    def split_new_terminal(self, orientation):
        """Split new terminal from another"""
        pass

    def add_terminal(self):
        self._new_terminal(self.current_terminal_emulator["bin"], None, 0)
    
    def _new_terminal(self, command, widget_ref, orientation):
        self.terminals[self.index] = ((
            TerminalWidget(self.div, command)
            .spawn(self.PORT())
        ))
        if self.index == 0:
            self.div.splitAt(widget_ref, orientation, self.terminals[self.index])
        else:
            self.div.splitAt(widget_ref, orientation, self.terminals[self.index])
        
        self._current_terminal_view = self.terminals[self.index]
        self._current_terminal_view.on_hand_event.connect(self.set_current_terminal_view)
        self._set_window_api(self.modern_window)

        self.index += 1
    
    def select_terminal(self, term_data:dict):
        self.current_terminal_emulator = term_data
    
    def kill_term(self):
        for idx, term in self.terminals.items():
            if term == self._current_terminal_view:
                self.terminals.pop(idx)
                term.close()
                term.deleteLater()
                break

    def kill_app(self) -> None:
        for term in self.terminals.values():
            term.terminate()
    
    def set_modern_window(self, modern_window)  -> None:
        self.modern_window = modern_window
        self._set_window_api(modern_window)
    
    def _set_window_api(self, modern_window)  -> None:
        for term in self.terminals.values():
            term.set_window_api(modern_window)

    def _app_focus_changed(self, _, new):
        if isinstance(new, TerminalWidget) and new in self.terminals.values():
            self._current_terminal_view = new
    
    def set_current_terminal_view(self, terminal_view:TerminalWidget):
        self._current_terminal_view = terminal_view
    
    def open_settings(self):
        editor = os.getenv('EDITOR')
        filename = os.path.join(ROOT_PATH, "settings.json")
        if editor:
            subprocess.Popen([editor, filename])
        else:
            subprocess.Popen(["xdg-open", filename])

app = QApplication(sys.argv)
app.setApplicationName("UTERM")

window = MainWindow(None, app)

if QTXTERM_SETTINGS["app-theme"] == "light":
    qtmodern.styles.light(app)
else:
    qtmodern.styles.dark(app)

mw = qtmodern.windows.ModernWindow(
    window,
    extra_buttons_left=[
        window.term_ghbtn,
        window.rem_term_button,
        window.cfg_term_button
        ]
    )
window.set_modern_window(mw)
mw.show()

app.setStyleSheet(STYLE_SHEET)
window.setStyleSheet(STYLE_SHEET)

app.exec()