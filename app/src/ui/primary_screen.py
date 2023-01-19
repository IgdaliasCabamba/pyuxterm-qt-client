import os
from PySide6.QtWidgets import *
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
import qtawesome as qta


class Home(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.build()

    def build(self) -> None:
        self.vbox = QHBoxLayout(self)
        self.vbox.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.vbox)

        self.start_panel = QFrame(self)
        self.start_panel.setMinimumWidth(300)
        self.vbox_panel = QVBoxLayout(self.start_panel)
        self.vbox_panel.setContentsMargins(0, 0, 0, 0)
        self.start_panel.setLayout(self.vbox_panel)
        self.start_panel.setSizePolicy(QSizePolicy(
            QSizePolicy.Fixed, QSizePolicy.Fixed))

        self.user_panel = QFrame(self)
        vbox_user_panel = QVBoxLayout(self.user_panel)
        vbox_user_panel.setContentsMargins(5, 5, 5, 5)
        self.user_panel.setLayout(vbox_user_panel)

        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("password")
        vbox_user_panel.addWidget(self.password_input)
        self.vbox_panel.addWidget(self.user_panel)

        self.btn_new_terminal = QPushButton(self)
        self.btn_new_terminal.setText("New terminal")
        self.btn_new_terminal.setObjectName("AppButtonPrimary")

        self.btn_install_distro = QPushButton(self)
        self.btn_install_distro.setText("Install")
        self.btn_install_distro.setIcon(qta.icon('fa5s.download', options=[
                                        {'scale_factor': 1}], color='white'))
        self.btn_install_distro.setObjectName("AppButtonSecondary")

        hbox_panel1 = QHBoxLayout()
        hbox_panel1.setContentsMargins(5, 0, 5, 0)

        hbox_panel1.addWidget(self.btn_new_terminal, Qt.AlignCenter)
        hbox_panel1.addWidget(self.btn_install_distro, Qt.AlignCenter)

        self.vbox_panel.addLayout(hbox_panel1)

        self.vbox.addWidget(self.start_panel)


class PrimaryScreen(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.build()

    def build(self) -> None:
        self.box = QStackedLayout(self)
        self.box.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.box)

        self.home = Home(self)
        self.btn_new_terminal = self.home.btn_new_terminal

        self.box.addWidget(self.home)
        self.box.setCurrentWidget(self.home)