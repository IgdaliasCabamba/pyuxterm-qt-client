# Based on amazing work of @hydrargyrum at https://github.com/hydrargyrum/eye/blob/master/eye/widgets/splitter.py

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
        self.setObjectName("qtmd-splitter")
        self.add_category("splitmanager")
        
        self.main = parent
        self.containers = []
        self.index = 0
        self.opaque_resize = False

        self.root = self.SplitterClass(orientation=Qt.Orientation.Horizontal)

        layout = QStackedLayout(self)
        self.setLayout(layout)
        layout.addWidget(self.root)
    
    def get_data_of(self, reference_widget):
        if reference_widget is None:
            parent = self.root
            idx = 0
        else:
            assert self.isAncestorOf(reference_widget)

            if hasattr(reference_widget.parent, "root"):
                parent = reference_widget.parent.root
            else:
                parent = reference_widget.parent()

            idx = parent.indexOf(reference_widget)
        
        return {"idx":idx, "parent":parent}

    def add_widget(self, widget:QWidget) -> None:
        self.containers.append(widget)

    def splitAt(self, reference_widget, direction, new_widget) -> None:
        widget_data = self.get_data_of(reference_widget)
        parent = widget_data["parent"]
        idx = widget_data["idx"]

        orientation = consts.ORIENTATIONS[direction]
        if parent.orientation() == orientation:
            oldsize = parent.sizes()
           
            if oldsize:
                oldsize[idx] //= 2
                oldsize.insert(idx, oldsize[idx])

            if direction in (consts.DOWN, consts.RIGHT):
                idx += 1

            parent.insertWidget(idx, new_widget) # insert the new widget to the parent of reference widget

            if oldsize:
                parent.setSizes(oldsize)
        else:
            refocus = reference_widget and reference_widget.hasFocus()
            new_split = self.SplitterClass(orientation=orientation)

            if reference_widget:
                oldsize = parent.sizes()
                
                if direction in (consts.DOWN, consts.RIGHT):
                    new_split.addWidget(reference_widget)
                    parent.insertWidget(idx, new_split) # insert the new splitter to the parent of reference widget
                    new_split.addWidget(new_widget)

                else:
                    new_split.addWidget(new_widget)
                    parent.insertWidget(idx, new_split) # insert the new splitter to the parent of reference widget
                    new_split.addWidget(reference_widget)

                parent.setSizes(oldsize)
                new_split.setSizes([100, 100])
                reference_widget.setParent(new_split)

            else:
                new_split.addWidget(new_widget)
                parent.insertWidget(idx, new_split)

            if refocus:
                reference_widget.setFocus()

        self.index += 1
        
        self.add_splited_widget(self.index, reference_widget, direction, new_widget)
        self.update_size()
        self._apply_properties()

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
    
    def _iter_recursive(self, startAt=None):
        if startAt is None:
            startAt = self.root

        splitters = [startAt]
        yield startAt
        while splitters:
            spl = splitters.pop()
            for i in range(spl.count()):
                w = spl.widget(i)
                if isinstance(w, self.SplitterClass):
                    splitters.append(w)
                yield w

    @property
    def has_widget(self) -> bool:
        return bool(len(self.containers))
    
    def _apply_properties(self):
        self.set_opaque_resize(self.opaque_resize)
    
    def set_opaque_resize(self, opaque:bool = True):
        self.opaque_resize = opaque
        for w in self._iter_recursive():
            if hasattr(w, "setOpaqueResize"):
                w.setOpaqueResize(opaque)