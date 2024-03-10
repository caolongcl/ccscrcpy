from threading import Thread
from typing import Any, Callable, Optional

import scrcpy
from adbutils import adb

from view.cc_frame import Frame


class Device:
    ACTION_DOWN = 0
    ACTION_UP = 1
    ACTION_MOVE = 2

    def __init__(
        self,
        index: int,
        serial: str,
        name: Optional[str | None],
        on_init: Callable[..., Any],
        on_frame: Callable[..., Any],
        on_post: Callable[..., Any],
    ) -> None:
        self.index = index
        self.serial = serial
        if name is not None:
            self.name = name
        else:
            self.name = serial

        self.frame = Frame()
        self.frame.set_connect(lambda frame: on_post(self, frame))

        self.on_init_listener = on_init
        self.on_frame_listener = on_frame

        # 设置 client
        self.device = adb.device(serial=self.serial)
        self.client = scrcpy.Client(device=self.device)

        self.client.add_listener(scrcpy.EVENT_INIT, self.__on_init)
        self.client.add_listener(scrcpy.EVENT_FRAME, self.__on_frame)

        self.started = False
        self.thread = None

        self.ratio = 1
        self.online = True

    def __on_init(self):
        print(f"device:{self.client.device_name}, resolution:{self.client.resolution}")
        if self.on_init_listener is not None:
            self.on_init_listener(self)

    def __on_frame(self, frame):
        if frame is not None and self.on_frame_listener is not None:
            self.on_frame_listener(self, frame)

    def __run(self):
        print(f"{self.thread.name} start")
        self.client.start()
        while self.started:
            self.client.start()
        print(f"{self.thread.name} end")

    def set_online(self, online):
        self.online = online

    def post_frame(self, frame):
        if self.online:
            self.frame.post(frame)

    def update_ratio(self, device_max_size):
        if self.online:
            if self.client.resolution[0] < self.client.resolution[1]:
                # 竖屏
                self.ratio = device_max_size / self.client.resolution[0]
            else:
                self.ratio = device_max_size / self.client.resolution[1]
        else:
            self.ratio = 1

    def start_frame(self):
        if self.started:
            print(f"device:{self.client.device_name} already start")
            return
        self.started = True
        self.thread = Thread(target=self.__run, name=f"device_thread_{self.serial}")
        self.thread.start()

    def stop_frame(self):
        if not self.started:
            print(f"device:{self.client.device_name} already exit")
            return
        self.started = False
        self.client.stop()
        self.thread.join()

    def on_click_home(self):
        self.client.control.keycode(scrcpy.KEYCODE_HOME, scrcpy.ACTION_DOWN)
        self.client.control.keycode(scrcpy.KEYCODE_HOME, scrcpy.ACTION_UP)

    def on_click_back(self):
        self.client.control.keycode(scrcpy.KEYCODE_BACK, scrcpy.ACTION_DOWN)
        self.client.control.keycode(scrcpy.KEYCODE_BACK, scrcpy.ACTION_UP)

    def on_click_recent(self):
        self.client.control.keycode(scrcpy.KEYCODE_APP_SWITCH, scrcpy.ACTION_DOWN)
        self.client.control.keycode(scrcpy.KEYCODE_APP_SWITCH, scrcpy.ACTION_UP)

    def touch(self, x, y, action):
        self.client.control.touch(x / self.ratio, y / self.ratio, action)

    def keycode(self, code, action):
        self.client.control.keycode(code, action)

    def get_clipboard(self):
        return self.client.control.get_clipboard()

    def set_clipboard(self, text, paste=True):
        self.client.control.set_clipboard(text, paste)

    def on_click_screen(self):
        self.client.control.back_or_turn_screen_on()

    def on_send_text(self, str):
        self.client.control.text(str)


class DeviceManager:
    def __init__(
        self,
        on_init: Callable[..., Any],
        on_frame: Callable[..., Any],
        on_post: Callable[..., Any],
        on_devices_changed: Callable[..., Any] = None,
    ) -> None:
        self.on_init = on_init
        self.on_frame = on_frame
        self.on_post = on_post
        self.on_devices_changed = on_devices_changed

        self.index = -1

        self.devices = self.__load_devices()  # 在线设备
        print(f"device num {len(self.devices)}")

        # self.__start_monitor()

    def start(self):
        for device in self.devices:
            device.start_frame()

    def stop(self):
        for device in self.devices:
            device.stop_frame()

    # def __start_monitor(self):
    #     self.thread = Thread(
    #         target=self.__run, name=f"device_monitor_thread", daemon=True
    #     )
    #     self.thread.start()

    # def __run(self):
    #     print(f"{self.thread.name} start")
    #     # 监控设备连接 track-devices
    #     try:
    #         for event in adb.track_devices():
    #             print(
    #                 f"device:{event.serial} present:{event.present} status:{event.status}"
    #             )

    #             if (event.present and event.status == "device") or (
    #                 not event.present and event.status == "absent"
    #             ):
    #                 self.__on_devices_status_changed(
    #                     event.serial, event.present and event.status == "device"
    #                 )
    #                 # # 通知外部
    #                 # self.on_devices_changed(
    #                 #     event.serial, event.present and event.status == "device"
    #                 # )
    #     except:
    #         pass
    #     print(f"{self.thread.name} end")

    # # 设备状态改变
    # def __on_devices_status_changed(self, serial, online):
    #     if serial in self.screen_devices:
    #         device = self.screen_devices[serial]
    #         if online and not device.online:
    #             print(f"{serial} online")
    #             device.set_online(True)
    #             # 尝试开启帧
    #         elif not online and device.online:
    #             print(f"{serial} offline")
    #             device.set_online(False)
    #             # 尝试关闭帧
    #     elif online:
    #         device = self.__create_screen_device(serial)
    #         self.screen_devices[serial] = device
    #         device.set_online(False)

    # 根据序列号创建逻辑设备
    def __create_screen_device(self, serial):
        self.index += 1
        return Device(
            index=self.index,
            serial=serial,
            name="",
            on_init=self.on_init,
            on_frame=self.on_frame,
            on_post=self.on_post,
        )

    # 加载当前在线设备
    def __load_devices(self):
        devices = [self.__create_screen_device(d.serial) for d in adb.device_list()]
        devices.sort(key=lambda d: d.index)
        return devices

    def get_device_num(self):
        return len(self.devices)

    def get_devices(self):
        return self.devices

    def update_ratio(self, device: Device, device_max_size):
        device.update_ratio(device_max_size)

    def update_ratios(self, device_max_size):
        for d in self.devices:
            d.update_ratio(device_max_size)

    def refresh_device_screen_on(self):
        for d in self.devices:
            d.on_click_screen()
