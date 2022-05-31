from PyQt5.QtWidgets import QFrame, QGraphicsDropShadowEffect, QVBoxLayout, QSizePolicy, QLabel, QHBoxLayout, QShortcut
from PyQt5.QtGui import QColor
from PyQt5.QtCore import pyqtSignal, QPoint

class ModernMenuSeparator(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy(
            QSizePolicy.Maximum, QSizePolicy.Fixed
        ))
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)

class ModernAction(QFrame):
    
    on_triggered = pyqtSignal()

    def __init__(self, parent=None, title:str="", shortcut:str=""):
        super().__init__(parent)
        self.title = title
        self.shortcut = QShortcut(self)
        self.shortcut.setKey(shortcut)
        self.shortcut.activated.connect(lambda: self.on_triggered.emit())
        
        self.hbox = QHBoxLayout(self)
        self.setLayout(self.hbox)
        
        self.title_component = QLabel(self.title)
        self.hbox.addWidget(self.title_component)
    
    def mousePressEvent(self, event) -> None:
        super().mousePressEvent(event)
        self.on_triggered.emit()

class ModernMenu(QFrame):
    def __init__(self, parent=None, title:str=""):
        super().__init__(parent)
        self.title = title

        self.vbox = QVBoxLayout(self)
        
        self.drop_shadow = QGraphicsDropShadowEffect(self)
        self.drop_shadow.setBlurRadius(10)
        self.drop_shadow.setOffset(0, 0)
        self.drop_shadow.setColor(QColor(0, 0, 0))
        self.setGraphicsEffect(self.drop_shadow)
    
    def add_action(self, action:ModernAction):
        if isinstance(action, ModernAction):
            self.vbox.addWidget()
    
    def add_separator(self):
        self.layout.addWidget(ModernMenuSeparator(self))
    
    def show_at(self, x, y):
        self.move(QPoint(x, y))
        self.show()

