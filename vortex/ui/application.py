from qt import QtCore, QtWidgets, QtGui
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
        self.keyBoardMapping(str(results.toString()))

    def keyBoardMapping(self, sequenceString):
        """Key mapping to operation

        :param sequenceString: eg. 'Ctrl+Z'
        :type sequenceString: str
        :return:
        :rtype:
        """
        pass
