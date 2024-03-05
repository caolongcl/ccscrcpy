from PySide6.QtCore import QObject
from PySide6.QtCore import *


class Frame(QObject):
    # int : 设备索引
    frame_signal = Signal(int, object)

    def __init__(self, index) -> None:
        super(Frame, self).__init__()
        self.device_index = index

    def set_connect(self, slot):
        self.frame_signal.connect(slot)

    def post(self, frame):
        self.frame_signal.emit(self.device_index, frame)

class CustomDeviceEvent(QObject):
    custom_signal = Signal(int)

    def __init__(self) -> None:
        super(CustomDeviceEvent, self).__init__()

    def set_connect(self, slot):
        self.custom_signal.connect(slot)

    def post(self, index):
        self.custom_signal.emit(index)
