from vortex.ui import plugin
from qt import QtCore, QtWidgets
from zoo.libs.pyqt.widgets import treewidget


class OutlinerPlugin(plugin.UIPlugin):
    id = "Outliner"
    autoLoad = True
    creator = "David Sparrow"
    dockArea = QtCore.Qt.LeftDockWidgetArea

    def show(self, parent):
        return Outliner(self.application, parent=parent)


class Outliner(treewidget.TreeWidgetFrame):
    def __init__(self, application, parent=None):
        super(Outliner, self).__init__(parent)
        self.application = application
        self.setObjectName("Outliner")
        tree = treewidget.TreeWidget(parent=self, locked=False, allowSubGroups=False)
        self.initUi(tree)
        self.application.onSelectionChanged.connect(self.onSceneSelection)
        self.application.onNodeDeleteRequested.connect(self.removeNode)
        self.application.onNewNodeRequested.connect(self.newNode)
        self.newNode({"model": self.application.currentModel})
        self.application.setShortcutForWidget(self, "Outliner")
    def onSceneSelection(self, selection, state):

        iterator = QtWidgets.QTreeWidgetItemIterator(self.treeWidget)
        for it in iterator:
            item = it.value()
            if item.data(0, QtCore.Qt.UserRole + 1) == selection:
                item.setSelected(state)

    def newNode(self, objectModel):
        objectModel = objectModel["model"]
        parentModel = objectModel.parentObject()
        if parentModel:
            parentItem = self.treeWidget.findItems(objectModel.parentObject().text(),
                                                   QtCore.Qt.MatchWildcard)[0]
        else:
            parentItem = self.treeWidget.invisibleRootItem()

        item = QtWidgets.QTreeWidgetItem(parentItem, [objectModel.text()])
        item.setData(0, QtCore.Qt.UserRole + 1, objectModel)
        parentItem.addChild(item)
        item.setExpanded(True)

    def removeNode(self, objectModel):
        iterator = QtWidgets.QTreeWidgetItemIterator(self.treeWidget)
        for it in iterator:
            item = it.value()
            if item.data(0, QtCore.Qt.UserRole + 1) == objectModel:
                parent = item.parent()
                parent.removeChild(item)
