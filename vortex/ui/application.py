from qt import QtCore, QtWidgets


class UIApplication(QtCore.QObject):
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

    def registerdNodes(self):
        """Returns a full list of registered nodes

        :return:
        :rtype: list(str)
        """
        return ["node1", "node2", "sum"]


