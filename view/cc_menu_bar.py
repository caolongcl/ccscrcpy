# -*- coding: utf-8 -*-

from PySide6.QtCore import *  # type: ignore
from PySide6.QtGui import *  # type: ignore
from PySide6.QtWidgets import *
from typing import Any, Callable


class _DeviceColMenu(QMenu):
    def __init__(self, parent, on_col_changed: Callable[..., Any]) -> None:
        super().__init__(f"手机列数", parent)

        device_cols = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        for i in range(len(device_cols)):
            action = QAction(f"{device_cols[i]}", parent)
            action.setData(device_cols[i])
            self.addAction(action)
            action.triggered.connect(self.__on_col_changed(action, on_col_changed))

    def __on_col_changed(self, action, on_col_changed: Callable[..., Any]):
        def _on_col_changed(self):
            on_col_changed(action.data())

        return _on_col_changed


class _DeviceScaleRatioMenu(QMenu):
    def __init__(self, parent, on_scale_ratio_changed: Callable[..., Any]) -> None:
        super().__init__(f"手机屏幕缩放 1.0", parent)

        scale_ratios = [0.2, 0.4, 0.5, 0.8, 1.0, 1.2, 1.5, 1.8, 2.0]
        for i in range(len(scale_ratios)):
            action = QAction(f"{scale_ratios[i]}", parent)
            action.setData(scale_ratios[i])
            print(f"ratio___{action.data()}")
            self.addAction(action)
            action.triggered.connect(
                self.__on_scale_ratio_changed(action, on_scale_ratio_changed)
            )

    def __on_scale_ratio_changed(
        self, action, on_scale_ratio_changed: Callable[..., Any]
    ):  
        menu = self
        def _on_scale_ratio_changed(self):
            on_scale_ratio_changed(action.data())
            menu.setTitle(f'手机屏幕缩放{action.data()}')
        return _on_scale_ratio_changed


class MenuBar(QMenuBar):
    def __init__(self, parent) -> None:
        super().__init__(parent)

        self.menu_settings = QMenu(f"设置", self)
        self.addAction(self.menu_settings.menuAction())

    def add_device_col_menu(self, on_col_changed: Callable[..., Any]):
        # device col
        self.device_col = _DeviceColMenu(self.menu_settings, on_col_changed)
        self.menu_settings.addMenu(self.device_col)

    def add_device_scale_ratio_menu(self, on_scale_ratio_changed: Callable[..., Any]):
        # device scale ratio
        self.device_scale_ratio = _DeviceScaleRatioMenu(
            self.menu_settings, on_scale_ratio_changed
        )
        self.menu_settings.addMenu(self.device_scale_ratio)
