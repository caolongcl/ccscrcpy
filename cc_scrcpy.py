import threading
from typing import Tuple

import scrcpy
from adbutils import adb
from PySide6.QtCore import QObject
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import *

# cc
from cc_ui import *
from model.device import *


def map_code(code):
    """
    Map qt keycode ti android keycode

    Args:
        code: qt keycode
        android keycode, -1 if not founded
    """

    print(f"keycode: {code}")

    if code == -1:
        return -1
    # 数字 0~9
    if 48 <= code <= 57:
        return code - 48 + 7
    # 字母
    if 65 <= code <= 90:
        return code - 65 + 29
    if 97 <= code <= 122:
        return code - 97 + 29

    hard_code = {
        Qt.Key.Key_Space: scrcpy.KEYCODE_SPACE,
        Qt.Key.Key_Minus: scrcpy.KEYCODE_MINUS,
        Qt.Key.Key_Equal: scrcpy.KEYCODE_EQUALS,
        Qt.Key.Key_Comma: scrcpy.KEYCODE_COMMA,
        Qt.Key.Key_Period: scrcpy.KEYCODE_PERIOD,
        Qt.Key.Key_QuoteLeft: scrcpy.KEYCODE_GRAVE,
        Qt.Key.Key_Backspace: scrcpy.KEYCODE_DEL,
        Qt.Key.Key_Shift: scrcpy.KEYCODE_SHIFT_LEFT,
        Qt.Key.Key_Enter: scrcpy.KEYCODE_ENTER,
        Qt.Key.Key_Return: scrcpy.KEYCODE_ENTER,
        Qt.Key.Key_Tab: scrcpy.KEYCODE_TAB,
        Qt.Key.Key_Control: scrcpy.KEYCODE_CTRL_LEFT,
        Qt.Key.Key_Escape: scrcpy.KEYCODE_ESCAPE,
        Qt.Key.Key_CapsLock: scrcpy.KEYCODE_CAPS_LOCK,
        Qt.Key.Key_F1: scrcpy.KEYCODE_F1,
        Qt.Key.Key_F2: scrcpy.KEYCODE_F2,
        Qt.Key.Key_F3: scrcpy.KEYCODE_F3,
        Qt.Key.Key_F4: scrcpy.KEYCODE_F4,
        Qt.Key.Key_F5: scrcpy.KEYCODE_F5,
        Qt.Key.Key_F6: scrcpy.KEYCODE_F6,
        Qt.Key.Key_F7: scrcpy.KEYCODE_F7,
        Qt.Key.Key_F8: scrcpy.KEYCODE_F8,
        Qt.Key.Key_F9: scrcpy.KEYCODE_F9,
        Qt.Key.Key_F10: scrcpy.KEYCODE_F10,
        Qt.Key.Key_F11: scrcpy.KEYCODE_F11,
        Qt.Key.Key_F12: scrcpy.KEYCODE_F12,
        Qt.Key.Key_BracketLeft: scrcpy.KEYCODE_LEFT_BRACKET,
        Qt.Key.Key_BracketRight: scrcpy.KEYCODE_RIGHT_BRACKET,
        Qt.Key.Key_Backslash: scrcpy.KEYCODE_BACKSLASH,
        Qt.Key.Key_Semicolon: scrcpy.KEYCODE_SEMICOLON,
        Qt.Key.Key_Apostrophe: scrcpy.KEYCODE_APOSTROPHE,
        Qt.Key.Key_Slash: scrcpy.KEYCODE_SLASH,
        Qt.Key.Key_ScrollLock: scrcpy.KEYCODE_SCROLL_LOCK,
        Qt.Key.Key_Pause: scrcpy.KEYCODE_BREAK,
        Qt.Key.Key_Insert: scrcpy.KEYCODE_INSERT,
        Qt.Key.Key_Home: scrcpy.KEYCODE_MOVE_HOME,
        Qt.Key.Key_PageUp: scrcpy.KEYCODE_PAGE_UP,
        Qt.Key.Key_Delete: scrcpy.KEYCODE_FORWARD_DEL,
        Qt.Key.Key_End: scrcpy.KEYCODE_MOVE_END,
        Qt.Key.Key_PageDown: scrcpy.KEYCODE_PAGE_DOWN,
        Qt.Key.Key_Up: scrcpy.KEYCODE_DPAD_UP,
        Qt.Key.Key_Down: scrcpy.KEYCODE_DPAD_DOWN,
        Qt.Key.Key_Left: scrcpy.KEYCODE_DPAD_LEFT,
        Qt.Key.Key_Right: scrcpy.KEYCODE_DPAD_RIGHT,
        Qt.Key.Key_Menu: scrcpy.KEYCODE_MENU,
        Qt.Key.Key_Control: scrcpy.KEYCODE_CTRL_LEFT,
        Qt.Key.Key_Shift: scrcpy.KEYCODE_SHIFT_LEFT,
        Qt.Key.Key_Alt: scrcpy.KEYCODE_ALT_LEFT,
    }
    if code in hard_code:
        return hard_code[code]

    print(f"Unknown keycode: {code}")
    return -1


if not QApplication.instance():
    app = QApplication([])
else:
    app = QApplication.instance()


class Frame(QObject):
    frame_signal = Signal(Device, object)

    def __init__(self, device) -> None:
        super(Frame, self).__init__()
        self.device = device

    def set_connect(self, slot):
        self.frame_signal.connect(slot)

    def post(self, frame):
        self.frame_signal.emit(self.device, frame)


class CCScrcpy(QMainWindow):
    def __init__(self):
        super(CCScrcpy, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.default_device_max_size = 240
        self.device_max_size = self.default_device_max_size
        self.device_max_col = 5

        self.devices, self.frames = self.get_device()

        self.stop_render_screen = False

        print(f"device {len(self.devices)}")

        # device 控制属性
        self.scale_ratio = [0.2, 0.4, 0.5, 0.8, 1.0, 1.2, 1.5, 1.8, 2.0]
        for i in range(len(self.scale_ratio)):
            self.ui.left_info_device_screen_scale.addItem(f"{self.scale_ratio[i]}")
        self.ui.left_info_device_screen_scale.setCurrentIndex(4)
        self.ui.left_info_device_screen_scale.currentIndexChanged.connect(
            self.__device_screen_scale_ratio
        )

        self.device_col = [1,2,3,4,5,6,7,8,9,10]
        for i in range(len(self.device_col)):
            self.ui.left_info_device_screen_col.addItem(f"{self.device_col[i]}")
        self.ui.left_info_device_screen_col.setCurrentIndex(4)
        self.ui.left_info_device_screen_col.currentIndexChanged.connect(
            self.__device_screen_col
        )

        # 帧更新信号
        for i in range(len(self.frames)):
            self.frames[i].set_connect(self.on_post)

        self.ui.update_left_info_device_grid(self.devices)
        self.reflash_device()

    def get_device(self):
        # print(f'adb device size:{len(adb.device_list())}')
        devices_list = adb.device_list()
        devices = [
            Device(
                serial=devices_list[i].serial,
                index=i,
                on_init=self.on_init,
                on_frame=self.on_frame,
            )
            for i in range(len(devices_list))
        ]
        frames = [Frame(device=devices[i]) for i in range(len(devices_list))]
        return devices, frames

    def reflash_device_screen(self):
        pass

    def __device_screen_scale_ratio(self, index):
        self.device_max_size = self.default_device_max_size * self.scale_ratio[index]
        self.__reflash_device_screen_on()
    
    def __device_screen_col(self, index):
        last_max_col = self.device_max_col
        self.device_max_col = self.device_col[index]
        if self.device_max_col >= len(self.devices) and last_max_col >= len(self.devices):
            return
        self.reflash_device()
        self.__reflash_device_screen_on()

    def reflash_device(self):
        self.stop_render_screen = True
        self.ui.update_right_device_screen_grid(
            self.devices,
            self.device_max_col,
            self.on_mouse_event(scrcpy.ACTION_DOWN),
            self.on_mouse_event(scrcpy.ACTION_MOVE),
            self.on_mouse_event(scrcpy.ACTION_UP),
            self.on_key_event(scrcpy.ACTION_DOWN),
            self.on_key_event(scrcpy.ACTION_UP),
        )
        self.stop_render_screen = False
    
    def __reflash_device_screen_on(self):
        for i in range(len(self.devices)):
            self.devices[i].on_click_screen()

    def on_init(self, device: Device):
        print(f"on_init {device.client.device_name}")

    def on_frame(self, device: Device, frame):
        app.processEvents()
        if self.stop_render_screen:
            return
        self.frames[device.index].post(frame)

    def on_post(self, device: Device, frame):
        self.display_device_screen(
            frame,
            self.__get_device_ratio(device),
            self.ui.device_screen_list[device.index],
        )

    def display_device_screen(self, frame, ratio, screen_ui):
        image = QImage(
            frame,
            frame.shape[1],
            frame.shape[0],
            frame.shape[1] * 3,
            QImage.Format_BGR888,
        )
        pix = QPixmap(image)
        pix.setDevicePixelRatio(1 / ratio)
        screen_ui.setPixmap(pix)
        self.resize(1, 1)

    def on_mouse_event(self, action=scrcpy.ACTION_DOWN):
        def handler1(device: Device):
            def handler(evt: QMouseEvent):
                # focused_widget = QApplication.focusWidget()
                # if focused_widget is not None:
                #     focused_widget.clearFocus()

                ratio = self.__get_device_ratio(device)
                device.client.control.touch(
                    evt.position().x() / ratio, evt.position().y() / ratio, action
                )

            return handler

        return handler1

    def on_key_event(self, action=scrcpy.ACTION_DOWN):
        def handler1(device: Device):
            def handler(evt: QKeyEvent):
                code = map_code(evt.key())
                if code != -1:
                    device.client.control.keycode(code, action)

            return handler

        return handler1

    def start(self):
        for i in range(len(self.devices)):
            self.devices[i].start()

    def closeEvent(self, _):
        print(f"app close")
        for i in range(len(self.devices)):
            self.devices[i].exit()

    def __get_device_ratio(self, device: Device):
        ratio = 1
        if device.client.resolution[0] < device.client.resolution[1]:
            # 竖屏
            ratio = self.device_max_size / device.client.resolution[0]
        else:
            ratio = self.device_max_size / device.client.resolution[1]
        return ratio


def main():
    cc = CCScrcpy()
    cc.show()
    cc.start()
    app.exec()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"running error:{e}")
