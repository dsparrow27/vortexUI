import os

from Qt import QtCore, QtWidgets, QtGui
from zoo.libs.plugin import pluginmanager
from vortex.ui import plugin


class ApplicationEvents(QtCore.QObject):
    selectionChanged = QtCore.Signal(list)
    nodeDeleted = QtCore.Signal(list)
    nodeCreated = QtCore.Signal(list)


class UIApplication(QtCore.QObject):

    def __init__(self, uiConfig):
        self.pluginManager = pluginmanager.PluginManager(plugin.UIPlugin, variableName="id")
        self.pluginManager.registerPaths(os.environ["VORTEX_UI_PLUGINS"].split(os.pathsep))
        self.graphNoteBook = None
        self.config = uiConfig
        self.graphType = None
        self.events = ApplicationEvents()

    def mainWindow(self):
        for wid in QtWidgets.QApplication.topLevelWidgets():
            if wid.objectName() == "Vortex":
                return wid

    def loadUIPlugin(self, pluginId, dock=True):
        # pass
        uiExt = self.pluginManager.loadPlugin(pluginId, application=self)
        if not uiExt:
            return
        uiExt.initUI(dock=dock)
        return uiExt

    def uiPlugin(self, pluginId):
        return self.pluginManager.getPlugin(pluginId)

    def loadPlugins(self):
        for uiPlugin in self.pluginManager.plugins.values():
            if uiPlugin.autoLoad:
                self.loadUIPlugin(uiPlugin.id)

    def registerGraphType(self, objectType):
        self.graphType = objectType

    def createGraphFromPath(self, filePath, parent=None):
        if self.graphNoteBook is None:
            return
        elif self.graphType is None:
            return
        newGraphInstance = self.graphType(self)
        rootModel = newGraphInstance.loadFromPath(filePath, parent=parent)
        if rootModel is not None:
            self.graphNoteBook.addPage(newGraphInstance, rootModel)
            self.events.nodeCreated.emit(rootModel)
