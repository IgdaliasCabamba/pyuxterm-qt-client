from utils import *
from terminal_widget import *
from qtmd.splitter import MultiSplitter
from qtmd.qgithubbutton import QGithubButton
import qtmodern.windows
import qtmodern.styles
from PySide6.QtWidgets import *
from PySide6.QtWebEngineWidgets import *
from PySide6.QtWebEngineCore import *
from PySide6.QtWebChannel import *
from PySide6.QtGui import *
from PySide6.QtCore import *
from weakref import ref
import random
import os
import faulthandler
import sys

sys.dont_write_bytecode = True
faulthandler.enable()


os.environ["QT_API"] = "pyside6"
os.environ["QT_QPA_PLATFORM"] = "xcb"  # Wayland scale issue


if getattr(sys, "frozen", False):
    if hasattr(sys, "_MEIPASS"):
        ROOT_PATH = sys._MEIPASS
    else:
        ROOT_PATH = os.path.dirname(os.path.realpath(sys.executable))
else:
    ROOT_PATH = os.path.dirname(os.path.realpath(__file__))

os.environ["QtxTermRootPath"] = ROOT_PATH

with open(os.path.join(ROOT_PATH, "resources", "style.qss"), "r") as fp:
    STYLE_SHEET = fp.read()

with open(os.path.join(ROOT_PATH, "settings.json"), "r") as fp:
    QTXTERM_SETTINGS = hjson.load(fp)


class MainWindow(QMainWindow):

    def __init__(self, parent=None, qapp=None):
        super().__init__(parent)
        self.terminals = {}
        self.terminals_json_api = TerminalsJsonApi(
            os.path.join(ROOT_PATH, "terminals.json"))
        self.current_terminal_emulator = self.terminals_json_api.current
        self.index = 0
        self.modern_window = None
        self.terminal_menu = TermBinsMenu(self)
        self.split_menu = TermSplitMenu(self)
        self._current_terminal_view = None
        self.qapp = qapp
        self.qapp.focusChanged.connect(self._app_focus_changed)
        self.qapp.lastWindowClosed.connect(self.kill_app)

        self.PORT = lambda: random.randint(7000, 65530)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(2, 0, 2, 0)

        self.main_widget = QWidget(self)
        self.status_bar = QStatusBar(self)

        self.add_term_button = QPushButton()
        self.add_term_button.clicked.connect(self.add_terminal)
        self.add_term_button.setObjectName("TermButton")
        self.add_term_button.setIcon(QIcon(
            os.path.join(ROOT_PATH, "resources", "icons",
                         "icons8-plus-math-48.png")
        ))

        self.term_picker = QToolButton(self)
        self.term_picker.setMenu(self.terminal_menu)
        self.term_picker.setObjectName("TermButton")
        self.term_picker.setProperty("min", True)
        self.term_picker.setIcon(QIcon(
            os.path.join(ROOT_PATH, "resources", "icons",
                         "icons8-expand-arrow-16.png")
        ))
        self.term_picker.clicked.connect(lambda: self.term_picker.showMenu())
        self.term_picker.setMaximumSize(16, 16)

        self.splitter_options = QPushButton()
        self.splitter_options.setMenu(self.split_menu)
        self.splitter_options.setObjectName("TermButton")
        self.splitter_options.setIcon(QIcon(
            os.path.join(ROOT_PATH, "resources", "icons",
                         "icons8-columns-48.png")
        ))
        self.splitter_options.clicked.connect(
            lambda: self.splitter_options.showMenu())

        self.rem_term_button = QPushButton()
        self.rem_term_button.clicked.connect(self.kill_term)
        self.rem_term_button.setIcon(QIcon(
            os.path.join(ROOT_PATH, "resources",
                         "icons", "icons8-trash-48.png")
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
            os.path.join(ROOT_PATH, "resources", "icons",
                         "icons8-settings-48.png")
        ))
        self.cfg_term_button.setObjectName("TermNavItem")

        self.div = MultiSplitter(self)
        self.div.setObjectName("Splitter")
        self.div.set_opaque_resize(True)

        self.layout.addWidget(self.div)
        #self.status_bar.addWidget(QLabel(str(os.getcwd())))
        self.status_bar.addPermanentWidget(QLabel("CPU: 100%"))
        self.main_widget.setLayout(self.layout)
        self.setCentralWidget(self.main_widget)
        self.setStatusBar(self.status_bar)

        self.resize(1000, 600)

        qtRectangle = self.frameGeometry()
        centerPoint = QGuiApplication.primaryScreen().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())
        self.initial_opening()

    def initial_opening(self):
        self._new_terminal(self.current_terminal_emulator["bin"], None, 0)

    def split_new_terminal(self, orientation: int) -> None:
        self._new_terminal(
            self.current_terminal_emulator["bin"], self._current_terminal_view, orientation)

    def add_terminal(self) -> None:
        self._new_terminal(self.current_terminal_emulator["bin"], None, 0)

    def _new_terminal(self, command, widget_ref, orientation):
        self.terminals[self.index] = ((
            TerminalWidget(self.div, command)
            .spawn(self.PORT())
        ))
        if self.index == 0:
            self.div.splitAt(widget_ref, orientation,
                             self.terminals[self.index])
        else:
            self.div.splitAt(widget_ref, orientation,
                             self.terminals[self.index])

        self._current_terminal_view = self.terminals[self.index]
        self._current_terminal_view.on_hand_event.connect(
            self.set_current_terminal_view)
        self._set_window_api(self.modern_window)

        for args in self.current_terminal_emulator.get("run", []):
            self._current_terminal_view.send_input(args)

        self.index += 1

    def select_terminal(self, term_data: dict):
        self.current_terminal_emulator = term_data

    def kill_term(self):
        for idx, term in self.terminals.items():
            if term == self._current_terminal_view:
                self.terminals.pop(idx)
                term.close()
                term.deleteLater()
                terminals = self.terminals.values()
                if terminals:
                    self._current_terminal_view = terminals[0]
                else:
                    self._current_terminal_view = None
                break

    def kill_app(self) -> None:
        for term in self.terminals.values():
            term.terminate()

    def set_modern_window(self, modern_window) -> None:
        self.modern_window = modern_window
        self._set_window_api(modern_window)

    def _set_window_api(self, modern_window) -> None:
        for term in self.terminals.values():
            term.set_window_api(modern_window)

    def _app_focus_changed(self, _, new):
        if isinstance(new, TerminalWidget) and new in self.terminals.values():
            self._current_terminal_view = new

    def set_current_terminal_view(self, terminal_view: TerminalWidget):
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
        window.splitter_options,
        window.rem_term_button,
        window.cfg_term_button
    ]
)
window.set_modern_window(mw)
mw.show()

app.setStyleSheet(STYLE_SHEET)
window.setStyleSheet(STYLE_SHEET)

app.exec()