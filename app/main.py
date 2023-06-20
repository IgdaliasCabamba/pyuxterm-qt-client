import sys
sys.dont_write_bytecode = True

import faulthandler
faulthandler.enable()

import qtmodern.windows
import qtmodern.styles
from src.qtxterm import MainWindow
from src import ChellyQThreadManager
from PySide6.QtWidgets import QApplication
import hjson
from weakref import ref
import random
import os


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


with open(os.path.join(ROOT_PATH, "data", "settings.json"), "r") as fp:
    QTXTERM_SETTINGS = hjson.load(fp)


if QTXTERM_SETTINGS["app-theme"] == "light":
    style_sheet_path = os.path.join(ROOT_PATH, "resources", "light-style.qss")
else:
    style_sheet_path = os.path.join(ROOT_PATH, "resources", "dark-style.qss")

with open(style_sheet_path, "r") as fp:
    STYLE_SHEET = fp.read()


EMULATORS_FILE = os.path.join(ROOT_PATH, "data", "terminals.json")

def main(*args, **kwargs) -> None:
    app = QApplication(sys.argv)
    app_thread_manager = ChellyQThreadManager(app)
    app.setApplicationName("QUTERM")

    window = MainWindow(None, app, EMULATORS_FILE, lambda: random.randint(7000, 65530))

    if QTXTERM_SETTINGS["app-theme"] == "light":
        qtmodern.styles.light(app)
    else:
        qtmodern.styles.dark(app)

    _modern_window = qtmodern.windows.ModernWindow(
        window,
        extra_buttons_left=[
            window.new_terminal_buttons,
            window.show_split_new_terminal_menu,
            window.remove_current_terminal_button,
        ],
        extra_buttons_right = [
            window.toggle_screens_button,
            window.open_settings_file_button
        ]
    )
    window.set_modern_window(_modern_window)
    _modern_window.show()

    app.setStyleSheet(STYLE_SHEET)
    window.setStyleSheet(STYLE_SHEET)

    app.exec()


if __name__ == "__main__":
    main()