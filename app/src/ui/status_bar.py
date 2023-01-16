from PySide6.QtWidgets import QStatusBar, QLabel

class StatusBar(QStatusBar):
    def __init__(self, parent):
        super().__init__(parent)
        self.build()
    
    def build(self):
        # self.status_bar.addWidget(QLabel(str(os.getcwd())))
        self.addPermanentWidget(QLabel("CPU: 100%"))