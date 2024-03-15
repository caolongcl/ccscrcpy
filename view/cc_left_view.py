from PySide6.QtCore import *  # type: ignore
from PySide6.QtGui import *  # type: ignore
from PySide6.QtWidgets import *

from view.cc_clear import ViewClear

from model.device import *


class _NormalLabel(QHBoxLayout):
    def __init__(self, title):
        super().__init__()

        title_label = QLabel(title)
        self.target_label = QLabel()
        self.addWidget(title_label)
        self.addWidget(self.target_label)

    def update_target_label(self, target):
        self.target_label.setText(target)


# 设备统计信息
class _DeviceStatsView(QGroupBox):
    def __init__(self):
        super().__init__()

        self.setFixedHeight(70)

        main_layout = QVBoxLayout()
        self.device_num = _NormalLabel(f"连接数:")
        main_layout.addLayout(self.device_num)

        self.cur_device = _NormalLabel(f"选中:")
        main_layout.addLayout(self.cur_device)

        self.setLayout(main_layout)

    def update_device_num(self, num):
        self.device_num.update_target_label(f"{num}")

    def update_cur_device(self, device: Device):
        if device is None:
            self.cur_device.update_target_label(f"")
            return
        self.cur_device.update_target_label(f"【{device.index+1:02d}】")


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
                0,
                0,
                hData=QSizePolicy.Policy.Expanding,
                vData=QSizePolicy.Policy.Expanding,
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
                Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft,
            )

    def __create_device_no(self, device: Device):
        device_label = QLabel(f"【{device.index+1:02d}】")
        device_label.setToolTip(
            f"序列号:{device.serial} 型号:{device.client.device_name}"
        )
        device_label.setFixedSize(40, 30)
        return device_label

    def update_device_name(self, d: Device):
        self.devices_no[d.device.serial].setToolTip(
            f"序列号:{d.device.serial} 型号:{d.client.device_name}"
        )

    # devices 是启动以来所有的设备
    def __compare_and_create(self, devices: list[Device]):
        sorted_devices_no = []
        for d in devices:
            if d.serial in self.devices_no:
                device_no = self.devices_no[d.serial]
                if d.online:
                    sorted_devices_no.append(device_no)
                else:
                    del device_no
            else:
                if d.online:
                    new_device_no = self.__create_device_no(d)
                    self.devices_no[d.serial] = new_device_no
                    sorted_devices_no.append(new_device_no)
        return sorted_devices_no


class _CurDeviceCtrlView(QGroupBox):
    def __init__(self):
        super().__init__(f"控制选中设备")

        self.setFixedHeight(120)

        self.device = None

        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        self.home_btn = QPushButton(f"桌面")
        self.back_btn = QPushButton(f"返回")
        self.apps_btn = QPushButton(f"最近")

        layout.addWidget(self.back_btn)
        layout.addWidget(self.home_btn)
        layout.addWidget(self.apps_btn)

        self.setLayout(layout)

    def set_cur_device(self, device: Device):
        if self.device is not None:
            self.home_btn.clicked.disconnect(self.device.on_click_home)
            self.back_btn.clicked.disconnect(self.device.on_click_back)
            self.apps_btn.clicked.disconnect(self.device.on_click_recent)

        self.device = device
        if self.device is not None:
            self.home_btn.clicked.connect(self.device.on_click_home)
            self.back_btn.clicked.connect(self.device.on_click_back)
            self.apps_btn.clicked.connect(self.device.on_click_recent)


##############################
class LeftView(QGroupBox):
    def __init__(self):
        super().__init__()

        self.setFixedWidth(140)

        # 左边栏：显示信息和控制
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # 设备列表
        self.device_stats_view = _DeviceStatsView()
        self.device_no_view = _DeviceNoView()
        self.device_cur_ctrl = _CurDeviceCtrlView()
        main_layout.addWidget(self.device_stats_view)
        main_layout.addWidget(self.device_no_view)
        main_layout.addWidget(
            self.device_cur_ctrl, alignment=Qt.AlignmentFlag.AlignBottom
        )

        # 设备控制
        # main_layout.addStretch(-1)  # 空白占用空间，不拉伸

    def update_devices_num(self, devices: list[Device]):
        num = len(list(filter(lambda d: d.online == True, devices)))
        self.device_stats_view.update_device_num(num)

    def update_cur_device(self, device: Device = None):
        self.device_stats_view.update_cur_device(device)
        self.device_cur_ctrl.set_cur_device(device)

    def update_devices_no(self, devices: list[Device]):
        self.device_no_view.update_devices(devices)

    def update_device_name(self, device: Device):
        self.device_no_view.update_device_name(device)
