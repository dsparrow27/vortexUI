from Qt import QtWidgets
from copy import deepcopy
from zoo.libs.pyqt.widgets import elements
from zoo.libs.pyqt.widgets import dialog
from zoo.libs.pyqt.extended import treeviewplus
from zoo.libs.pyqt.models import treemodel, datasources
from vortex import api


class NodePropertiesDialog(dialog.Dialog):
    def __init__(self, application, objectModel, parent=None):
        title = "Graph Node Properties - {}".format(objectModel.text())
        super(NodePropertiesDialog, self).__init__(width=600, height=300,
                                                   title=title,
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
        okCancelBtn.cancelBtn.clicked.connect(self.close)
        if not self.objectModel.canCreateAttributes():
            okCancelBtn.okBtn.setEnabled(False)

    def onCreate(self):
        attr = Root(deepcopy(api.AttributeModel.defaultFields))
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
        for child in self.treeModel.root.children:
            self.objectModel.createAttribute(child.attribute)
        self.close()


class Root(datasources.BaseDataSource):
    def __init__(self, attribute, *args, **kwargs):
        super(Root, self).__init__(*args, **kwargs)
        self.headers = list(api.AttributeModel.defaultFields.keys())
        self.attribute = attribute

    def data(self, index):
        return self.attribute[self.headers[index]]

    def setData(self, index, value):
        self.attribute[self.headers[index]] = value
        return
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