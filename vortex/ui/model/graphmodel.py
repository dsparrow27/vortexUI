from functools import partial

from Qt import QtCore, QtWidgets, QtGui


class GraphModel(QtCore.QObject):
    """High Level Application object, handles node plugins, UI Plugins, global events


    """

    def __init__(self, application):
        """
        :param application:
        :type application:
        """
        super(GraphModel, self).__init__()
        self.config = application.config
        self.application = application
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
