# coding: utf8
import json
import importlib
from pathlib import Path
from PySide6 import QtWidgets, QtGui, QtCore

from da_data_path import DaDataPath
from da_plugin_mgr import DaPluginMgr

from utils import PluginInfo, AbstractPluginWidget


class UiMwChromHelper(object):

    def __init__(self, window: QtWidgets.QMainWindow):
        # self.sbr = window.statusBar()
        self.mbr = window.menuBar()
        self.cw = QtWidgets.QWidget(window)
        window.setCentralWidget(self.cw)

        self.act_browser_chrome = QtGui.QAction(QtGui.QIcon(":/images/chrome_32.png"), "Chrome", window)
        self.act_browser_edge = QtGui.QAction(QtGui.QIcon(":/images/edge_32.png"), "Edge", window)
        self.act_browser_brave = QtGui.QAction(QtGui.QIcon(":/images/brave_32.png"), "Brave", window)
        self.act_browser_chrome.setCheckable(True)
        self.act_browser_edge.setCheckable(True)
        self.act_browser_brave.setCheckable(True)
        # 保证子窗口的初始化成功
        self.act_browser_chrome.setChecked(True)
        self.acg_browsers = QtGui.QActionGroup(window)
        self.acg_browsers.setExclusive(True)
        self.acg_browsers.addAction(self.act_browser_chrome)
        self.acg_browsers.addAction(self.act_browser_edge)
        self.acg_browsers.addAction(self.act_browser_brave)

        self.menu_browsers = self.mbr.addMenu("浏览器")
        self.menu_browsers.addAction(self.act_browser_chrome)
        self.menu_browsers.addAction(self.act_browser_edge)
        self.menu_browsers.addAction(self.act_browser_brave)
        self.menu_browsers.addSeparator()
        self.act_update_browser_data = QtGui.QAction("更新用户数据", window)
        self.menu_browsers.addAction(self.act_update_browser_data)

        self.act_data_path = QtGui.QAction("数据路径", window)
        self.act_plugin_mgr = QtGui.QAction("插件管理", window)
        self.menu_settings = self.mbr.addMenu("设置")
        self.menu_settings.addAction(self.act_data_path)
        self.menu_settings.addAction(self.act_plugin_mgr)

        self.act_about = QtGui.QAction("关于", window)
        self.act_about_qt = QtGui.QAction("关于 Qt", window)
        self.menu_about = self.mbr.addMenu("关于")
        self.menu_about.addAction(self.act_about)
        self.menu_about.addAction(self.act_about_qt)

        self.vly_cw = QtWidgets.QVBoxLayout()
        self.cw.setLayout(self.vly_cw)

        self.tw_main = QtWidgets.QTabWidget(window)
        self.vly_cw.addWidget(self.tw_main)


class MwChromHelper(QtWidgets.QMainWindow):

    def __init__(self, version: tuple[int, ...], parent=None):
        super().__init__(parent)
        self.version = version
        self.setWindowTitle("Chromium 核心浏览器辅助工具 4")
        self.setWindowIcon(QtGui.QIcon(":/images/chromhelper_64.png"))
        self.ui = UiMwChromHelper(self)
        
        self.local_state_map: dict[str, dict] = {}
        self.enabled_tabs: dict[str, AbstractPluginWidget] = {}
        self.plugins: dict[str, PluginInfo] = self.read_plugins()
        # 这里的顺序是先创建控件，再调用更新函数更新数据，所以下面这个函数要在触发槽函数之前
        self.update_plugins()

        self.ui.act_data_path.triggered.connect(self.on_act_data_path_triggered)
        self.ui.act_plugin_mgr.triggered.connect(self.on_act_plugin_mgr_triggered)
        self.ui.act_about.triggered.connect(self.on_act_about_triggered)
        self.ui.act_about_qt.triggered.connect(self.on_act_about_qt_triggered)
        self.ui.act_update_browser_data.triggered.connect(self.on_act_update_browser_data_triggered)

        self.ui.acg_browsers.triggered.connect(self.on_acg_browsers_triggered)
        # 为了触发槽函数
        self.ui.act_browser_chrome.trigger()

    def read_plugins(self) -> dict[str, PluginInfo]:
        plugins_dir = QtCore.QDir(__file__)
        plugins_dir.cdUp()
        ok = plugins_dir.cd("plugins")
        if not ok:
            QtWidgets.QMessageBox.critical(self, "错误", "没有找到插件目录。")
            return {}

        plugins_file = Path(plugins_dir.filePath("plugins.json"))
        plugins_data: dict = json.loads(plugins_file.read_text(encoding="utf8"))
        if "plugins" not in plugins_data:
            QtWidgets.QMessageBox.critical(self, "错误", "插件目录配置文件有误。")
            return {}
        plugins_list: list[dict] = plugins_data["plugins"]
        plugins_info: dict[str, PluginInfo] = {}
        for plugin in plugins_list:
            try:
                plg_id = plugin["id"]
                plg_wg = importlib.import_module(f".{plg_id}", package="plugins").entry()
                plugins_info[plg_id] = PluginInfo(
                    id=plg_id,
                    name=plugin["name"],
                    enable=plugin["enable"],
                    widget=plg_wg,
                )
            except AttributeError:
                QtWidgets.QMessageBox.warning(self, "警告", f"导入插件 {plugin['name']} 出错。")
            except ModuleNotFoundError:
                QtWidgets.QMessageBox.warning(self, "警告", f"没有找到插件 {plugin['name']} 。")
            except KeyError:
                QtWidgets.QMessageBox.warning(self, "警告", "插件目录配置文件有误。")

        return plugins_info

    def update_plugins(self):
        for pid in self.plugins:
            plugin = self.plugins[pid]
            if plugin.enable and (pid not in self.enabled_tabs):
                tb_wg = plugin.widget(self)
                self.ui.tw_main.addTab(tb_wg, plugin.name)
                self.enabled_tabs[pid] = tb_wg
            elif (not plugin.enable) and (pid in self.enabled_tabs):
                idx = self.ui.tw_main.indexOf(self.enabled_tabs[pid])
                self.ui.tw_main.removeTab(idx)
                self.enabled_tabs.pop(pid).close()

    def sizeHint(self):
        return QtCore.QSize(860, 680)

    def on_act_data_path_triggered(self):
        da_data_path = DaDataPath(self)
        da_data_path.exec()

    def on_act_plugin_mgr_triggered(self):
        da_plugin_mgr = DaPluginMgr(self.plugins, self)
        da_plugin_mgr.exec()
        self.update_plugins()

    def on_act_about_triggered(self):
        msg = ("Chromium 核心浏览器辅助工具\n\n旨在更方便地对以 Chromium 为核心的浏览器"
               "进行快速设置、插件检查、书签检查、书签导出、追加插件等操作。\n\n"
               f"当前版本：v{self.version[0]}.{self.version[1]}.{self.version[2]}，发布日期：{self.version[-1]}")
        QtWidgets.QMessageBox.about(self, "关于", msg)

    def on_act_about_qt_triggered(self):
        QtWidgets.QMessageBox.aboutQt(self, "关于 Qt")

    def get_local_state_data(self, browser: str) -> dict:
        us = QtCore.QSettings()
        user_data_path = str(us.value(f"{browser}Data", ""))
        if len(user_data_path) == 0 or not Path(user_data_path).exists():
            QtWidgets.QMessageBox.critical(self, "错误", f"{browser} 的用户数据路径有误！")
            return {}
        local_state_file = Path(user_data_path, "Local State")
        if not local_state_file.exists():
            QtWidgets.QMessageBox.critical(self, "错误",
                                           f"无法找到 Local State 文件，请检查 {browser} 的用户数据路径.")
            return {}

        return json.loads(local_state_file.read_text(encoding="utf8"))

    def on_acg_browsers_triggered(self, action: QtGui.QAction):
        browser = action.text()
        if browser not in self.local_state_map:
            local_state_data = self.get_local_state_data(browser)
            if len(local_state_data) == 0:
                return
            self.local_state_map[browser] = local_state_data

        for pid in self.enabled_tabs:
            tb_wg = self.enabled_tabs[pid]
            tb_wg.update_browser(browser, self.local_state_map[browser])

    def get_current_browser(self) -> str:
        action = self.ui.acg_browsers.checkedAction()
        return action.text()

    def on_act_update_browser_data_triggered(self):
        browser = self.get_current_browser()
        local_state_data = self.get_local_state_data(browser)
        if len(local_state_data) == 0:
            return
        self.local_state_map[browser] = local_state_data
