from zoo.libs.pyqt.widgets import groupedtreewidget
from zoo.libs.pyqt.widgets import stackwidget
from vortex import api
from Qt import QtCore, QtWidgets


class AttributeEditorPlugin(api.UIPlugin):
    id = "AttributeEditor"
    autoLoad = True
    creator = "David Sparrow"
    dockArea = QtCore.Qt.RightDockWidgetArea

    def close(self):
        self._widget.close()
        self._widget = None

    def show(self, parent):
        return AttributeEditor(self.application, parent=parent)


class AttributeEditor(groupedtreewidget.GroupedTreeWidget):
    def __init__(self, application, parent=None):
        super(AttributeEditor, self).__init__(parent)
        self.application = application
        self.setObjectName("AttributeEditor")
        self.nodes = {}
        # self.application.events.onSelectionChanged.connect(self.onSceneSelection)
        # self.application.onSelectionChanged.connect(self.onSceneSelection)
        # self.application.events.onNodeDeleted.connect(self.removeNode)
        # self.application.onNodeDeleteRequested.connect(self.removeNode)
        # self.graph.setShortcutForWidget(self, "AttributeEditor")

    def onSceneSelection(self, *args):
        for i in self.application.notebook.currentPage().scene.selectedNodes():
            self.addNode(i.model)
        # if state:
        #     self.addNode(selection)
        # else:
        #     self.removeNode(selection)

    def addNode(self, objectModel):
        exists = self.nodes.get(objectModel)
        if exists:
            exists.setVisible(True)
            return
        wid = NodeItem(objectModel.text(), parent=self)
        wid.setObjectModel(objectModel)
        treeItem = self.insertNewItem("", widget=wid, index=0, treeParent=None)
        self.nodes[objectModel] = treeItem

    def removeNode(self, objectModel):
        treeItem = self.nodes.get(objectModel)
        if treeItem:
            parent = treeItem.parent() or self.invisibleRootItem()
            parent.removeChild(treeItem)
            del self.nodes[objectModel]


class NodeItem(stackwidget.StackItem):

    def __init__(self, title, parent, collapsed=False, collapsable=True, icon=None, startHidden=False,
                 shiftArrowsEnabled=False, deleteButtonEnabled=True, titleEditable=True):
        super(NodeItem, self).__init__(title, parent, collapsed, collapsable, icon, startHidden,
                                       shiftArrowsEnabled, deleteButtonEnabled, titleEditable)
        self.model = None
        self.customWidget = None

    def setObjectModel(self, model):
        widget = model.attributeWidget(parent=self)
        if widget is not None:
            self.customWidget = widget
            self.addWidget(self.customWidget)
        self.model = model
