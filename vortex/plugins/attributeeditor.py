from zoo.libs.pyqt.widgets import treewidget
from zoo.libs.pyqt.extended import stackwidget
from vortex.ui import plugin
from qt import QtCore, QtWidgets


class AttributeEditorPlugin(plugin.UIPlugin):
    id = "AttributeEditor"
    type = "Widget"
    autoLoad = True
    creator = "David Sparrow"

    def initializeWidget(self):
        window = self.application.mainWindow()
        self.attributeEditor = AttributeEditor(self.application, parent=window)
        window.createDock(self.attributeEditor, QtCore.Qt.RightDockWidgetArea)
        return self.attributeEditor


class AttributeEditor(treewidget.TreeWidgetFrame):
    def __init__(self, application, parent=None):
        super(AttributeEditor, self).__init__(parent)
        self.application = application
        self.setObjectName("AttributeEditor")
        tree = treewidget.TreeWidget(parent=self, locked=False, allowSubGroups=False)
        self.initUi(tree)
        self.nodes = {}
        self.application.onSelectionChanged.connect(self.onSceneSelection)
        self.application.onNodeDeleteRequested.connect(self.removeNode)

    def onSceneSelection(self, selection, state):
        if state:
            self.addNode(selection)
        else:
            self.removeNode(selection)

    def addNode(self, objectModel):
        exists = self.nodes.get(objectModel)
        if exists:
            exists.show()
            return
        wid = NodeItem(objectModel.text(), parent=self.treeWidget)
        wid.setObjectModel(objectModel)
        treeItem = self.treeWidget.insertNewItem(objectModel.text(), widget=wid, index=0, treeParent=None)
        self.nodes[objectModel] = treeItem

    def removeNode(self, objectModel):
        treeItem = self.nodes.get(objectModel)
        if treeItem:
            parent = treeItem.parent() or self.treeWidget.invisibleRootItem()
            parent.removeChild(treeItem)
            del self.nodes[objectModel]


class NodeItem(stackwidget.StackItem):

    def __init__(self, title, parent, collapsed=False, collapsable=True, icon=None, startHidden=False,
                 shiftArrowsEnabled=True, deleteButtonEnabled=True, titleEditable=True,
                 initUi=True):
        super(NodeItem, self).__init__(title, parent, collapsed, collapsable, icon, startHidden,
                                       shiftArrowsEnabled, deleteButtonEnabled, titleEditable, initUi)
        self.model = None
        self.customWidget = None

    def setObjectModel(self, model):
        widget = model.attributeWidget(parent=self)
        if widget is not None:
            self.customWidget = widget
            self.addWidget(self.customWidget)
        self.model = model
