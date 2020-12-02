import os

from Qt import QtCore, QtWidgets, QtGui
from zoo.libs.plugin import pluginmanager
from vortex.ui import plugin


class ApplicationEvents(QtCore.QObject):
    # events which the UI Plugins react on, these should be used within the models and/or internal signals
    uiSelectionChanged = QtCore.Signal(list)
    uiNodesDeleted = QtCore.Signal(list)
    uiNodesCreated = QtCore.Signal(list)
    uiGraphDeleted = QtCore.Signal(object)
    # model events
    modelGraphSaved = QtCore.Signal(str)
    modelNodesCreated = QtCore.Signal(list)


class UIApplication(QtCore.QObject):

    def __init__(self, uiConfig):
        super(UIApplication, self).__init__()
        self.pluginManager = pluginmanager.PluginManager(plugin.UIPlugin, variableName="id")
        self.pluginManager.registerPaths(os.environ["VORTEX_UI_PLUGINS"].split(os.pathsep))
        self.graphNoteBook = None # type: None or slither.ui.views.grapheditor.GraphEditor
        self.config = uiConfig
        self.graphType = None
        self.events = ApplicationEvents()

    def currentGraph(self):
        if self.graphNoteBook is None:
            raise RuntimeError("No graph currently created")
        return self.graphNoteBook.currentEditor().graph

    def currentNetworkEditor(self):
        if self.graphNoteBook is None:
            raise RuntimeError("No graph currently created")
        return self.graphNoteBook.currentEditor()

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

    def createNewGraph(self, name=None):
        newGraphInstance = self.graphType(self, name=name)
        self.events.uiNodesCreated.emit([newGraphInstance.rootNode])
        self.graphNoteBook.addGraph(newGraphInstance, newGraphInstance.rootNode)

    def createGraphFromPath(self, filePath, name=None, parent=None):
        if self.graphNoteBook is None or self.graphType is None:
            return
        newGraphInstance = self.graphType(self, name=name or "NewGraph")
        models = newGraphInstance.loadFromPath(filePath, parent=parent)
        if models:
            newGraphInstance.rootNode = models[0]
            self.events.uiNodesCreated.emit(models)
            self.graphNoteBook.addGraph(newGraphInstance, models[0])
