from typing import Any, Callable
from PySide6.QtCore import *
from PySide6.QtWidgets import *
from PySide6.QtGui import *

from model.device import Device
from view.settings import DeviceNameSettings


class _ModifyEdit(QWidget):
    def __init__(self, device: Device) -> None:
        super().__init__()

        self.device = device
        box = QHBoxLayout()
        label = QLabel(f"【{self.device.index+1:02d}】")
        label.setFixedWidth(50)
        label.setToolTip(self.device.serial)
        box.addWidget(label)

        self.lineEdit = QLineEdit()
        self.lineEdit.setText(self.device.name)
        box.addWidget(self.lineEdit)
        self.setLayout(box)

        self.setFixedHeight(50)

    def update_device_info(self):
        self.device.name = self.lineEdit.text()


class _ModifyList(QWidget):
    def __init__(self, devices: list[Device]) -> None:
        super().__init__()

        self.devices = devices
        self.modify_device_list = QVBoxLayout()
        self.modify_device_list.setSpacing(0)
        self.modify_device_list.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.modify_device_list)

        self.modify_edit = []
        for device in self.devices:
            edit = _ModifyEdit(device)
            self.modify_edit.append(edit)
            self.modify_device_list.addWidget(edit)

        self.modify_device_list.addStretch(-1)

    def update_device_info(self):
        for m in self.modify_edit:
            m.update_device_info()


class DeviceNameModifyDialog(QDialog):
    def __init__(
        self, devices: list[Device], on_device_name_update: Callable[..., Any]
    ) -> None:
        super().__init__()

        self.devices = devices
        self.on_device_name_update = on_device_name_update

        self.setWindowTitle("修改设备命名")

        button_box = QDialogButtonBox()
        button_box.addButton("取消", QDialogButtonBox.ButtonRole.RejectRole)
        button_box.addButton("确定", QDialogButtonBox.ButtonRole.AcceptRole)
        button_box.accepted.connect(self.__accept)
        button_box.rejected.connect(self.__reject)

        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        self.modify_list = _ModifyList(devices)
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setMinimumWidth(200)
        self.scroll_area.setMinimumHeight(100)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.modify_list)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        layout.addWidget(self.scroll_area)

        layout.addWidget(
            button_box,
            alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom,
        )
        self.setLayout(layout)

    def __accept(self):
        self.modify_list.update_device_info()
        device_name_settings = DeviceNameSettings()
        for device in self.devices:
            device_name_settings.add_device_name(device.serial, device.name)
            self.on_device_name_update(device)

        self.close()

    def __reject(self):
        self.close()
