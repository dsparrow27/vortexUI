from qt import QtCore, QtWidgets
from vortex.ui import nodelibrary


class UIApplication(QtCore.QObject):
    # list(objectModel)
    onSelectionChanged = QtCore.Signal(list)

    # from api to ui signals
    onNewNodeRequested = QtCore.Signal(dict)
    onNodeDeleteRequested = QtCore.Signal(object)
    onConnectionAddedRequested = QtCore.Signal(object, object)
    onConnectionDeleteRequested = QtCore.Signal(object, object)

    def __init__(self, uiConfig, apiApplication):
        super(UIApplication, self).__init__()
        self._apiApplication = apiApplication
        self.config = uiConfig

        self.models = {}
        self.currentModel = None

    def mainWindow(self):
        for wid in QtWidgets.QApplication.topLevelWidgets():
            if wid.objectName() == "SlitherMainWindow":
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

    def registeredNodes(self):
        """Returns a full list of registered nodes

        :return:
        :rtype: list(str)
        """
        return []
