import os
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest
import qtawesome as qta
import sh
from sarge import capture_stdout
from ..thread_manager import ChellyQThreadManager
import webbrowser


class MorePage(QFrame):

    class WidgetModel(QFrame):
        def __init__(self, parent, icon_name: str = None, legend_text: str = None, open_btn_text: str = None, open_btn_link: str = None):
            super().__init__(parent)
            self.icon_name = icon_name
            self.legend_text = legend_text
            self.open_btn_text = open_btn_text
            self.open_btn_link = open_btn_link
            self.setStyleSheet("WidgetModel { border-radius: 15px }")
            self.build()

        def build(self):
            self.hbox = QHBoxLayout(self)
            self.hbox.setContentsMargins(0, 0, 0, 0)
            self.setLayout(self.hbox)

            self.icon = QPushButton(self)
            self.icon.setObjectName("AppButtonIcon")
            self.icon.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding))
            self.icon.setIcon(qta.icon(self.icon_name, options=[{'scale_factor': 1}], color='white'))
            self.icon.setIconSize(QSize(64, 64))

            self.legend_lbl = QLabel(self)
            self.legend_lbl.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
            self.legend_lbl.setAlignment(Qt.AlignCenter)
            self.legend_lbl.setWordWrap(True)
            self.legend_lbl.setText(self.legend_text)

            self.open_btn = QPushButton(self)
            self.open_btn.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding))
            self.open_btn.setText(self.open_btn_text)
            self.open_btn.setObjectName("AppButtonPrimary-rounded_0")
            self.open_btn.setStyleSheet("border-top-right-radius: 15px; border-bottom-right-radius: 15px;")

            self.hbox.addWidget(self.icon)
            self.hbox.addWidget(self.legend_lbl)
            self.hbox.addWidget(self.open_btn)

            self.open_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(self.open_btn_link)))


    def __init__(self, parent):
        super().__init__(parent)
        self.build()

    def build(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)
        self.scroll_area = QScrollArea(self)

        self.main_widget = QFrame(self)
        self.vbox = QVBoxLayout(self.main_widget)
        self.vbox.setContentsMargins(100, 10, 100, 10)
        self.main_widget.setLayout(self.vbox)

        header_hbox = QHBoxLayout()
        header_hbox.setContentsMargins(0, 0, 0, 0)
        self.nav_back_btn = QPushButton(self.main_widget)
        self.nav_back_btn.setText("Back")
        self.nav_back_btn.setSizePolicy(QSizePolicy(
            QSizePolicy.Fixed, QSizePolicy.Fixed))
        self.nav_back_btn.setIcon(qta.icon('ri.arrow-left-s-line', options=[
            {'scale_factor': 1.8}], color='white'))
        self.nav_back_btn.setObjectName("AppButtonPrimary")
        header_hbox.setAlignment(Qt.AlignLeft)
        header_hbox.addWidget(self.nav_back_btn, Qt.AlignLeft)

        self.vbox.addLayout(header_hbox)

        self.update_widget = MorePage.WidgetModel(
            self, icon_name="mdi6.update",
            legend_text=f"Software Update Available: Enhancements, Fixes, and New Features for pyuxterm-qt<br><strong>Current version: 0.0.1</strong>",
            open_btn_text="Open Link",
            open_btn_link="https://github.com/IgdaliasCabamba/pyuxterm-qt-client/releases")
        self.update_widget.setObjectName("AppFrameSecondary")

        self.github_widget = MorePage.WidgetModel(
            self, icon_name="mdi6.github",
            legend_text="Explore and Collaborate on Our GitHub Repository!",
            open_btn_text="Open Link",
            open_btn_link="https://github.com/IgdaliasCabamba/pyuxterm-qt-client")
        self.github_widget.setObjectName("AppFrameSecondary")

        self.distrobox_widget = MorePage.WidgetModel(
            self, icon_name="mdi6.linux",
            legend_text="<strong style='background:red; color:white'>DistroBox</strong> Use any Linux distribution inside your terminal.",
            open_btn_text="Open Link",
            open_btn_link="https://github.com/89luca89/distrobox")
        self.distrobox_widget.setObjectName("AppFrameSecondary")

        self.vbox.addWidget(self.update_widget)
        self.vbox.addWidget(self.github_widget)
        self.vbox.addWidget(self.distrobox_widget)

        self.scroll_area.setWidget(self.main_widget)
        self.scroll_area.setWidgetResizable(True)
        self.layout.addWidget(self.scroll_area)


class Home(QFrame):
    on_password_changed = Signal(str)

    def __init__(self, parent):
        super().__init__(parent)
        self.build()
        self.listen_events()

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

        self.new_terminal_btn = QPushButton(self)
        self.new_terminal_btn.setText("New terminal")
        self.new_terminal_btn.setIcon(qta.icon('mdi6.console-line', options=[
            {'scale_factor': 1}], color='white'))
        self.new_terminal_btn.setObjectName("AppButtonPrimary")

        self.view_distros_btn = QPushButton(self)
        self.view_distros_btn.setText("More")
        self.view_distros_btn.setIcon(qta.icon('mdi6.more', options=[
            {'scale_factor': 1}], color='white'))
        self.view_distros_btn.setObjectName("AppButtonSecondary")

        hbox_panel1 = QHBoxLayout()
        hbox_panel1.setContentsMargins(5, 0, 5, 0)

        hbox_panel1.addWidget(self.new_terminal_btn, Qt.AlignCenter)
        hbox_panel1.addWidget(self.view_distros_btn, Qt.AlignCenter)

        self.vbox_panel.addLayout(hbox_panel1)

        self.vbox.addWidget(self.start_panel)

    def save_password(self, password: str):
        with sh.contrib.sudo(password=password, _with=True):
            try:
                sh.echo("uterm")
                self.password_input.setStyleSheet("border: 2px inset green;")
                self.on_password_changed.emit(password)
            except sh.ErrorReturnCode:
                self.password_input.setStyleSheet("border: 2px outset red;")

    def listen_events(self):
        self.password_input.returnPressed.connect(
            lambda: self.save_password(self.password_input.text()))


class PrimaryScreen(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.build()
        self.listen_events()

    def build(self) -> None:
        self.box = QStackedLayout(self)
        self.box.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.box)

        self.home = Home(self)
        self.install = MorePage(self)
        self.nav_back_btn = self.install.nav_back_btn
        self.new_terminal_btn = self.home.new_terminal_btn
        self.view_distros_btn = self.home.view_distros_btn

        self.box.addWidget(self.home)
        self.box.addWidget(self.install)
        self.box.setCurrentWidget(self.home)

    def listen_events(self):
        self.view_distros_btn.clicked.connect(
            lambda: self.box.setCurrentWidget(self.install))
        self.nav_back_btn.clicked.connect(
            lambda: self.box.setCurrentWidget(self.home))
