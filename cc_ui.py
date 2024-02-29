# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'cc.ui'
##
## Created by: Qt User Interface Compiler version 6.5.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import *  # type: ignore
from PySide6.QtGui import *  # type: ignore
from PySide6.QtWidgets import *
from typing import Any, Callable

from model.device import Device  # type: ignore


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName("CCScrcpy")
        MainWindow.resize(400, 400)

        # 基本容器
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.main_layout = QHBoxLayout(self.centralwidget)
        self.main_layout.setContentsMargins(1, 1, 1, 1)

        # 左边栏：显示信息和控制
        self.left_info_group_box = QGroupBox()
        self.main_layout.addWidget(self.left_info_group_box)
        self.left_info_group_box.setFixedWidth(140)

        # 设备列表
        self.left_info = QVBoxLayout()
        self.left_info_group_box.setLayout(self.left_info)
        self.left_info.setContentsMargins(2, 2, 2, 2)

        self.left_info_device_group_box = QGroupBox(f"设备列表")
        self.left_info_device = QVBoxLayout()
        self.left_info_device.setSpacing(4)
        self.left_info_device.setContentsMargins(2, 2, 2, 2)
        self.left_info_device_group_box.setLayout(self.left_info_device)
        self.left_info.addWidget(self.left_info_device_group_box)

        # 设备列表 grid
        self.left_info_device_grid = QGridLayout()
        self.left_info_device_grid.setSpacing(4)
        self.left_info_device_grid.setContentsMargins(2, 2, 2, 2)

        self.left_info_device.addLayout(self.left_info_device_grid)
        self.left_info_device.addItem(
            QSpacerItem(
                0, 0, hData=QSizePolicy.Policy.Maximum, vData=QSizePolicy.Policy.Maximum
            )
        )

        self.device_list = []

        # 设备控制
        self.left_info_device_control_group_box = QGroupBox(f"属性")
        self.left_info_device_control_layout = QVBoxLayout()
        self.left_info_device_control_group_box.setLayout(self.left_info_device_control_layout)
        self.left_info.addWidget(self.left_info_device_control_group_box)
        layout = QHBoxLayout()
        layout.addWidget(QLabel(f'缩放'))
        self.left_info_device_screen_scale = QComboBox()
        layout.addWidget(self.left_info_device_screen_scale)
        self.left_info_device_control_layout.addLayout(layout)

        layout = QHBoxLayout()
        layout.addWidget(QLabel(f'列数'))
        self.left_info_device_screen_col = QComboBox()
        layout.addWidget(self.left_info_device_screen_col)
        self.left_info_device_control_layout.addLayout(layout)

        # layout = QHBoxLayout()
        # layout.addWidget(QLabel(f'质量'))
        # self.left_info_device_screen_bitrate = QComboBox()
        # layout.addWidget(self.left_info_device_screen_bitrate)
        # self.left_info_device_control_layout.addLayout(layout)
        
        self.left_info.addStretch(-1)  # 空白占用空间，不拉伸

        # 右边栏：显示所有手机投屏
        self.right_device_screen_group_box = QGroupBox()
        self.main_layout.addWidget(self.right_device_screen_group_box)
        self.right_device_screen_grid = QGridLayout()
        self.right_device_screen_group_box.setLayout(self.right_device_screen_grid)
        self.right_device_screen_grid.setObjectName("device_screen_grid")
        self.right_device_screen_grid.setSpacing(4)
        self.right_device_screen_grid.setContentsMargins(4, 4, 4, 4)

        self.device_screen_list = []
        self.device_screen_list_box = []

        # 设置全部布局
        MainWindow.setCentralWidget(self.centralwidget)
        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)

    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(
            QCoreApplication.translate("MainWindow", "CCScrcpy v0.1.0", None)
        )

    # retranslateUi

    def update_left_info_device_grid(self, device_model_list: list[Device]):
        if len(device_model_list) <= 0:
            print(f"update_left_info_device_grid empty device")
            return

        if len(self.device_list) > 0:
            for i in range(len(self.device_list)):
                self.left_info_device_grid.removeWidget(self.device_list[i])
        self.device_list = []

        # 更新
        max_col = 3
        row = 0
        col = 0

        for i in range(len(device_model_list)):
            device = device_model_list[i]
            row = i // max_col
            col = i % max_col
            device_label = QLabel(f"【{i+1:02d}】")
            device_label.setFixedSize(40, 30)
            self.device_list.append(device_label)
            self.left_info_device_grid.addWidget(
                device_label,
                row,
                col,
                Qt.AlignmentFlag.AlignCenter,
            )

        # for i in range(20):
        #     row = i // max_col
        #     col = i % max_col
        #     device_label = QLabel(f"【{i+1:02d}】")
        #     device_label.setFixedSize(40, 30)
        #     self.device_list.append(device_label)
        #     self.left_info_device_grid.addWidget(
        #         device_label,
        #         row,
        #         col,
        #         Qt.AlignmentFlag.AlignCenter,
        #     )
        
    def update_right_device_screen_grid(
        self,
        device_model_list: list[Device],
        device_col,
        mousePressEvent: Callable[..., Any],
        mouseMoveEvent: Callable[..., Any],
        mouseReleaseEvent: Callable[..., Any],
        keyPressEvent: Callable[..., Any],
        keyReleaseEvent: Callable[..., Any],
    ):
        if len(self.device_screen_list_box) > 0:
            for i in range(len(self.device_screen_list_box)):
                self.right_device_screen_grid.removeWidget(self.device_screen_list_box[i])
                self.device_screen_list_box[i].deleteLater()
            self.right_device_screen_grid.removeItem(
                self.right_device_screen_grid_space_item
            )
            # self.right_device_screen_grid_space_item.deleteLater()
        self.device_screen_list = []
        self.device_screen_list_box = []

        # 更新
        max_col = device_col
        row = 0
        col = 0

        for i in range(len(device_model_list)):
            device = device_model_list[i]
            row = i // max_col
            col = i % max_col

            device_screen_box = QGroupBox(
                f"【{device.index+1:02d}】序列号:{device.serial}"
            )
            self.device_screen_list_box.append(device_screen_box)

            device_screen_layout = QVBoxLayout()
            device_screen_layout.setContentsMargins(0, 0, 0, 0)
            device_screen_box.setLayout(device_screen_layout)

            device_screen_label = QLabel()
            device_screen_layout.addWidget(
                device_screen_label, alignment=Qt.AlignmentFlag.AlignCenter
            )

            # Bind mouse event
            device_screen_label.mousePressEvent = mousePressEvent(device)
            device_screen_label.mouseMoveEvent = mouseMoveEvent(device)
            device_screen_label.mouseReleaseEvent = mouseReleaseEvent(device)

            # Bind key event
            device_screen_label.setFocusPolicy(Qt.StrongFocus)
            device_screen_label.keyPressEvent = keyPressEvent(device)
            device_screen_label.keyReleaseEvent = keyReleaseEvent(device)

            self.device_screen_list.append(device_screen_label)

            # other control
            device_screen_control_layout = QHBoxLayout()
            device_screen_control_layout.setSpacing(0)
            device_screen_control_layout.setContentsMargins(0,0,0,0)
            device_screen_layout.addLayout(device_screen_control_layout)

            screen_btn = QPushButton(f"亮屏")
            screen_btn.clicked.connect(device.on_click_screen)
            home_btn = QPushButton(f"桌面")
            home_btn.clicked.connect(device.on_click_home)
            back_btn = QPushButton(f"返回")
            back_btn.clicked.connect(device.on_click_back)
            apps_btn = QPushButton(f"最近")
            apps_btn.clicked.connect(device.on_click_recent)

            device_screen_control_layout.addItem(
                QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
            )
            device_screen_control_layout.addWidget(screen_btn)
            device_screen_control_layout.addWidget(back_btn)
            device_screen_control_layout.addWidget(home_btn)
            device_screen_control_layout.addWidget(apps_btn)
            device_screen_control_layout.addItem(
                QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
            )

            self.right_device_screen_grid.addWidget(
                device_screen_box,
                row,
                col,
                Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter,
            )

        self.right_device_screen_grid_space_item = QSpacerItem(
            0, 0, hData=QSizePolicy.Policy.Expanding, vData=QSizePolicy.Policy.Expanding
        )
        self.right_device_screen_grid.addItem(
            self.right_device_screen_grid_space_item,
            row + 1,
            col + 1,
            col + 1,
            row + 1,
        )
