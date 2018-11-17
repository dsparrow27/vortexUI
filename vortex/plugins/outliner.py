from vortex.ui import plugin
from qt import QtCore, QtWidgets
from zoo.libs.pyqt.widgets import treewidget


class OutlinerPlugin(plugin.UIPlugin):
    id = "Outliner"
    autoLoad = True
    creator = "David Sparrow"

    def initializeWidget(self):
        window = self.application.mainWindow()
        self.outliner = Outliner(self.application, parent=window)
        window.createDock(self.outliner, QtCore.Qt.LeftDockWidgetArea)
        return self.outliner


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

    def onSceneSelection(self, selection, state):
        print "selection", selection, state
        pass

    def newNode(self, objectModel):
        objectModel = objectModel["model"]
        parentModel = objectModel.parentObject()
        if parentModel:
            parentItem = self.treeWidget.findItems(objectModel.parentObject().text(),
                                                   QtCore.Qt.MatchWildcard)[0]
        else:
            parentItem = self.treeWidget.invisibleRootItem()

        item = QtWidgets.QTreeWidgetItem(parentItem, [objectModel.text()])
        parentItem.addChild(item)
        item.setExpanded(True)


    def removeNode(self, objectModel):
        print "removeNode", objectModel
