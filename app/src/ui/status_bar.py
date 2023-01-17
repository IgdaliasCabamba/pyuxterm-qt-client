import psutil
from PySide6.QtWidgets import QStatusBar, QLabel
from PySide6.QtCore import Qt, QObject, QThread

class StatusBar(QStatusBar):
    def __init__(self, parent):
        super().__init__(parent)
        self.build()
    
    def build(self):
        # self.status_bar.addWidget(QLabel(str(os.getcwd())))
        self.addPermanentWidget(QLabel("CPU: 100%"))
        
        print(psutil.cpu_percent(interval=1, percpu=True))
        print(psutil.virtual_memory())