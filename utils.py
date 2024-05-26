# coding: utf8
from dataclasses import dataclass
from PySide6 import QtWidgets


@dataclass
class PluginInfo(object):
    id: str
    name: str
    enable: bool
    widget: QtWidgets.QWidget


class AbstractPluginWidget(QtWidgets.QWidget):

    def update_browser(self, browser: str, local_state_data: dict):
        raise NotImplementedError
