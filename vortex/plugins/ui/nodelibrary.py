from collections import defaultdict
from Qt import QtWidgets, QtCore, QtGui
from zoo.libs.pyqt.extended import treeviewplus
from zoo.libs.pyqt.models import datasources, treemodel
from vortex import api
import logging

logger = logging.getLogger(__name__)


class NodeLibraryPlugin(api.UIPlugin):
    id = "NodeLibrary"
    autoLoad = True
    creator = "David Sparrow"
    dockArea = QtCore.Qt.LeftDockWidgetArea

    def show(self, parent):
        items = self.application.config.registeredNodes().items()
        plus = View(self.application, parent=parent)
        plus.reload(items)
        return plus


class View(treeviewplus.TreeViewPlus):
    finished = QtCore.Signal()

    def __init__(self, application, searchable=True, parent=None, expand=True, sorting=True,
                 labelVisible=False, comboVisible=False):
        super(View, self).__init__(searchable, parent, expand, sorting, labelVisible, comboVisible)
        self.application = application
        self.setObjectName("NodeLibrary")
        self.setAlternatingColorEnabled(False)
        root = NodeItem("")
        self.setModel(treemodel.TreeModel(root))
        self.treeView.doubleClicked.connect(self.onDoubleClicked)

    def reload(self, nodes):
        result = defaultdict(list)
        for item, category in sorted(nodes):
            result[category].append(item)
        categoryItems = {}
        model = self.model
        root = self.model.root
        for category, types in result.items():
            cat = categoryItems.get(category)
            if cat is None:
                cat = NodeItem(category, model=model, parent=root)
                root.addChild(cat)
                categoryItems[category] = cat
            for item in types:
                cat.addChild(NodeItem(item, model=model, parent=cat))
        self.model.reload()
        self.expandAll()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.finished.emit()
        elif event.key() in (QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter):
            self.onEnterPressed()
        elif event.key() in (QtCore.Qt.Key_Down, QtCore.Qt.Key_Up):
            return self.nodeListWidget.keyPressEvent(event)
        super(View, self).keyPressEvent(event)

    def onDoubleClicked(self, index):
        data = index.data(0)
        if not data:
            return
        self.createNode(index.data())

    def onEnterPressed(self):
        for item in self.selectedItems():
            data = item.data(0)
            self.createNode(data)

    def createNode(self, nodeType):
        editor = self.application.currentNetworkEditor()
        graph = self.application.currentGraph()
        if graph is not None:
            graph.createNode(nodeType, parent=editor.model)
            self.finished.emit()


class NodeItem(datasources.BaseDataSource):

    def __init__(self, nodeType, headerText=None, model=None, parent=None):
        super(NodeItem, self).__init__(headerText, model, parent)
        self.nodeType = nodeType

    def headerText(self, index):
        if index == 0:
            return "Node Type"

    def columnCount(self):
        return 1

    def isEditable(self, index):
        return False

    def data(self, index):
        if index == 0:
            return self.nodeType
