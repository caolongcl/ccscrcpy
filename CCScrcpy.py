import time

from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import *

import scrcpy
from view.dialog import DeviceNameModifyDialog

# cc
from view.settings import DeviceNameSettings
from view.cc_ui import *
from view.cc_com import resource_path
from model.device import *
from model.config import *


def map_code(code):
    """
    Map qt keycode to android keycode

    Args:
        code: qt keycode
        android keycode, -1 if not founded
    """

    # print(f"keycode: {code}")

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


class CCScrcpy(QMainWindow):
    def __init__(self, app: QApplication):
        super(CCScrcpy, self).__init__()

        self.app = app
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.default_device_max_size = 240
        self.device_max_size = self.default_device_max_size
        self.device_max_col = 5

        self.stop_render_screen = False

        self.cur_devices = []
        self.focused_device = None

        # 初始化菜单
        self.ui.menu_bar.add_device_col_menu(self.__device_screen_col)
        self.ui.menu_bar.add_device_scale_ratio_menu(self.__device_screen_scale_ratio)
        # self.ui.menu_bar.add_request_screen_resize_menu(self.__request_screen_resize)
        # self.ui.menu_bar.add_modify_device_name_menu(self.__modify_device_name)

        # 初始化 view
        self.ui.right_view.attach(
            self.device_max_col,
            self.__on_mouse_event,
            self.__on_key_event,
        )
        self.ui.left_view.set_on_global_ctrl(self.__on_global_ctrl)

        self.resize(1, 1)

        # 设备管理
        self.device_manager = DeviceManager(
            self.__on_init,
            self.__on_frame,
            self.__on_post,
            self.__on_devices_changed,
            self.__device_name_get,
        )

        if ui_config_show_log:
            self.device_manager.set_print_log(
                lambda msg: self.ui.right_view.set_log(msg)
            )

    def __on_init(self, device: Device):
        print(
            f"on_init {device.serial}:{device.client.device_name}:{device.client.resolution}"
        )
        self.device_manager.update_ratio(device, self.device_max_size)
        self.ui.right_view.update_title(device)
        self.ui.left_view.update_device_name(device)

    def __on_frame(self, device: Device, frame):
        # print(f"__on_frame {device.serial}")
        self.app.processEvents()
        if self.stop_render_screen:
            return
        device.post_frame(frame)

    def __on_post(self, device, frame):
        # print(f"__on_post {device.serial}")
        self.ui.right_view.render_device_screen(device, frame)

    def __on_mouse_event(self, action=scrcpy.ACTION_DOWN):
        def handler1(device: Device):
            def handler(evt: QMouseEvent):
                # focused_widget = QApplication.focusWidget()
                # if focused_widget is not None:
                #     focused_widget.clearFocus()

                device.touch(evt.position().x(), evt.position().y(), action)
                if action == scrcpy.ACTION_DOWN:
                    # print(f'mouse index {device.index}')
                    self.ui.right_view.update_focused_status(device, self.cur_devices)
                    self.ui.left_view.update_cur_device(device)
                    self.focused_device = device
                    self.focused_device.on_click_screen()

            return handler

        return handler1

    def __on_key_event(self, action=scrcpy.ACTION_DOWN):
        def handler1(device: Device):
            def handler(evt: QKeyEvent):
                # 处理特殊键
                # print(f"modify {evt.modifiers()}, keycode {evt.key()} action {action}")
                if (
                    evt.modifiers() == Qt.KeyboardModifier.ControlModifier
                    and evt.key() == Qt.Key.Key_C
                ):
                    # print(f"device copy to clipboard")
                    device.keycode(scrcpy.KEYCODE_COPY, action)
                    time.sleep(0.3)  #
                    text_from_dclipboard = device.get_clipboard()
                    # print(f"copy:{text_from_dclipboard}")
                    self.__set_clipboard_text(text_from_dclipboard)
                elif (
                    evt.modifiers() == Qt.KeyboardModifier.ControlModifier
                    and evt.key() == Qt.Key.Key_V
                    and action == scrcpy.ACTION_DOWN
                ):
                    text_from_qclipboard = self.__get_clipboard_text()
                    # print(f"text_from_qclipboard: {text_from_qclipboard}")
                    device.set_clipboard(text_from_qclipboard)
                    # device.client.control.keycode(scrcpy.KEYCODE_PASTE, action)
                elif (
                    evt.modifiers() == Qt.KeyboardModifier.ControlModifier
                    and evt.key() == Qt.Key.Key_X
                    and action == scrcpy.ACTION_DOWN
                ):
                    print(f"device cut to clipboard")
                    device.keycode(scrcpy.KEYCODE_CUT, action)
                    time.sleep(0.3)  #
                    text_from_dclipboard = device.get_clipboard()
                    print(f"copy:{text_from_dclipboard}")
                    self.__set_clipboard_text(text_from_dclipboard)
                else:
                    code = map_code(evt.key())
                    # print(f'key {evt.text()}')
                    if code != -1:
                        device.keycode(code, action)

            return handler

        return handler1

    def __on_devices_changed(self, devices: list[Device]):
        self.cur_devices = devices
        self.stop_render_screen = True
        # left
        # 初始化设备列表
        self.ui.left_view.update_devices_num(devices)
        self.ui.left_view.update_devices_no(devices)

        # right
        if self.focused_device is not None and not self.focused_device.online:
            self.ui.right_view.clear_focused(self.focused_device)
            self.focused_device = None
            self.ui.left_view.update_cur_device(self.focused_device)
        self.ui.right_view.update_devices(devices)

        # 更新绘制状态
        self.device_manager.update_renders(devices)
        self.stop_render_screen = False

    def __device_name_get(self, serial):
        name_settings = DeviceNameSettings()
        return name_settings.read_device_name(serial)

    def __get_clipboard_text(self):
        clipboard = QApplication.clipboard()
        return clipboard.text()

    def __set_clipboard_text(self, text):
        clipboard = QApplication.clipboard()
        clipboard.setText(text)

    def __on_device_name_update(self, device):
        self.ui.right_view.update_title(device)

    def __modify_device_name(self):
        devices = self.device_manager.get_devices_info()
        dialog = DeviceNameModifyDialog(devices, self.__on_device_name_update)
        dialog.exec()

    def __device_screen_scale_ratio(self, ratio):
        last_device_max_size = self.device_max_size
        self.device_max_size = self.default_device_max_size * ratio
        if last_device_max_size == self.device_max_size:
            return

        self.device_manager.update_ratios(self.device_max_size)
        self.device_manager.refresh_device_screen_on()

    def __device_screen_col(self, col):
        if col == self.device_max_col:
            return
        self.device_max_col = col
        self.stop_render_screen = True
        self.ui.right_view.update_devices_by_col(self.device_max_col)
        self.stop_render_screen = False
        self.device_manager.refresh_device_screen_on()
    
    def __on_global_ctrl(self, action):
        if action == ui_global_ctrl_resize:
            self.resize(1, 1)
        elif action == ui_global_ctrl_rename:
            self.__modify_device_name()

    def closeEvent(self, _):
        print(f"app close")
        self.device_manager.stop()


def main():
    if not QApplication.instance():
        app = QApplication([])
    else:
        app = QApplication.instance()

    icon = QIcon(resource_path("res/icon.ico"))
    app.setWindowIcon(icon)
    cc = CCScrcpy(app)
    cc.show()
    app.exec()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"running error:{e}")
