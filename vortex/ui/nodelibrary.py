from qt import QtWidgets, QtCore


class NodeBoxTreeWidget(QtWidgets.QTreeWidget):

    def __init__(self, parent):
        super(NodeBoxTreeWidget, self).__init__(parent)
        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.setObjectName("nodeLibraryTreeWidget")
        self.setSortingEnabled(True)
        self.setDragEnabled(True)
        self.setColumnCount(1)
        self.setHeaderHidden(True)
        self.setDragDropMode(QtWidgets.QAbstractItemView.DragOnly)
        self.setAnimated(True)


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
        self.treeWidget = NodeBoxTreeWidget(parent=self)
        self.verticalLayout.addWidget(self.treeWidget)
        self.lineEdit.textChanged.connect(self.searchTextChanged)
        self.treeWidget.itemChanged.connect(self.onSelectionChanged)
        self.treeWidget.itemClicked.connect(self.onSelectionChanged)
        self.resize(400, 250)

    def sizeHint(self):
        return QtCore.QSize(400, 250)

    def show(self, *args, **kwargs):
        self.lineEdit.setFocus()
        super(NodesBox, self).show(*args, **kwargs)

    def searchTextChanged(self, text):
        if not self.lineEdit.text():
            self.lineEdit.setPlaceholderText("enter node name..")

        self.reload(self.uiApplication.registeredNodes(), text)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.hide()
        elif event.key() in (QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter):
            currentText = self.lineEdit.text()
            if currentText in self.uiApplication.registeredNodes().keys():
                self.uiApplication.onNodeCreated(currentText)
                self.hide()

    def onSelectionChanged(self, current, previous):
        self.lineEdit.setText(current.text(0))

    def reload(self, items, searchText=None):
        searchText = (searchText or "").lower()
        self.treeWidget.clear()
        existing = {}

        for item, category in items.items():
            if not category:
                category = "misc"
            if searchText not in category.lower() and searchText not in item.lower():
                continue
            if category in existing:
                child = QtWidgets.QTreeWidgetItem()
                child.setText(0, item)
                existing[category].addChild(child)
            else:
                cat = QtWidgets.QTreeWidgetItem()
                cat.setText(0, category)
                existing[category] = cat
                self.treeWidget.insertTopLevelItem(0, cat)
                child = QtWidgets.QTreeWidgetItem()
                child.setText(0, item)
                cat.addChild(child)
                if searchText:
                    cat.setExpanded(True)

        self.treeWidget.sortItems(0, QtCore.Qt.AscendingOrder)
