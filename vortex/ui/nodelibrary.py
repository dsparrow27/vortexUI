from qt import QtWidgets, QtCore, QtGui

import logging

logger = logging.getLogger(__name__)


class NodeBoxWidget(QtWidgets.QListWidget):

    def __init__(self, parent):
        super(NodeBoxWidget, self).__init__(parent)
        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.setObjectName("nodeLibraryTreeWidget")
        self.setSortingEnabled(True)
        self.setDragEnabled(True)
        self.setDragDropMode(QtWidgets.QAbstractItemView.DragOnly)

class NodesBox(QtWidgets.QFrame):
    """doc string for NodesBox"""

    def __init__(self, uiApplication, parent):
        super(NodesBox, self).__init__(parent)
        self.uiApplication = uiApplication
        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout.setContentsMargins(4, 4, 4, 4)
        self.lineEdit = QtWidgets.QLineEdit(self)
        self.lineEdit.setObjectName("nodelibraryLineEdit")
        self.lineEdit.setPlaceholderText("Enter node name..")
        self.verticalLayout.addWidget(self.lineEdit)
        self.nodeListWidget = NodeBoxWidget(parent=self)
        self.verticalLayout.addWidget(self.nodeListWidget)
        self.lineEdit.textChanged.connect(self.searchTextChanged)
        self.nodeListWidget.itemChanged.connect(self.onSelectionChanged)
        self.nodeListWidget.itemClicked.connect(self.onSelectionChanged)
        self.nodeListWidget.itemDoubleClicked.connect(self.onDoubleClicked)
        self.resize(400, 250)

    def sizeHint(self):
        return QtCore.QSize(400, 250)

    def show(self, *args, **kwargs):
        self.lineEdit.setFocus()
        super(NodesBox, self).show(*args, **kwargs)

    def searchTextChanged(self, text):
        if not self.lineEdit.text():
            self.lineEdit.setPlaceholderText("enter node name..")
        nodes = self.uiApplication.registeredNodes()
        nodes["Group"] = "misc"
        self.reload(nodes, text)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.hide()
        elif event.key() in (QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter):
            currentText = self.lineEdit.text()
            if currentText in self.uiApplication.registeredNodes().keys():
                self.uiApplication.onNodeCreated(currentText)
                self.hide()
            elif currentText == "Group":
                self.parent().scene.createBackDrop()
                self.hide()
        elif event.key() in (QtCore.Qt.Key_Down, QtCore.Qt.Key_Up):
            return self.nodeListWidget.keyPressEvent(event)
        super(NodesBox, self).keyPressEvent(event)

    def onDoubleClicked(self, item):
        self.uiApplication.onNodeCreated(item.text())
        self.hide()

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
