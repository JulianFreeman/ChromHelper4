# coding: utf8
from PySide6 import QtWidgets


class WgDemoPlugin1(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.pbn_1 = QtWidgets.QPushButton("Plugin1 Button", self)

    def update_browser(self, browser: str, local_state_data: dict):
        print(browser)
        print(len(local_state_data))


def entry():
    return WgDemoPlugin1
