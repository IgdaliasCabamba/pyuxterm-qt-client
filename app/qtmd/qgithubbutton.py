from PyQt5.QtWidgets import QFrame, QSizePolicy, QHBoxLayout, QVBoxLayout

class QGithubButton(QFrame):
    def __init__(self, parent, orientation=0):
        super().__init__(parent)
        self.setObjectName("qtmd-github-button")
        self.parent = parent
        self.widget_primary = None
        self.widget_secondary = None
        self.orientation = orientation
        self.size_policy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setSizePolicy(self.size_policy)

        if self.orientation == 0:
            self.layout = QHBoxLayout(self)
        else:
            self.layout = QVBoxLayout(self)

        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

    def set_widget_primary(self, btn):
        self.widget_primary = btn
        self.layout.addWidget(self.widget_primary)

    def set_widget_secondary(self, btn):
        self.widget_secondary = btn
        self.layout.addWidget(self.widget_secondary)
