import os
from . import *
from qtmd.splitter import MultiSplitter
from qtmd.qgithubbutton import QGithubButton
from PySide6.QtWidgets import *
from PySide6.QtWebEngineWidgets import *
from PySide6.QtWebEngineCore import *
from PySide6.QtWebChannel import *
from PySide6.QtGui import *
from PySide6.QtCore import *
import subprocess

from enum import Enum


class MainWindow(QMainWindow):

    class VIEWS(Enum):
        HOME = 0
        TERMINALS = 1
    
    @property
    def password(self):
        return self.__password
    
    @password.setter
    def password(self, password:str):
        self.__password = password
    
    def set_password(self, password:str) -> None:
        self.password = password

    def __init__(self, parent, qapp, emulators_file:str, port_creator:object):
        super().__init__(parent)
        self.__password = None
        self.terminals = dict()
        self.terminals_json_api = TerminalsJsonApi(emulators_file)
        self.current_screen = self.VIEWS.HOME
        self.current_terminal_emulator = self.terminals_json_api.current
        self.index = 0
        self.modern_window = None
        self.terminal_menu = TermBinsMenu(self)
        self.split_menu = TermSplitMenu(self)
        self._current_terminal_view = None
        self.qapp = qapp
        self.PORT = port_creator
        (self.build()
         .listen_events())

    def build(self) -> "MainWindow":

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(2, 0, 2, 0)

        self.main_widget = QWidget(self)
        self.status_bar = StatusBar(self)

        self.create_new_terminal_button = QPushButton()
        self.create_new_terminal_button.setObjectName("TermButton")
        self.create_new_terminal_button.setIcon(QIcon(
            os.path.join(os.environ["QtxTermRootPath"], "resources", "icons",
                         "icons8-plus-math-48.png")
        ))

        self.terminal_emulator_menu_button = QToolButton(self)
        self.terminal_emulator_menu_button.setMenu(self.terminal_menu)
        self.terminal_emulator_menu_button.setObjectName("TermButton")
        self.terminal_emulator_menu_button.setProperty("min", True)
        self.terminal_emulator_menu_button.setIcon(QIcon(
            os.path.join(os.environ["QtxTermRootPath"], "resources", "icons",
                         "icons8-expand-arrow-16.png")
        ))
        self.terminal_emulator_menu_button.setMaximumSize(16, 16)

        self.show_split_new_terminal_menu = QPushButton()
        self.show_split_new_terminal_menu.setMenu(self.split_menu)
        self.show_split_new_terminal_menu.setObjectName("TermButton")
        self.show_split_new_terminal_menu.setIcon(QIcon(
            os.path.join(os.environ["QtxTermRootPath"], "resources", "icons",
                         "icons8-columns-48.png")
        ))

        self.remove_current_terminal_button = QPushButton()
        self.remove_current_terminal_button.setIcon(QIcon(
            os.path.join(os.environ["QtxTermRootPath"], "resources",
                         "icons", "icons8-trash-48.png")
        ))
        self.remove_current_terminal_button.setObjectName("TermNavItem")

        self.new_terminal_buttons = QGithubButton(self)
        self.new_terminal_buttons.setObjectName("TermNavItem")
        self.new_terminal_buttons.setProperty("min", True)
        self.new_terminal_buttons.set_widget_primary(
            self.create_new_terminal_button)
        self.new_terminal_buttons.set_widget_secondary(
            self.terminal_emulator_menu_button)

        self.open_settings_file_button = QPushButton()
        self.open_settings_file_button.setIcon(QIcon(
            os.path.join(os.environ["QtxTermRootPath"], "resources", "icons",
                         "icons8-settings-48.png")
        ))
        self.open_settings_file_button.setObjectName("TermNavItem")

        self.toggle_screens_button = QPushButton()
        self.toggle_screens_button.setIcon(QIcon(
            os.path.join(os.environ["QtxTermRootPath"], "resources", "icons",
                         "icons8-console-48.png")
        ))
        self.toggle_screens_button.setObjectName("TermNavItem")

        self.home_screen = PrimaryScreen(self)
        self.home_screen.setObjectName("HomeScreen")

        self.div = MultiSplitter(self)
        self.div.setObjectName("Splitter")
        self.div.set_opaque_resize(True)
        self.div.setVisible(False)

        self.layout.addWidget(self.home_screen)
        self.layout.addWidget(self.div)
        self.main_widget.setLayout(self.layout)
        self.setCentralWidget(self.main_widget)
        self.setStatusBar(self.status_bar)
        self.resize(1000, 600)

        qtRectangle = self.frameGeometry()
        centerPoint = QGuiApplication.primaryScreen().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())
        return self

    def listen_events(self) -> "MainWindow":
        self.create_new_terminal_button.clicked.connect(self.add_terminal)
        self.terminal_emulator_menu_button.clicked.connect(
            lambda: self.terminal_emulator_menu_button.showMenu())
        self.show_split_new_terminal_menu.clicked.connect(
            lambda: self.show_split_new_terminal_menu.showMenu())
        self.remove_current_terminal_button.clicked.connect(self.kill_term)
        self.open_settings_file_button.clicked.connect(self.open_settings)
        self.toggle_screens_button.clicked.connect(self.toggle_screens)

        self.qapp.focusChanged.connect(self._app_focus_changed)
        self.qapp.lastWindowClosed.connect(self.kill_app)

        self.home_screen.home.on_password_changed.connect(self.set_password)
        self.home_screen.new_terminal_btn.clicked.connect(
            self.add_terminal)
            
        return self

    def change_screen(self, **kwargs) -> None:
        if kwargs.get("home", False):
            if self.div.isVisible():
                self.div.setVisible(False)

            if not self.home_screen.isVisible():
                self.home_screen.setVisible(True)

            self.current_screen = self.VIEWS.HOME

            self.toggle_screens_button.setIcon(QIcon(
                os.path.join(os.environ["QtxTermRootPath"], "resources", "icons",
                             "icons8-console-48.png")
            ))

        elif kwargs.get("terminals", False):
            if self.home_screen.isVisible():
                self.home_screen.setVisible(False)

            if not self.div.isVisible():
                self.div.setVisible(True)

            self.current_screen = self.VIEWS.TERMINALS

            self.toggle_screens_button.setIcon(QIcon(
                os.path.join(os.environ["QtxTermRootPath"], "resources", "icons",
                             "icons8-home-48.png")
            ))
        
    def split_new_terminal(self, orientation: int) -> "MainWindow":
        self._new_terminal(
            self.current_terminal_emulator["bin"], self._current_terminal_view, orientation)
        return self

    def add_terminal(self) -> "MainWindow":
        self._new_terminal(self.current_terminal_emulator["bin"], None, 0)
        return self

    def _new_terminal(self, command, widget_ref, orientation) -> None:
        self.change_screen(terminals=True)
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

    def select_terminal(self, term_data: dict) -> None:
        self.current_terminal_emulator = term_data

    def kill_term(self) -> None:
        for idx, term in self.terminals.items():
            if term == self._current_terminal_view:
                self.terminals.pop(idx)
                term.close()
                term.deleteLater()
                if (idx-1) >= 0:
                    self._current_terminal_view = self.terminals[idx-1]
                else:
                    self.change_screen(home=True)
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

    def _app_focus_changed(self, _, new) -> None:
        if isinstance(new, TerminalWidget) and new in self.terminals.values():
            self._current_terminal_view = new

    def set_current_terminal_view(self, terminal_view: TerminalWidget) -> None:
        self._current_terminal_view = terminal_view

    def open_settings(self) -> None:
        editor = os.getenv('EDITOR')
        filename = os.path.join(
            os.environ["QtxTermRootPath"], "data", "settings.json")
        if editor:
            subprocess.Popen([editor, filename])
        else:
            subprocess.Popen(["xdg-open", filename])

    def toggle_screens(self):
        if self.current_screen == self.VIEWS.HOME:
            self.change_screen(terminals = True)
        
        elif self.current_screen == self.VIEWS.TERMINALS:
            self.change_screen(home = True)