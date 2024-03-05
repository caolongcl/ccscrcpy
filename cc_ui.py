# -*- coding: utf-8 -*-

from PySide6.QtCore import *  # type: ignore
from PySide6.QtGui import *  # type: ignore
from PySide6.QtWidgets import *
from typing import Any, Callable

from model.device import Device  # type: ignore
from view.cc_left_view import LeftView
from view.cc_menu_bar import MenuBar
from view.cc_right_view import RightView


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName("CCScrcpy")
        MainWindow.resize(800, 600)

        # 菜单
        self.menu_bar = MenuBar(MainWindow)

        # 基本容器
        self.centralwidget = QWidget(MainWindow)
        self.main_layout = QHBoxLayout(self.centralwidget)
        self.main_layout.setContentsMargins(1, 1, 1, 1)

        self.left_view = LeftView()
        self.right_view = RightView()
        self.main_layout.addWidget(self.left_view)
        self.main_layout.addWidget(self.right_view)

        # 状态栏
        self.statusbar = QStatusBar(MainWindow)

        # 设置全部布局
        MainWindow.setMenuBar(self.menu_bar)
        MainWindow.setCentralWidget(self.centralwidget)
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)

    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(
            QCoreApplication.translate("MainWindow", "CCScrcpy", None)
        )

    # retranslateUi
