from threading import Thread
from typing import Any, Callable

import scrcpy
from adbutils import adb

from view.cc_frame import Frame


class Device:
    ACTION_DOWN = 0
    ACTION_UP = 1
    ACTION_MOVE = 2

    def __init__(
        self,
        # 设备序列号
        serial: str,
        name: str = None,
        on_init: Callable[..., Any] = None,
        on_frame: Callable[..., Any] = None,
    ) -> None:
        self.serial = serial
        if name is not None:
            self.name = name
        else:
            self.name = serial

        self.on_init_listener = on_init
        self.on_frame_listener = on_frame

        # 设置 client
        self.device = adb.device(serial=self.serial)
        self.client = scrcpy.Client(device=self.device)

        self.client.add_listener(scrcpy.EVENT_INIT, self.__on_init)
        self.client.add_listener(scrcpy.EVENT_FRAME, self.__on_frame)

        self.started = False
        self.thread = None

    def __on_init(self):
        print(f"device:{self.client.device_name}, resolution:{self.client.resolution}")
        if self.on_init_listener is not None:
            self.on_init_listener(
                self.serial, self.client.device_name, self.client.resolution
            )

    def __on_frame(self, frame):
        if frame is not None and self.on_frame_listener is not None:
            self.on_frame_listener(self.serial, frame)

    def __run(self):
        print(f"{self.thread.name} start")
        self.client.start()
        while self.started:
            self.client.start()
        print(f"{self.thread.name} end")

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

    def on_click_screen(self):
        self.client.control.back_or_turn_screen_on()

    def on_send_text(self, str):
        self.client.control.text(str)


class ScreenDevice:
    def __init__(
        self,
        device: Device,
        frame: Frame,
        on_post: Callable[..., Any],
        ratio=None,
    ) -> None:
        self.device = device
        self.frame = frame
        self.frame.set_connect(on_post)

        self.ratio = 1
        if ratio is not None:
            self.ratio = ratio

        self.online = True

    def set_online(self, online):
        self.online = online

    def post_frame(self, frame):
        if self.online:
            self.frame.post(frame)

    def update_ratio(self, device_max_size):
        if self.online:
            if self.device.client.resolution[0] < self.device.client.resolution[1]:
                # 竖屏
                self.ratio = device_max_size / self.device.client.resolution[0]
            else:
                self.ratio = device_max_size / self.device.client.resolution[1]
        else:
            self.ratio = 1


class DeviceManager:
    def __init__(
        self,
        on_init: Callable[..., Any] = None,
        on_frame: Callable[..., Any] = None,
        on_post: Callable[..., Any] = None,
        on_devices_changed: Callable[..., Any] = None,
    ) -> None:
        self.on_init = on_init
        self.on_frame = on_frame
        self.on_post = on_post
        self.on_devices_changed = on_devices_changed

        self.screen_devices = self.__load_devices()  # 在线设备

        self.__start_monitor()

    def __start_monitor(self):
        self.thread = Thread(
            target=self.__run, name=f"device_monitor_thread", daemon=True
        )
        self.thread.start()

    def __run(self):
        print(f"{self.thread.name} start")
        # 监控设备连接 track-devices
        try:
            for event in adb.track_devices():
                print(
                    f"device:{event.serial} present:{event.present} status:{event.status}"
                )

                if (event.present and event.status == "device") or (
                    not event.present and event.status == "absent"
                ):
                    self.__on_devices_status_changed(
                        event.serial, event.present and event.status == "device"
                    )
                    # # 通知外部
                    # self.on_devices_changed(
                    #     event.serial, event.present and event.status == "device"
                    # )
        except:
            pass
        print(f"{self.thread.name} end")

    def __on_devices_status_changed(self, serial, online):
        if serial in self.screen_devices:
            device = self.screen_devices[serial]
            if online and not device.online:
                print(f"{serial} online")
                device.set_online(True)
                # 尝试开启帧
            elif not online and device.online:
                print(f"{serial} offline")
                device.set_online(False)
                # 尝试关闭帧
        elif online:
            device = self.__create_screen_device(serial)
            self.screen_devices[serial] = device
            device.set_online(False)

    def __create_screen_device(self, serial):
        return ScreenDevice(
            device=Device(serial=serial, on_init=self.on_init, on_frame=self.on_frame),
            frame=Frame(serial),
        )

    def post_frame(self, serial, frame):
        self.screen_devices[serial].post_frame(frame)

    def __load_devices(self):
        return {
            d.serial: ScreenDevice(
                device=Device(
                    serial=d.serial, on_init=self.on_init, on_frame=self.on_frame
                ),
                frame=Frame(d.serial),
            )
            for d in adb.device_list()
        }

    # def get_device_num(self):
    #     return len(self.get_devices())

    # def get_devices(self) -> list[ScreenDevice]:
    #     return self.devices

    # def refresh_device_screen_on(self):
    #     for i in range(len(self.devices)):
    #         self.devices[i].on_click_screen()
