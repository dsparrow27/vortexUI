from zoo.libs.pyqt.widgets import treewidget
from zoo.libs.pyqt.extended import stackwidget
from vortex.ui import plugin
from qt import QtCore


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
        wid = AttributeItem(objectModel.text(), parent=self.treeWidget)
        treeItem = self.treeWidget.insertNewItem(objectModel.text(), widget=wid, index=0, treeParent=None)
        self.nodes[objectModel] = treeItem

    def removeNode(self, objectModel):
        treeItem = self.nodes.get(objectModel)
        if treeItem:
            parent = treeItem.parent() or self.treeWidget.invisibleRootItem()
            parent.removeChild(treeItem)
            del self.nodes[objectModel]


class AttributeItem(stackwidget.StackItem):

    def __init__(self, title, parent, collapsed=False, collapsable=True, icon=None, startHidden=False,
                 itemTint=tuple([60, 60, 60]), shiftArrowsEnabled=True, deleteButtonEnabled=True, titleEditable=True,
                 initUi=True):
        super(AttributeItem, self).__init__(title, parent, collapsed, collapsable, icon, startHidden, itemTint,
                                            shiftArrowsEnabled, deleteButtonEnabled, titleEditable, initUi)
        self.model = None

    def setObjectModel(self, model):
        self.model = model
        self.setTitle(model.name)
