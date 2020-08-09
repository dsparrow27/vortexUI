from Qt import QtWidgets, QtCore, QtGui
from zoo.libs.pyqt.widgets import elements
from zoo.libs.pyqt.widgets import frame
from vortex import api
import logging

logger = logging.getLogger(__name__)


class NodeLibraryPlugin(api.UIPlugin):
    id = "NodeLibrary"
    autoLoad = True
    creator = "David Sparrow"
    dockArea = QtCore.Qt.LeftDockWidgetArea

    def show(self, parent):
        nb = NodesBox(self.application, parent=parent)
        return nb


class NodeBoxWidget(QtWidgets.QListWidget):
    enterPressed = QtCore.Signal()

    def __init__(self, parent):
        super(NodeBoxWidget, self).__init__(parent)
        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.setObjectName("nodeLibraryTreeWidget")
        self.setSortingEnabled(True)
        self.setDragEnabled(True)
        self.setDragDropMode(QtWidgets.QAbstractItemView.DragOnly)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Enter:
            self.enterPressed.emit()
        super(NodeBoxWidget, self).keyPressEvent(event)


class NodesBox(frame.QFrame):
    """doc string for NodesBox"""
    finished = QtCore.Signal()

    def __init__(self, application, parent):
        super(NodesBox, self).__init__(parent)
        self.application = application
        self.setObjectName("NodeLibrary")
        self.verticalLayout = elements.vBoxLayout(self)
        self.verticalLayout.setObjectName("verticalLayout")
        self.lineEdit = elements.LineEdit("Name: ", parent=self)
        self.lineEdit.setObjectName("nodelibraryLineEdit")
        self.lineEdit.setPlaceholderText("Enter node name..")
        self.verticalLayout.addWidget(self.lineEdit)
        self.nodeListWidget = NodeBoxWidget(parent=self)
        self.verticalLayout.addWidget(self.nodeListWidget)

        self.resize(200, self.sizeHint().height())
        self.connections()
        self.reload(self.application.config.registeredNodes(), "")

    def connections(self):
        self.lineEdit.textChanged.connect(self.searchTextChanged)
        self.nodeListWidget.itemChanged.connect(self.onSelectionChanged)
        self.nodeListWidget.itemDoubleClicked.connect(self.onDoubleClicked)
        self.nodeListWidget.enterPressed.connect(self.onEnterPressed)

    def show(self, *args, **kwargs):
        self.lineEdit.setFocus()
        self.nodeListWidget.clear()
        for item, category in self.application.config.registeredNodes().items():
            self.nodeListWidget.addItem(item)
        super(NodesBox, self).show(*args, **kwargs)

    def searchTextChanged(self, text):
        if not self.lineEdit.text():
            self.lineEdit.setPlaceholderText("Enter node name..")
        nodes = self.application.config.registeredNodes()
        nodes["Group"] = "misc"
        self.reload(nodes, text)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.finished.emit()
        elif event.key() in (QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter):
            self.onEnterPressed()
        elif event.key() in (QtCore.Qt.Key_Down, QtCore.Qt.Key_Up):
            return self.nodeListWidget.keyPressEvent(event)
        super(NodesBox, self).keyPressEvent(event)

    def onEnterPressed(self):
        currentText = self.nodeListWidget.currentItem().text()
        if currentText in self.application.config.registeredNodes().keys():
            self.application.graphNoteBook.currentPage().createNode(currentText)
            self.finished.emit()

    def onDoubleClicked(self, item):
        graphEditor = self.application.graphNoteBook.currentPage()
        graphEditor.graph.createNode(item.text(), parent=graphEditor.model)
        self.finished.emit()

    def onSelectionChanged(self, current):
        self.lineEdit.setText(current.text())

    def reload(self, items, searchText=None):
        searchText = (searchText or "").lower()
        self.nodeListWidget.clear()

        for item, category in items.items():
            if searchText not in item.lower():
                continue
            self.nodeListWidget.addItem(item)

        self.nodeListWidget.sortItems(QtCore.Qt.AscendingOrder)
        self.nodeListWidget.setCurrentRow(0)
