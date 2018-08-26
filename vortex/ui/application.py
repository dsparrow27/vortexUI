import os

from qt import QtCore, QtWidgets, QtGui
from vortex.ui import nodelibrary
from zoo.libs.plugin import pluginmanager
from vortex.ui import plugin


class UIApplication(QtCore.QObject):
    # from api to ui signals
    onNewNodeRequested = QtCore.Signal(dict)
    onNodeDeleteRequested = QtCore.Signal(object)
    onBeforeRemoveTab = QtCore.Signal(object)
    onAfterRemoveTab = QtCore.Signal(object)
    onSelectionChanged = QtCore.Signal(object, bool)

    def __init__(self, uiConfig, apiApplication):
        """
        :param uiConfig:
        :type uiConfig:
        :param apiApplication:
        :type apiApplication:
        """
        super(UIApplication, self).__init__()
        self._apiApplication = apiApplication
        self.pluginManager = pluginmanager.PluginManager(plugin.UIPlugin)
        self.pluginManager.registerPaths(os.environ["VORTEX_UI_PLUGINS"].split(os.pathsep))

        self.config = uiConfig

        self.models = {}
        self.currentModel = None

    def loadPlugins(self):
        for uiPlugin in self.pluginManager.plugins.values():
            if uiPlugin.autoLoad:
                print uiPlugin.__name__
                uiExt = self.pluginManager.loadPlugin(uiPlugin.__name__, application=self)
                uiExt.initializeWidget()

    def mainWindow(self):

        for wid in QtWidgets.QApplication.topLevelWidgets():
            if wid.objectName() == "VortexMainWindow":
                return wid

    def nodeLibraryWidget(self, parent):
        """Returns the custom node library widget which will popup within the graphview on ctrl+tab. This widget will
        only get created once per session.

        :param parent: the graphicsEditor widget used as the parent
        :type parent:  GraphEditor
        :return: The node library widget
        :rtype: QtWidget
        """
        return nodelibrary.NodesBox(self, parent=parent)

    def customToolbarActions(self, parent):
        pass

    def onNodeCreated(self, Type):
        pass

    def createContextMenu(self, objectModel):
        pass

    def registeredNodes(self):
        """Returns a full list of registered nodes

        :return:
        :rtype: list(str)
        """
        return []

    def keyPressEvent(self, event):
        """Gets executed any time a key gets pressed

        :note not yet hooked up to the ui
        :param event: The keyevent
        :type event: ::class:`QtGui.QKeyEvent`
        :rtype: str
        :return: eg. 'Ctrl+Z'
        """
        modifiers = event.modifiers()
        key = event.key()
        if key == 16777249:
            return
        sequence = []
        if modifiers == QtCore.Qt.ControlModifier:
            sequence.append(QtCore.Qt.SHIFT + key)
        if modifiers == QtCore.Qt.ShiftModifier:
            sequence.append(QtCore.Qt.CTRL + key)
        if modifiers == QtCore.Qt.AltModifier:
            sequence.append(QtCore.Qt.ALT + key)
        if not sequence:
            sequence = [key]
        results = QtGui.QKeySequence(*sequence)
        self.keyBoardMapping(str(results.toString()), key, modifiers)

    def keyBoardMapping(self, sequenceString, key, modifiers):
        """Key mapping to operation

        :param sequenceString: eg. 'Ctrl+Z'
        :type sequenceString: str
        :return:
        :rtype:
        """
        print sequenceString, key, modifiers

    def save(self, filePath):
        print "saving", filePath

    def load(self, filePath):
        print "loading", filePath
