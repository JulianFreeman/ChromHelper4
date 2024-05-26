# coding: utf8
from PySide6 import QtWidgets, QtCore

from utils import PluginInfo

PluginIdRole = 0x0101


class DaPluginMgr(QtWidgets.QDialog):

    def __init__(self, plugins: dict[str, PluginInfo], parent=None):
        super().__init__(parent)
        self.setWindowTitle("插件管理")
        self.plugins = plugins

        # ------------------- UI ------------------------

        self.hly_m = QtWidgets.QHBoxLayout()
        self.setLayout(self.hly_m)

        self.lw_plugins = QtWidgets.QListWidget(self)
        self.lw_plugins.setSelectionMode(QtWidgets.QListWidget.SelectionMode.SingleSelection)
        self.hly_m.addWidget(self.lw_plugins)

        self.vly_buttons = QtWidgets.QVBoxLayout()
        self.hly_m.addLayout(self.vly_buttons)

        self.pbn_install = QtWidgets.QPushButton("安装插件", self)
        self.pbn_uninstall = QtWidgets.QPushButton("卸载插件", self)
        self.vly_buttons.addWidget(self.pbn_install)
        self.vly_buttons.addWidget(self.pbn_uninstall)
        self.vly_buttons.addStretch(1)
        self.pbn_save = QtWidgets.QPushButton("保存", self)
        self.pbn_cancel = QtWidgets.QPushButton("取消", self)
        self.vly_buttons.addWidget(self.pbn_save)
        self.vly_buttons.addWidget(self.pbn_cancel)

        self.hly_m.setStretch(0, 3)
        self.hly_m.setStretch(1, 1)

        # ------------------- end UI --------------------

        for pid in self.plugins:
            plugin = self.plugins[pid]
            lw_item = QtWidgets.QListWidgetItem(plugin.name, self.lw_plugins)
            lw_item.setCheckState(QtCore.Qt.CheckState.Checked
                                  if plugin.enable else QtCore.Qt.CheckState.Unchecked)
            lw_item.setData(PluginIdRole, pid)

        self.pbn_save.clicked.connect(self.on_pbn_save_clicked)
        self.pbn_cancel.clicked.connect(self.on_pbn_cancel_clicked)

    def sizeHint(self):
        return QtCore.QSize(360, 360)

    def on_pbn_save_clicked(self):
        for i in range(self.lw_plugins.count()):
            item = self.lw_plugins.item(i)
            pid = item.data(PluginIdRole)
            enable = item.checkState() == QtCore.Qt.CheckState.Checked
            self.plugins[pid].enable = enable

        self.accept()

    def on_pbn_cancel_clicked(self):
        self.reject()
