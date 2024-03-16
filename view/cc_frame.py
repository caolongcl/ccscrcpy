from PySide6.QtCore import QObject
from PySide6.QtCore import *


class Frame(QObject):
    frame_signal = Signal(object)

    def __init__(self) -> None:
        super(Frame, self).__init__()

    def set_connect(self, slot):
        self.frame_signal.connect(slot)

    def post(self, frame):
        self.frame_signal.emit(frame)


class CustomEvent(QObject):
    custom_signal = Signal(object)

    def __init__(self) -> None:
        super(CustomEvent, self).__init__()

    def set_connect(self, slot):
        self.custom_signal.connect(slot)

    def post(self, data):
        self.custom_signal.emit(data)