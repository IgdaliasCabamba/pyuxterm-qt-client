import os
from PySide6.QtWidgets import *
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap


class PrimaryScreen(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.build()

    def build(self) -> None:
        self.vbox = QVBoxLayout(self)
        self.vbox.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.vbox)

        hbox1 = QHBoxLayout() 
        hbox1.setContentsMargins(0, 0, 0, 0)

        self.main_widget = QFrame(self)
        hbox1.addWidget(self.main_widget, Qt.AlignCenter)

        self.vbox_main = QHBoxLayout(self.main_widget) 
        self.vbox_main.setContentsMargins(0, 0, 0, 0)
        self.main_widget.setLayout(self.vbox_main)

        self.start_panel = QFrame(self)
        vbox_panel = QVBoxLayout(self.start_panel)
        vbox_panel.setContentsMargins(0, 0, 0, 0)
        self.start_panel.setLayout(vbox_panel)
        self.start_panel.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))

        self.btn_new_local_terminal = QPushButton(self)
        self.btn_new_local_terminal.setText("New local terminal")
        self.btn_new_local_terminal.setObjectName("AppButton")
        self.btn_new_local_terminal.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        
        hbox_panel1 = QHBoxLayout()
        hbox_panel1.setContentsMargins(0, 0, 0, 0)

        hbox_panel1.addWidget(self.btn_new_local_terminal, Qt.AlignCenter)

        vbox_panel.addLayout(hbox_panel1)

        self.vbox_main.addWidget(self.start_panel, Qt.AlignCenter)

        self.vbox.addLayout(hbox1)