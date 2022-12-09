from functools import partial
import hjson
from PySide6.QtWidgets import *
from qtpy.QtGui import *

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
