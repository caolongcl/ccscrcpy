from threading import Thread
from typing import Any, Callable

import scrcpy
from adbutils import adb


class Device:
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
        self.listener_on_init = on_init
        self.listener_on_frame = on_frame

        # 设置 client
        self.device = adb.device(serial=self.serial)
        self.client = scrcpy.Client(device=self.device)

        self.client.add_listener(scrcpy.EVENT_INIT, self.on_init)
        self.client.add_listener(scrcpy.EVENT_FRAME, self.on_frame)

        self.started = False
        self.thread = Thread(target=self.__run, name=f'device_thread_{self.serial}')

    def __run(self):
        print(f'start thread:{self.thread.name}')
        self.client.start()
        while self.started:
            self.client.start()
        print(f'end thread:{self.thread.name}')
    
    def on_init(self):
        print(f"device:{self.client.device_name}, resolution:{self.client.resolution}")
        if self.listener_on_init is not None:
            self.listener_on_init(self)

    def on_frame(self, frame):
        if frame is not None and self.listener_on_frame is not None:
            self.listener_on_frame(self, frame)

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
    
    def on_click_screen_on(self):
        self.client.control.back_or_turn_screen_on()

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
