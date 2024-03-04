from PySide6.QtCore import *  # type: ignore
from PySide6.QtGui import *  # type: ignore
from PySide6.QtWidgets import *

class ViewClear:
  def clear(self, item):
    if hasattr(item, "layout"):
        if callable(item.layout):
            layout = item.layout()
    else:
        layout = None

    if hasattr(item, "widget"):
        if callable(item.widget):
            widget = item.widget()
    else:
        widget = None

    if widget:
        widget.setParent(None)
    elif layout:
        for i in reversed(range(layout.count())):
            self.clear(layout.itemAt(i))