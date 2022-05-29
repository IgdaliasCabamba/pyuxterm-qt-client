from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from . import CategoryMixin
from . import consts


class Splitter(QSplitter):
    def __init__(self, **kwargs):
        super(Splitter, self).__init__(**kwargs)

    def child_at(self, pos):

        if not self.rect().contains(pos):
            return None
        for i in range(self.count()):
            for w in (self.widget(i), self.handle(i)):
                if w.geometry().contains(pos):
                    return w

    def parent_manager(self):

        w = self.parent()
        while not isinstance(w, MultiSplitter):
            w = w.parent()
        return w

    def widgets(self):
        return [self.widget(i) for i in range(self.count())]

    children = widgets

    def remove_child(self, widget):
        assert self.isAncestorOf(widget)
        assert self is not widget

        widget.setParent(None)

    def replace_child(self, child, new):
        assert child is not new
        assert self is not child
        assert self is not new
        assert self.isAncestorOf(child)

        idx = self.indexOf(child)
        child.setParent(None)
        self.insertWidget(idx, new)


class MultiSplitter(QFrame, CategoryMixin):

    SplitterClass = Splitter
    on_last_widget_closed = pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)
        self.main = parent
        self.containers = []
        self.index = 0

        self.root = self.SplitterClass(orientation=Qt.Orientation.Horizontal)

        layout = QStackedLayout(self)
        self.setLayout(layout)
        layout.addWidget(self.root)

        self.add_category("splitmanager")

    def add_widget(self, widget:QWidget) -> None:
        self.containers.append(widget)

    def splitAt(self, current_widget, direction, new_widget) -> None:
        if current_widget is None:
            parent = self.root
            idx = 0
        else:
            assert self.isAncestorOf(current_widget)

            if hasattr(current_widget.parent, "root"):
                parent = current_widget.parent.root
            else:
                parent = current_widget.parent()

            idx = parent.indexOf(current_widget)

        orientation = consts.ORIENTATIONS[direction]
        if parent.orientation() == orientation:
            oldsize = parent.sizes()
            if oldsize:
                oldsize[idx] //= 2
                oldsize.insert(idx, oldsize[idx])

            if direction in (consts.DOWN, consts.RIGHT):
                idx += 1

            parent.insertWidget(idx, new_widget)

            if oldsize:
                parent.setSizes(oldsize)
        else:
            refocus = current_widget and current_widget.hasFocus()

            new_split = self.SplitterClass(orientation=orientation)

            if current_widget:
                oldsize = parent.sizes()
                if direction in (consts.DOWN, consts.RIGHT):
                    new_split.addWidget(current_widget)
                    parent.insertWidget(idx, new_split)
                    new_split.addWidget(new_widget)

                else:
                    new_split.addWidget(new_widget)
                    parent.insertWidget(idx, new_split)
                    new_split.addWidget(current_widget)

                parent.setSizes(oldsize)
                new_split.setSizes([100, 100])
                current_widget.setParent(new_split)

            else:
                new_split.addWidget(new_widget)
                parent.insertWidget(idx, new_split)

            if refocus:
                current_widget.setFocus()

        self.index += 1
        self.add_splited_widget(self.index, current_widget, direction, new_widget)
        self.update_size()

    def add_splited_widget(self, id, ref, direction, new_widget):
        ref_id = None

        for item in self.containers:
            if id == item["id"]:
                return

        for item in self.containers:
            if ref is not None:
                if ref == item["ref"]:
                    ref_id = item["id"]

        self.containers.append(
            {"id": id, "ref": ref_id, "direction": direction, "widget": new_widget}
        )

    def update_size(self) -> None:
        x = []

        for i in range(self.root.count()):
            x.append(2)

        self.root.setSizes(x)

    @property
    def has_widget(self) -> bool:
        return bool(len(self.containers))
