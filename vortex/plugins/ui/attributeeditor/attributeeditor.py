from functools import partial

from zoo.libs.pyqt.widgets import groupedtreewidget
from zoo.libs.pyqt.widgets import stackwidget, elements
from vortex import api
from zoovendor.Qt import QtCore, QtWidgets


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
        self.application.events.uiSelectionChanged.connect(self.onSceneSelection)
        self.application.events.uiNodesDeleted.connect(self.removeNode)

    def onSceneSelection(self, selection):
        for model in selection:
            if model.isSelected():
                self.addNode(model)

    def addNode(self, objectModel):
        exists = self.nodes.get(objectModel)
        if exists:
            exists.setHidden(False)
            return
        wid = NodeItem(objectModel.text(), parent=self)
        wid.setObjectModel(objectModel)
        treeItem = self.insertNewItem("", widget=wid, index=0, treeParent=None)
        wid.deletePressed.connect(partial(self.removeNode, [objectModel]))
        self.nodes[objectModel] = treeItem

    def removeNode(self, objectModels):
        for objectModel in objectModels:
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
