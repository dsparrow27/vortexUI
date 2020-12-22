from functools import partial

from zoovendor.Qt import QtCore, QtWidgets, QtGui


class GraphModel(QtCore.QObject):
    """High Level Application object, handles node plugins, UI Plugins, global events

    :param application:
    :type application: :class:`vortex.ui.uiApplication.UIApplication`
    :param name:
    :type name: str
    """
    sigNodesCreated = QtCore.Signal(list)

    def __init__(self, application, name):
        super(GraphModel, self).__init__()
        self.name = name
        self.config = application.config
        self.application = application  # type: vortex.ui.uiApplication.UIApplication
        self._rootNode = None

    @property
    def rootNode(self):
        """
        :rtype: :class:`vortex.ui.model.objectmodel.ObjectModel`
        """
        return self._rootNode

    @rootNode.setter
    def rootNode(self, value):
        self._rootNode = value

    def customToolbarActions(self, parent):
        pass

    def registeredNodes(self):
        """Returns a full list of registered nodes

        :return:
        :rtype: list(str)
        """
        return []

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
