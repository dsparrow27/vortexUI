from Qt import QtWidgets
from zoo.libs.pyqt.widgets import elements
from zoo.libs.pyqt.widgets import dialog
from zoo.libs.pyqt.extended import treeviewplus
from zoo.libs.pyqt.models import treemodel, datasources
from vortex import api


class NodePropertiesDialog(dialog.Dialog):
    def __init__(self, application, objectModel, parent=None):
        super(NodePropertiesDialog, self).__init__(width=600, height=300,
                                                   title="Node property Editor",
                                                   showOnInitialize=False,
                                                   parent=parent)
        self.application = application
        self.objectModel = objectModel
        self.initUI()
        self.state = {}

    def initUI(self):
        self.treeModel = treemodel.TreeModel(Root({}))
        self.mainLayout = elements.vBoxLayout(parent=self, spacing=1)
        self.treeview = treeviewplus.TreeViewPlus(searchable=True, parent=self)
        self.treeview.setAlternatingColorEnabled(False)
        self.treeview.setModel(self.treeModel)
        self.mainLayout.addWidget(self.treeview)

        addAttrBtn = elements.styledButton(text=None,
                                           icon="plus", parent=self,
                                           toolTip="Add an Attribute")
        removeAttrBtn = elements.styledButton(text=None,
                                              icon="minus", parent=self,
                                              toolTip="Remove an Attribute")
        opLayout = elements.hBoxLayout()
        self.mainLayout.addLayout(opLayout)
        opLayout.addWidget(addAttrBtn)
        opLayout.addWidget(removeAttrBtn)
        opLayout.addItem(QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))

        okCancelLayout = elements.hBoxLayout()
        okCancelLayout.addItem(
            QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))
        okCancelBtn = elements.OkCancelButtons(parent=self)
        okCancelLayout.addWidget(okCancelBtn)
        self.mainLayout.addLayout(okCancelLayout)

        addAttrBtn.clicked.connect(self.onCreate)
        removeAttrBtn.clicked.connect(self.onRemove)
        okCancelBtn.okBtn.clicked.connect(self.onCommit)

    def onCreate(self):
        attr = Root(api.AttributeModel(self.objectModel))
        self.treeModel.root.addChild(attr)
        self.treeModel.reload()

    def onRemove(self):
        indices = self.treeview.selectedQIndices()
        model = self.treeview.model
        for item in indices:
            itemParent = model.itemFromIndex(item.parent())
            itemParent.removeRowDataSource(item.row())
        self.treeModel.reload()

    def onCommit(self):
        pass


class Root(datasources.BaseDataSource):
    def __init__(self, attribute, *args, **kwargs):
        super(Root, self).__init__(*args, **kwargs)
        self.headers = ["Name", "Type", "Input", "Output", "Default", "Min", "Max", "isCompound", "isArray"]
        self.attribute = attribute

    def data(self, index):
        if index == 0:
            return self.attribute.text()
        if index == 1:
            return self.attribute.type()
        elif index == 2:
            return self.attribute.isInput()
        elif index == 3:
            return self.attribute.isOutput()
        elif index == 4:
            return self.attribute.default()
        elif index == 5:
            return self.attribute.min()
        elif index == 6:
            return self.attribute.max()
        elif index == 7:
            return self.attribute.isCompound()
        elif index == 8:
            return self.attribute.isArray()

    def setData(self, index, value):
        if index == 0:
            self.attribute.setText(str(value))
        elif index == 1:
            self.attribute.setType(str(value))
        elif index == 2:
            self.attribute.setAsInput(bool(value))
        elif index == 3:
            self.attribute.setAsOutput(bool(value))
        elif index == 4:
            self.attribute.setDefault(bool(value))
        elif index == 5:
            self.attribute.setMin(value)
        elif index == 6:
            self.attribute.setMax(value)
        elif index == 7:
            self.setIsCompound(value)
        elif index == 8:
            self.setIsArray(value)

    def rowCount(self):
        return len(self.children)

    def columnCount(self):
        return len(self.headers)

    def headerText(self, index):
        if index in range(len(self.headers)):
            return self.headers[index]

    def removeRowDataSource(self, index):
        if index in range(self.rowCount()):
            self.children.pop(index)
