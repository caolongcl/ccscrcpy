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
        # 设备列表号
        index: int,
        on_init: Callable[..., Any] = None,
        on_frame: Callable[..., Any] = None,
    ) -> None:
        self.serial = serial
        self.index = index
        self.on_init_listener = on_init
        self.on_frame_listener = on_frame

        # 设置 client
        self.device = adb.device(serial=self.serial)
        self.client = scrcpy.Client(device=self.device)

        self.client.add_listener(scrcpy.EVENT_INIT, self.on_init)
        self.client.add_listener(scrcpy.EVENT_FRAME, self.on_frame)

        self.started = False
        self.thread = Thread(target=self.__run, name=f"device_thread_{self.serial}")

    def __run(self):
        print(f"start thread:{self.thread.name}")
        self.client.start()
        while self.started:
            self.client.start()
        print(f"end thread:{self.thread.name}")

    def on_init(self):
        print(f"device:{self.client.device_name}, resolution:{self.client.resolution}")
        if self.on_init_listener is not None:
            self.on_init_listener(self.index)

    def on_frame(self, frame):
        if frame is not None and self.on_frame_listener is not None:
            self.on_frame_listener(self.index, frame)

    def start(self):
        if self.started:
            print(f"device:{self.client.device_name} already start")
            return
        self.started = True
        self.thread.start()

    def exit(self):
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


class DeviceManager:
    def __init__(
        self,
        on_init: Callable[..., Any] = None,
        on_frame: Callable[..., Any] = None,
        on_post: Callable[..., Any] = None,
    ) -> None:
        self.on_init = on_init
        self.on_frame = on_frame
        self.on_post = on_post

        self.devices = []
        self.frames = []
        #
        self.reload()

        self.__start_monitor()

    def __start_monitor(self):
        self.thread = Thread(target=self.__run, name=f"device_monitor_thread", daemon=True)
        self.thread.start()

    def __run(self):
        print(f"start thread:{self.thread.name}")
        # 监控设备连接 track-devices
        try:
            for event in adb.track_devices():
               print(event.present, event.serial, event.status)
        except:
            pass
        print(f"end thread:{self.thread.name}")

    def reload(self):
        # 检查设备
        self.devices, self.frames = self.__load_device()

        print(f"load device {len(self.devices)}")

        # 帧更新信号
        for i in range(len(self.frames)):
            self.frames[i].set_connect(self.on_post)

    def post_frame(self, device_index, frame):
        # print(f'post_frame {device_index}')
        self.frames[device_index].post(frame)

    def get_device_num(self):
        return len(self.get_devices())

    def __load_device(self):
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
        frames = [Frame(index=devices[i].index) for i in range(len(devices_list))]
        return devices, frames

    def get_devices(self) -> list[Device]:
        return self.devices

    def refresh_device_screen_on(self):
        for i in range(len(self.devices)):
            self.devices[i].on_click_screen()

    def get_device_ratio(self, device_max_size, device_index):
        ratio = 1
        device: Device = self.devices[device_index]
        if device.client.resolution[0] < device.client.resolution[1]:
            # 竖屏
            ratio = device_max_size / device.client.resolution[0]
        else:
            ratio = device_max_size / device.client.resolution[1]
        return ratio

    def start(self):
        for i in range(len(self.devices)):
            self.devices[i].start()

    def stop(self):
        for i in range(len(self.devices)):
            self.devices[i].exit()
