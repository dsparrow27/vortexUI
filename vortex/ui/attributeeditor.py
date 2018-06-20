from zoo.libs.pyqt.widgets import treewidget
from zoo.libs.pyqt.extended import stackwidget


class AttributeEditor(treewidget.TreeWidgetFrame):
    def __init__(self, application, parent=None):
        super(AttributeEditor, self).__init__(parent)
        self.application = application
        self.setObjectName("AttributeEditor")
        tree = treewidget.TreeWidget(parent=self, locked=False, allowSubGroups=False)
        self.initUi(tree)
        self.nodes = {}
        self.application.onSelectionChanged.connect(self.onSceneSelection)

    def onSceneSelection(self, selection):
        for sel in self.nodes:
            self.removeNode(sel)
        for sel in selection:
            self.addNode(sel)

    def addNode(self, objectModel):
        exists = self.nodes.get(objectModel)
        if exists:
            exists.show()
            return
        wid = AttributeItem(objectModel.name, parent=self.treeWidget)
        treeItem = self.treeWidget.addNewItem(self, wid.name, widget=wid)
        self.nodes[objectModel] = treeItem

    def removeNode(self, objectModel):
        treeItem = self.nodes.get(objectModel)
        if treeItem:
            treeItem.parent().removeItem(treeItem)
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
