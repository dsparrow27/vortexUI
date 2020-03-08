from functools import partial

from Qt import QtCore, QtWidgets, QtGui


class GraphModel(QtCore.QObject):
    """High Level Application object, handles node plugins, UI Plugins, global events


    """
    graphSaved = QtCore.Signal(str)
    graphLoaded = QtCore.Signal(object)
    nodeCreated = QtCore.Signal(object)
    requestRefresh = QtCore.Signal()

    def __init__(self, application):
        """
        :param application:
        :type application:
        """
        super(GraphModel, self).__init__()
        self.config = application.config
        self.application = application
        self._keyBoardMapping = {}
        self._rootNode = None

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

    def rootNode(self):
        return self._rootNode

    def saveGraph(self, objectModel):
        return {}

    def loadGraph(self, filePath):
        pass

    def delete(self):
        pass

    def loadFromDict(self, data):
        pass

    def createNode(self, nodeType, parent=None):
        pass
