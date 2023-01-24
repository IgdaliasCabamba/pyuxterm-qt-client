import os
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest
import qtawesome as qta
import sh
from sarge import capture_stdout
from ..thread_manager import ChellyQThreadManager


class DockerPullWorker(QObject):

    on_pulled = Signal(object)

    def __init__(self, parent):
        super().__init__()
        self._parent = parent

    def run(self) -> None:
        self._parent.on_pull_requested.connect(self.pull_image)

    def pull_image(self, image_path: str, password: str) -> None:
        try:
            res = capture_stdout(
                f"echo '{password}' | sudo -S docker pull {image_path}")
            self.on_pulled.emit(image_path)
        except Exception as e:
            print(e)


class ContainerImage(QFrame):
    on_pull_requested = Signal(str, str)

    def render_icon(self, reply):
        img = QImage()
        img.loadFromData(reply.readAll())
        self.icon_label.setPixmap(QPixmap(img.scaled(QSize(96, 96))))

    def __init__(self, parent, container_key, container_data: dict):
        super().__init__(parent)
        self.setObjectName("AppFrameSecondary")

        self.container_data = container_data
        self.container_key = container_key
        self.thread_manager = ChellyQThreadManager()

        self.thread = QThread(self)
        self.thread_manager.append(self.thread)
        self.pull_worker = DockerPullWorker(self)
        self.pull_worker.moveToThread(self.thread)
        self.thread.started.connect(self.pull_worker.run)
        self.thread.start()
        self.build()

    def build(self):
        self.gbox = QGridLayout(self)
        self.gbox.setContentsMargins(5, 5, 5, 5)
        self.setLayout(self.gbox)

        self.icon_label = QLabel(self)
        self.icon_label.setPixmap(qta.icon('msc.terminal-linux', options=[
            {'scale_factor': 1}], color='white').pixmap(QSize(64, 64)))
        self.icon_label.setAlignment(Qt.AlignCenter)

        self.title_label = QLabel(self)
        self.title_label.setText(
            f"<h3>{self.container_data['name']}</h3> <p>{self.container_data['description']}</p>")
        self.title_label.setWordWrap(True)

        self.install_btn = QPushButton(self)
        self.install_btn.setText("Install")
        self.install_btn.setSizePolicy(QSizePolicy(
            QSizePolicy.Fixed, QSizePolicy.Fixed))
        self.install_btn.setIcon(qta.icon('fa5s.download', options=[
            {'scale_factor': 1}], color='white'))
        self.install_btn.setObjectName("AppButtonPrimary")

        self.gbox.addWidget(self.icon_label, 0, 0)
        self.gbox.addWidget(self.title_label, 1, 0)
        self.gbox.addWidget(self.install_btn, 2, 0)

        self.nam = QNetworkAccessManager()
        self.nam.finished.connect(self.render_icon)
        self.nam.get(QNetworkRequest(QUrl(self.container_data['icon'])))


class DistroInstall(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.images = self.parent().parent().docker_images
        self._container_widgets = []
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

        for key, value in self.images.items():
            container_widget = ContainerImage(self, key, value)
            self._container_widgets.append(container_widget)
            self.vbox.addWidget(container_widget, Qt.AlignCenter)

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
        self.view_distros_btn.setText("Distros")
        self.view_distros_btn.setIcon(qta.icon('fa5s.shopping-bag', options=[
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
        self.install = DistroInstall(self)
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
