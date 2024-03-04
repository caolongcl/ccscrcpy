from PySide6.QtCore import *  # type: ignore
from PySide6.QtGui import *  # type: ignore
from PySide6.QtWidgets import *
from typing import Any, Callable

from model.device import Device  # type: ignore
from view.cc_left_view import *


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

        left_view = LeftView()
        self.main_layout.addWidget(left_view)
        left_view.update_device_num(10)

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

if not QApplication.instance():
    app = QApplication([])
else:
    app = QApplication.instance()


class CCScrcpy(QMainWindow):
    def __init__(self):
        super(CCScrcpy, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

    def closeEvent(self, _):
        print(f"app close")


def main():
    cc = CCScrcpy()
    cc.show()
    app.exec()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"running error:{e}")
