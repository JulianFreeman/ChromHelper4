# coding: utf8
from PySide6 import QtWidgets


class WgDemoPlugin2(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.cbx_1 = QtWidgets.QCheckBox("Plugin2 CheckBox", self)

    def update_browser(self, browser: str, local_state_data: dict):
        pass
