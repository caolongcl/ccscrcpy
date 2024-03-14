from PySide6.QtCore import Qt
from PySide6.QtWidgets import *
from PySide6.QtWidgets import QWidget

class _ModifyEdit():
  def __init__(self) -> None:
    pass

class DeviceNameModifyDialog(QDialog):
  def __init__(self, parent=None) -> None:
    super().__init__(parent)

    self.setWindowTitle("修改设备命名")

    self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
    self.button_box.accepted.connect(self.__accept)
    self.button_box.rejected.connect(self.__reject)

    self.layout = QVBoxLayout()
    message = QLabel("发生了一些事情！")
    self.layout.addWidget(message)
    self.layout.addWidget(self.button_box)
    self.setLayout(self.layout)

  def __accept(self):
    self.close()

  def __reject(self):
    self.close()