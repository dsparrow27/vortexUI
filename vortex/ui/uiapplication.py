import os

from zoovendor.Qt import QtCore, QtWidgets, QtGui
from zoo.core.plugin import pluginmanager
from zoo.libs.pyqt import utils
from vortex.ui import plugin


class ApplicationEvents(QtCore.QObject):
    # events which the UI Plugins react on emitted by the view
    uiGraphDeleted = QtCore.Signal(object)
    uiGraphCreated = QtCore.Signal(object)
    uiNodesDeleted = QtCore.Signal(list)
    uiNodesCreated = QtCore.Signal(list)
    uiSelectionChanged = QtCore.Signal(list)


class UIApplication(QtCore.QObject):
    sigGraphCreated = QtCore.Signal(object)  # emitted by graph notebook
    sigGraphSaved = QtCore.Signal(str)
    sigSelectionChanged = QtCore.Signal(list)

    def __init__(self, uiConfig):
        super(UIApplication, self).__init__()
        self.pluginManager = pluginmanager.PluginManager([plugin.UIPlugin], variableName="id")
        self.pluginManager.registerPaths(os.environ["VORTEX_UI_PLUGINS"].split(os.pathsep))
        self.graphNoteBook = None  # type: None or vortex.ui.views.grapheditor.GraphEditor
        self.config = uiConfig
        self.graphType = None
        self.events = ApplicationEvents()

    def currentGraph(self):
        if self.graphNoteBook is None:
            raise RuntimeError("No graph currently created")
        editor = self.currentNetworkEditor()
        if not editor:
            return

        return editor.graph

    def currentNetworkEditor(self):
        if self.graphNoteBook is None:
            raise RuntimeError("No graph currently created")
        return self.graphNoteBook.currentEditor()

    def mainWindow(self):
        for wid in QtWidgets.QApplication.topLevelWidgets():
            for child in utils.iterChildren(wid):
                if child.objectName() == "Vortex":
                    return child

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
        raise NotImplementedError("Subclasses must implement this method")

    def createGraphFromPath(self, filePath, name=None, parent=None):
        raise NotImplementedError("Subclasses must implement this method")
