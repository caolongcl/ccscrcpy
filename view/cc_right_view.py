from PySide6.QtCore import *  # type: ignore
from PySide6.QtGui import *  # type: ignore
from PySide6.QtWidgets import *
from typing import Any, Callable, Optional

from view.cc_com import Com

from model.device import *
from view.cc_clear import ViewClear


# 单个投屏
class _DeviceScreen(QGroupBox):
    def __init__(
        self,
        device: Device,
        mousePressEvent: Callable[..., Any],
        mouseMoveEvent: Callable[..., Any],
        mouseReleaseEvent: Callable[..., Any],
        keyPressEvent: Callable[..., Any],
        keyReleaseEvent: Callable[..., Any],
    ):
        super().__init__(f"【{device.index+1:02d}】序列号:{device.client.device_name}")
        self.device = device

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.screen = QLabel()  # 对外暴露
        layout.addWidget(self.screen, alignment=Qt.AlignmentFlag.AlignCenter)

        # Bind mouse event
        self.screen.mousePressEvent = mousePressEvent(device)
        self.screen.mouseMoveEvent = mouseMoveEvent(device)
        self.screen.mouseReleaseEvent = mouseReleaseEvent(device)

        # Bind key event
        self.screen.setFocusPolicy(Qt.StrongFocus)
        self.screen.keyPressEvent = keyPressEvent(device)
        self.screen.keyReleaseEvent = keyReleaseEvent(device)

        # other control
        ctrl_layout = QHBoxLayout()
        ctrl_layout.setSpacing(0)
        ctrl_layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(ctrl_layout)

        screen_btn = QPushButton(f"亮屏")
        screen_btn.clicked.connect(device.on_click_screen)
        home_btn = QPushButton(f"桌面")
        home_btn.clicked.connect(device.on_click_home)
        back_btn = QPushButton(f"返回")
        back_btn.clicked.connect(device.on_click_back)
        apps_btn = QPushButton(f"最近")
        apps_btn.clicked.connect(device.on_click_recent)

        ctrl_layout.addItem(
            QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
        )
        ctrl_layout.addWidget(screen_btn)
        ctrl_layout.addWidget(back_btn)
        ctrl_layout.addWidget(home_btn)
        ctrl_layout.addWidget(apps_btn)
        ctrl_layout.addItem(
            QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
        )

    def render_frame(self, ratio, frame):
        # print(f"render_frame ratio{ratio}")
        image = QImage(
            frame,
            frame.shape[1],
            frame.shape[0],
            frame.shape[1] * 3,
            QImage.Format_BGR888,
        )
        # print(f"frame {frame.shape[1]} {frame.shape[0]}")
        pix = QPixmap(image)
        pix.setDevicePixelRatio(1 / ratio)
        self.screen.setPixmap(pix)

    def update_title(self):
        self.setTitle(
            f"【{self.device.index+1:02d}】设备型号:{self.device.client.device_name}"
        )


# 投屏列表
class _DeviceScreenGridView(QGroupBox):
    def __init__(self):
        super().__init__(f"设备投屏")

        self.on_mouse_event = None
        self.on_key_event = None

        # 右边栏：显示所有手机投屏
        layout = QVBoxLayout()
        layout.setContentsMargins(2, 2, 2, 2)
        self.setLayout(layout)

        self.device_screen_grid = QGridLayout()
        layout.addLayout(self.device_screen_grid)

        self.device_screen_grid.setSpacing(4)
        self.device_screen_grid.setContentsMargins(2, 2, 2, 2)

        self.device_screen_list = []

        layout.addItem(
            QSpacerItem(
                0,
                0,
                hData=QSizePolicy.Policy.Expanding,
                vData=QSizePolicy.Policy.Expanding,
            )
        )

    # 更新视频列表
    def update_device_screen(self, device_col, devices: list[Device]):
        ViewClear().clear(self.device_screen_grid)
        self.device_screen_list = []

        max_col = device_col
        row = 0
        col = 0

        for i in range(len(devices)):
            device = devices[i]
            row = i // max_col
            col = i % max_col

            device_screen = _DeviceScreen(
                device,
                self.on_mouse_event(Com.ACTION_DOWN),
                self.on_mouse_event(Com.ACTION_MOVE),
                self.on_mouse_event(Com.ACTION_UP),
                self.on_key_event(Com.ACTION_DOWN),
                self.on_key_event(Com.ACTION_UP),
            )
            self.device_screen_list.append(device_screen)

            self.device_screen_grid.addWidget(
                device_screen,
                row,
                col,
                Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter,
            )

        self.device_screen_grid.addItem(
            QSpacerItem(
                0,
                0,
                hData=QSizePolicy.Policy.Expanding,
                vData=QSizePolicy.Policy.Expanding,
            ),
            row + 1,
            col + 1,
            col + 1,
            row + 1,
        )

    def attach(
        self, on_mouse_event: Callable[..., Any], on_key_event: Callable[..., Any]
    ):
        self.on_mouse_event = on_mouse_event
        self.on_key_event = on_key_event

    def get_screen_list(self):
        return self.device_screen_list

    def update_device_name(self, device: Device):
        self.device_screen_list[device.index].update_title()


#####################################
class RightView(QGroupBox):
    def __init__(self):
        super().__init__()

        self.device_col = 0
        self.on_mouse_event = None
        self.on_key_event = None
        self.device_manager = None

        # 显示设备投屏
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # 设备列表
        self.device_screen_grid_view = _DeviceScreenGridView()
        main_layout.addWidget(self.device_screen_grid_view)

        # 设备控制

        main_layout.addStretch(-1)  # 空白占用空间，不拉伸

    def attach(
        self,
        device_manager: DeviceManager,
        on_mouse_event: Callable[..., Any],
        on_key_event: Callable[..., Any],
    ):
        self.device_manager = device_manager
        self.on_mouse_event = on_mouse_event
        self.on_key_event = on_key_event

        self.device_screen_grid_view.attach(self.on_mouse_event, self.on_key_event)

    def update_devices_by_col(self, device_col):
        self.device_col = device_col
        self.device_screen_grid_view.update_device_screen(
            device_col, self.device_manager.get_devices()
        )

    def update_devices(self):
        self.device_screen_grid_view.update_device_screen(
            self.device_col, self.device_manager.get_devices()
        )

    def render_device_screen(self, index, ratio, frame):
        screen_list = self.device_screen_grid_view.get_screen_list()
        screen_list[index].render_frame(ratio, frame)

    def update_device_name(self, device_index):
        self.device_screen_grid_view.update_device_name(
            self.device_manager.get_devices()[device_index]
        )
