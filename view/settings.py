from PySide6.QtCore import QSettings


class DeviceNameSettings:
    def __init__(self) -> None:
        self.filename = "ccsettings.ini"        

    def add_device_name(self, serial, name):
        self.__write(serial, name)

    def read_device_name(self, serial):
        return self.__read(serial)

    # 写入配置
    def __write(self, key, value):
        settings = QSettings(self.filename, QSettings.IniFormat)
        settings.setValue(key, value)

    # 读取配置
    def __read(self, key):
        settings = QSettings(self.filename, QSettings.IniFormat)
        return settings.value(key, "")
