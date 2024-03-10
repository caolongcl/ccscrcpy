from PySide6.QtCore import *  # type: ignore
from PySide6.QtGui import *  # type: ignore
from PySide6.QtWidgets import *
from typing import Any, Callable

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
        super().__init__(f"【{device.index+1:02d}】型号:{device.client.device_name}")
        self.device = device

        layout = QVBoxLayout()
        layout.setSpacing(2)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.focused = QLabel()
        self.focused.setFixedHeight(8)
        self.update_focused_status(False)
        layout.addWidget(self.focused)

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

    def update_focused_status(self, focused):
        if focused:
            self.focused.setStyleSheet(f"background-color: rgba(0,200,0,255)")
        else:
            self.focused.setStyleSheet(f"background-color: grey")


# 投屏列表
class _DeviceScreenGridView(QGroupBox):
    def __init__(self):
        super().__init__(f"设备投屏")

        self.col = -1
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

        self.devices_screen = {}

        layout.addItem(
            QSpacerItem(
                0,
                0,
                hData=QSizePolicy.Policy.Expanding,
                vData=QSizePolicy.Policy.Expanding,
            )
        )

    def __update_devices_screen(self, devices_screen: list[_DeviceScreen]):
        max_col = self.col
        row = 0
        col = 0

        for i in range(len(devices_screen)):
            row = i // max_col
            col = i % max_col

            self.device_screen_grid.addWidget(
                devices_screen[i],
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

    def __create_device_screen(self, device: Device):
        return _DeviceScreen(
            device,
            self.on_mouse_event(Com.ACTION_DOWN),
            self.on_mouse_event(Com.ACTION_MOVE),
            self.on_mouse_event(Com.ACTION_UP),
            self.on_key_event(Com.ACTION_DOWN),
            self.on_key_event(Com.ACTION_UP),
        )

    # devices 是启动以来所有的设备
    def __compare_and_create(self, devices: list[Device]):
        sorted_devices_screen = []
        for i in range(len(devices)):
            d = devices[i]
            if d.device.serial in self.devices_screen:
                screen = self.devices_screen[d.device.serial]
                if d.online:
                    sorted_devices_screen.append(screen)
                else:
                    del screen
            else:
                if d.online:
                    screen = self.__create_device_screen(d)
                    self.devices_screen[d.device.serial] = screen
                    sorted_devices_screen.append(screen)
        return sorted_devices_screen

    def attach(
        self, col, on_mouse_event: Callable[..., Any], on_key_event: Callable[..., Any]
    ):  
        self.col = col
        self.on_mouse_event = on_mouse_event
        self.on_key_event = on_key_event

    def update_devices_by_col(self, col):
        num = len(self.devices_screen)
        last_col = self.col
        self.col = col
        if (self.col >= num and last_col >= num) or self.col == last_col:
            print(f"return update_devices_by_col")
            return
        print(f"update_devices_by_col")

        ViewClear().clear(self.device_screen_grid)
        self.__update_devices_screen(self.devices_screen)

    # 更新设备列表
    def update_devices(self, devices: list[Device]):
        ViewClear().clear(self.device_screen_grid)
        self.__update_devices_screen(self.__compare_and_create(devices))

    def update_title(self, d: Device):
        self.devices_screen[d.device.serial].update_title()

    def render_device_screen(self, d: Device, frame):
        self.devices_screen[d.device.serial].render_frame(d.ratio, frame)

    def update_focused_status(self, d: Device, focused):
        self.devices_screen[d.device.serial].update_focused_status(focused)


#####################################
class RightView(QGroupBox):
    def __init__(self):
        super().__init__()

        self.on_mouse_event = None
        self.on_key_event = None

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
        col,
        on_mouse_event: Callable[..., Any],
        on_key_event: Callable[..., Any],
    ):
        self.on_mouse_event = on_mouse_event
        self.on_key_event = on_key_event

        self.device_screen_grid_view.attach(col, self.on_mouse_event, self.on_key_event)

    def update_devices_by_col(self, col):
        self.device_screen_grid_view.update_devices_by_col(col)

    def update_devices(self, devices: list[Device]):
        self.device_screen_grid_view.update_devices(devices)

    def render_device_screen(self, device, frame):
        self.device_screen_grid_view.render_device_screen(device, frame)
    
    def update_title(self, device):
         self.device_screen_grid_view.update_title(device)

    def update_focused_status(self, device, devices: list[Device]):
        for i in range(len(devices)):
            # print(f'ddsf device_index == i {device_index}=={i}')
            self.device_screen_grid_view.update_focused_status(
                devices[i], devices[i] == device
            )
