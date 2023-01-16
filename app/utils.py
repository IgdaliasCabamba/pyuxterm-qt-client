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

class TermSplitMenu(QMenu):
    SPLIT_MAP = {
        "up":{
            "orientation":0,
            "text": "Split Up"
            },
        "down":{
            "orientation":1,
            "text": "Split Down"
            },
        "left":{
            "orientation":2,
            "text": "Split Left"
            },
        "right":{
            "orientation":3,
            "text": "Split Right"
            },
    }
    def __init__(self, parent):
        super().__init__(parent)
        self.build()

    def build(self):
        self.setTitle("Split")
        self.setToolTip("Split New Terminal")

        for key, split_option in self.SPLIT_MAP.items():
            action = QAction(split_option["text"], self)
            orientation = split_option["orientation"]

            action.triggered.connect(partial(self.parent().split_new_terminal, orientation))
            self.addAction(action)


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
