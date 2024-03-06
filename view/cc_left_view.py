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

        self.device_no_list = []

        layout = QVBoxLayout()
        self.setLayout(layout)

        layout.setSpacing(4)
        layout.setContentsMargins(2, 2, 2, 2)

        # 设备列表 grid
        self.device_no_grid = QGridLayout()
        self.device_no_grid.setSpacing(4)
        self.device_no_grid.setContentsMargins(2, 2, 2, 2)

        layout.addLayout(self.device_no_grid)
        layout.addItem(
            QSpacerItem(
                0, 0, hData=QSizePolicy.Policy.Maximum, vData=QSizePolicy.Policy.Maximum
            )
        )

    def update_list(self, devices: list[Device]):
        ViewClear().clear(self.device_no_grid)
        self.device_no_list = []

        # 更新
        max_col = 3
        row = 0
        col = 0

        for i in range(len(devices)):
            device = devices[i]
            row = i // max_col
            col = i % max_col
            device_label = QLabel(f"【{i+1:02d}】")
            self.device_no_list.append(device_label)
            device_label.setFixedSize(40, 30)
            self.device_no_grid.addWidget(
                device_label,
                row,
                col,
                Qt.AlignmentFlag.AlignCenter,
            )

        # for i in range(20):
        #     row = i // max_col
        #     col = i % max_col
        #     device_label = QLabel(f"【{i+1:02d}】")
        #     device_label.setFixedSize(40, 30)
        #     self.device_no_grid.addWidget(
        #         device_label,
        #         row,
        #         col,
        #         Qt.AlignmentFlag.AlignCenter,
        #     )

    def update_device_name(self, device: Device):
        self.device_no_list[device.index].setToolTip(f"序列号:{device.serial}")


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

    def update_device_num(self):
        self.device_stats_view.update_device_num(self.device_manager.get_device_num())

    def update_device_no_list(self):
        self.device_no_view.update_list(self.device_manager.get_devices())

    def update_device_name(self, device_index):
        self.device_no_view.update_device_name(
            self.device_manager.get_devices()[device_index]
        )
