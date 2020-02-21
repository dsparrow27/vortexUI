import os
from functools import partial

from Qt import QtCore, QtWidgets, QtGui
from zoo.libs.plugin import pluginmanager
from vortex.ui import plugin


class UIApplication(QtCore.QObject):
    # from api to ui signals
    onNewNodeRequested = QtCore.Signal(dict)
    onNodeDeleteRequested = QtCore.Signal(object)
    onBeforeRemoveTab = QtCore.Signal(object)
    onAfterRemoveTab = QtCore.Signal(object)
    onSelectionChanged = QtCore.Signal(object, bool)

    def __init__(self, uiConfig):
        """
        :param uiConfig:
        :type uiConfig:
        """
        super(UIApplication, self).__init__()
        self.pluginManager = pluginmanager.PluginManager(plugin.UIPlugin, variableName="id")
        self.pluginManager.registerPaths(os.environ["VORTEX_UI_PLUGINS"].split(os.pathsep))
        self.config = uiConfig
        self._keyBoardMapping = {}
        self.models = {}
        self.currentModel = None

    def loadUIPlugin(self, pluginId, dock=True):
        # pass
        uiExt = self.pluginManager.loadPlugin(pluginId, application=self)
        if not uiExt:
            return
        uiExt.initUI(dock=dock)
        return uiExt

    def loadPlugins(self):
        for uiPlugin in self.pluginManager.plugins.values():
            if uiPlugin.autoLoad:
                self.loadUIPlugin(uiPlugin.id)

    def mainWindow(self):

        for wid in QtWidgets.QApplication.topLevelWidgets():
            if wid.objectName() == "VortexMainWindow":
                return wid

    def customToolbarActions(self, parent):
        pass

    def onNodeCreated(self, Type):
        pass

    def createContextMenu(self, objectModel):
        pass

    def initialize(self):
        pass

    def registeredNodes(self):
        """Returns a full list of registered nodes

        :return:
        :rtype: list(str)
        """
        return []

    def setShortcutForWidget(self, widget, name):
        keymap = self._keyBoardMapping.get(name)
        if not keymap:
            return

        for k, command in keymap:
            if command:
                QtWidgets.QShortcut(QtGui.QKeySequence(k), widget, partial(self.executeCommand, widget, command))

    def executeCommand(self, widget, command):
        print("executingCommand", widget, command)

    def save(self, filePath):
        print ("saving", filePath)

    def load(self, filePath):
        print("loading", filePath)

