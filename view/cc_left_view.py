from PySide6.QtCore import *  # type: ignore
from PySide6.QtGui import *  # type: ignore
from PySide6.QtWidgets import *

from view.cc_clear import ViewClear

from model.device import *


# 设备统计信息
class _DeviceStatsView(QGroupBox):
    def __init__(self):
        super().__init__()

        layout = QHBoxLayout()
        self.setLayout(layout)
        title = QLabel(f"连接设备:")
        self.device_num = QLabel(f"0")
        layout.addWidget(title)
        layout.addWidget(self.device_num)

    def update_device_num(self, num):
        self.device_num.setText(f"{num}")


# 设备序号列表
class _DeviceNoView(QGroupBox):
    def __init__(self):
        super().__init__(f"设备列表")

        # 设备标号 serial:QLabel
        self.devices_no = {}

        layout = QVBoxLayout()
        self.setLayout(layout)

        layout.setSpacing(4)
        layout.setContentsMargins(2, 2, 2, 2)

        # 设备列表 grid
        self.devices_no_grid = QGridLayout()
        self.devices_no_grid.setSpacing(4)
        self.devices_no_grid.setContentsMargins(2, 2, 2, 2)

        layout.addLayout(self.devices_no_grid)
        layout.addItem(
            QSpacerItem(
                0, 0, hData=QSizePolicy.Policy.Maximum, vData=QSizePolicy.Policy.Maximum
            )
        )

    def update_devices(self, devices: list[Device]):
        ViewClear().clear(self.devices_no_grid)

        # 更新设备列表
        devices_no_list = self.__compare_and_create(devices)

        # 更新
        max_col = 3
        row = 0
        col = 0

        for i in range(len(devices_no_list)):
            row = i // max_col
            col = i % max_col
            self.devices_no_grid.addWidget(
                devices_no_list[i],
                row,
                col,
                Qt.AlignmentFlag.AlignCenter,
            )

    def __create_device_no(self, device: Device):
        device_label = QLabel(f"【{device.index+1:02d}】")
        device_label.setToolTip(f"序列号:{device.serial}")
        device_label.setFixedSize(40, 30)
        return device_label

    # devices 是启动以来所有的设备
    def __compare_and_create(self, devices: list[Device]):
        sorted_devices_no = []
        for i in range(len(devices)):
            d = devices[i]
            if d.device.serial in self.devices_no:
                device_no = self.devices_no[d.device.serial]
                if d.online:
                    sorted_devices_no.append(device_no)
                else:
                    del device_no
            else:
                if d.online:
                    new_device_no = self.__create_device_no(d)
                    self.devices_no[d.device.serial] = new_device_no
                    sorted_devices_no.append(new_device_no)
        return sorted_devices_no

    def __update_device_no(self, d: Device):
        self.devices_no[d.device.serial].setText(f"【{d.index+1:02d}】")
        self.devices_no[d.device.serial].setToolTip(f"序列号:{d.device.serial}")


##############################
class LeftView(QGroupBox):
    def __init__(self):
        super().__init__()
        self.device_manager = None

        self.setFixedWidth(140)

        # 左边栏：显示信息和控制
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # 设备列表
        self.device_stats_view = _DeviceStatsView()
        self.device_no_view = _DeviceNoView()
        main_layout.addWidget(self.device_stats_view)
        main_layout.addWidget(self.device_no_view)

        # 设备控制
        main_layout.addStretch(-1)  # 空白占用空间，不拉伸

    def attach(self, device_manager: DeviceManager):
        self.device_manager = device_manager

    def update_devices_num(self):
        self.device_stats_view.update_device_num(self.device_manager.get_device_num())

    def update_devices_no(self):
        self.device_no_view.update_devices(self.device_manager.get_devices())
