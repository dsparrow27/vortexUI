import os
from functools import partial

from Qt import QtCore, QtWidgets, QtGui
from zoo.libs.plugin import pluginmanager
from vortex.ui import plugin


class EventManager(QtCore.QObject):
    """
    ..code-block:: python
        sig = QtCore.Signal()
        events = EventManager()
        events.register("selectionChanged", sig)
        events.selectionChanged.connect()
    """

    def __init__(self):
        super(EventManager, self).__init__()
        self.events = {}

    def register(self, name, function):
        if name in self.events:
            raise NameError("Event Name: '{}' already exists".format(name))
        self.events[name] = function
        return True

    def unregister(self, name):
        if name not in self.events:
            raise NameError("Event Name: '{}' already exists".format(name))
        self.events.pop(name)
        return True

    def __getattr__(self, name):
        """

        :param name: The event name
        :type name: str
        :rtype: QSignal
        """
        event = self.events.get(name)
        if event is not None:
            return event
        return super(EventManager, self).__getattribute__(name)


class UIApplication(QtCore.QObject):
    """High Level Application object, handles node plugins, UI Plugins, global events
    """
    # graph, list(objectModel), True
    onSelectionChanged = QtCore.Signal(object, list, bool)

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
        self.events = EventManager()
        self.attributeModelClass = None
        self.objectModelClass = None

    def registerObjectModelType(self, objectModel):
        self.objectModelClass = objectModel

    def registerAttributeModel(self, attributeModel):
        self.attributeModelClass = attributeModel

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

    def mainWindow(self):
        for wid in QtWidgets.QApplication.topLevelWidgets():
            if wid.objectName() == "Vortex":
                return wid

    def customToolbarActions(self, parent):
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

    def saveGraph(self, objectModel):
        print("test")
        return {}
