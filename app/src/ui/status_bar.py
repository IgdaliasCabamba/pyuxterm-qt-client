import psutil
from PySide6.QtWidgets import QStatusBar, QLabel
from PySide6.QtCore import Qt, QObject, QThread, Signal, QTimer
from ..thread_manager import ChellyQThreadManager


class SystemMonitor(QObject):

    on_updated = Signal(dict)

    def __init__(self, parent):
        super().__init__()
        self.parent = parent

    def run(self) -> None:
        self.parent.on_refresh_stats.connect(self.update_stats)

    def update_stats(self) -> None:
        data = {"cpu": psutil.cpu_percent(interval=1, percpu=True),
                "mem": psutil.virtual_memory()}

        self.on_updated.emit(data)
        


class StatusBar(QStatusBar):
    on_refresh_stats = Signal()

    COLORS = {
        "good": "#51c48f",
        "warning": "#e8c55a",
        "danger": "#ed6673"
    }

    def __init__(self, parent):
        super().__init__(parent)
        self.thread_manager = ChellyQThreadManager()
        self.thread = QThread(self)
        self.thread_manager.append(self.thread)
        self.monitor_worker = SystemMonitor(self)
        self.monitor_worker.moveToThread(self.thread)
        self.monitor_worker.on_updated.connect(self.display_stats)
        self.thread.started.connect(self.monitor_worker.run)
        self.thread.start()
        self.stats_update_timer = QTimer(self)
        self.stats_update_timer.setInterval(1000)
        self.stats_update_timer.timeout.connect(lambda: self.on_refresh_stats.emit())
        self.stats_update_timer.start()
        self.build()

    def build(self):
        self.label_cpu_stat = QLabel(self)
        self.label_free_mem = QLabel(self)

        self.addWidget(self.label_cpu_stat)
        self.addWidget(self.label_free_mem)

    def display_stats(self, data: dict) -> None:
        mem_percent = int(data['mem'].percent)
        percentage_text = str()

        for index, percent in enumerate(data["cpu"]):
            percent = int(percent)
            if percent <= 33:
                fgcolor = self.COLORS["good"]

            elif percent <= 66:
                fgcolor = self.COLORS["warning"]

            else:
                fgcolor = self.COLORS["danger"]

            if len(data) >= index+2:
                percentage_text += f"<span style='color: {fgcolor}'>&nbsp;CPU[{index+1}]:&nbsp;{percent}%&nbsp;|&nbsp;</span>"
            else:
                percentage_text += f"<span style='color: {fgcolor}'>CPU[{index+1}]:&nbsp;{percent}%</span>"

        self.label_cpu_stat.setText(percentage_text)

        if mem_percent <= 33:
            fgcolor = self.COLORS["good"]

        elif mem_percent <= 66:
            fgcolor = self.COLORS["warning"]

        else:
            fgcolor = self.COLORS["danger"]

        self.label_free_mem.setText(
            f"<span style='color: {fgcolor}'>MEM:&nbsp;{mem_percent}%</span>")
