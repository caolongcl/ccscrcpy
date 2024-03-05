from PySide6.QtCore import *  # type: ignore
from PySide6.QtGui import *  # type: ignore
from PySide6.QtWidgets import *

class ViewClear:
  def clear(self, item):
    if hasattr(item, "layout"):
        # print(f'hasattr layout')
        if callable(item.layout):
            # print(f'callbal layout')
            layout = item.layout()
    else:
        # print(f'noattr layout')
        layout = None

    if hasattr(item, "widget"):
        # print(f'hasattr widget')
        if callable(item.widget):
            # print(f'callbal widget')
            widget = item.widget()
    else:
        # print(f'noattr widget')
        widget = None

    if widget:
        widget.setParent(None)
    elif layout:
        for i in reversed(range(layout.count())):
            self.clear(layout.itemAt(i))