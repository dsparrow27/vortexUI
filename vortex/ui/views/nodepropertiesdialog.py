from Qt import QtWidgets
from copy import deepcopy
from zoo.libs.pyqt.widgets import elements
from zoo.libs.pyqt.widgets import dialog
from zoo.libs.pyqt.extended import tabwidget
from zoo.libs.pyqt.extended import treeviewplus
from zoo.libs.pyqt.extended import pythoneditor
from zoo.libs.pyqt.models import treemodel, datasources
from vortex.ui.model import attributemodel


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
        self.attributeEditorWidget = AttributeEditorWidget(objectModel=self.objectModel, parent=self)
        self.nodeProperties = NodePropertiesWidget(objectModel=self.objectModel, parent=self)
        self.scriptEditor = ScriptEditor(objectModel=self.objectModel, parent=self)
        self.tab = tabwidget.TabWidget("NoteBook", parent=self)
        self.tab.newTabBtn.hide()
        self.tab.addTab(self.nodeProperties, "General")
        self.tab.addTab(self.attributeEditorWidget, "Attributes")
        self.tab.addTab(self.scriptEditor, "Script")
        self.mainLayout = elements.vBoxLayout(parent=self, spacing=0)
        self.mainLayout.addWidget(self.tab)

        okCancelLayout = elements.hBoxLayout()
        okCancelLayout.addItem(
            QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))
        okCancelBtn = elements.OkCancelButtons(parent=self)
        okCancelLayout.addWidget(okCancelBtn)
        self.mainLayout.addLayout(okCancelLayout)

        okCancelBtn.okBtn.clicked.connect(self.onCommit)
        okCancelBtn.cancelBtn.clicked.connect(self.close)
        if not self.objectModel.canCreateAttributes():
            okCancelBtn.okBtn.setEnabled(False)

    def onCommit(self):
        for k, v in self.nodeProperties.newData.items():
            if v:
                getattr(self.objectModel, "set" + k)(v)

        for child in self.attributeEditorWidget.treeModel.root.children:
            self.objectModel.createAttribute(child.attribute)
        self.close()


class NodePropertiesWidget(QtWidgets.QWidget):
    def __init__(self, objectModel, parent=None):
        super(NodePropertiesWidget, self).__init__(parent=parent)
        self.objectModel = objectModel
        self.newData = {"Text": "",
                        "Description": "",
                        "BackgroundColour": None,
                        "HeaderColour": None}
        self.initUI()

    def initUI(self):
        self.mainLayout = elements.vBoxLayout(parent=self, spacing=1)
        self.nameEdit = elements.StringEdit(label="Name:",
                                            editText=self.objectModel.text(),
                                            editPlaceholder="Please Enter Node Name",
                                            enableMenu=False,
                                            parent=self)
        color = self.objectModel.backgroundColour()
        headerColor = self.objectModel.headerColour()
        self.colorBtn = elements.LabelColorBtn(label="Colour:",
                                               initialRgbColor=(color.red(), color.green(), color.blue()),
                                               parent=self)
        self.colorBtn.colorChanged.connect(self.colourChanged)
        self.headerColorBtn = elements.LabelColorBtn(label="Header Colour:",
                                                     initialRgbColor=(headerColor.red(), headerColor.green(), headerColor.blue()),
                                                     parent=self)
        self.headerColorBtn.colorChanged.connect(self.headerColourChanged)
        self.description = elements.TextEdit(text=self.objectModel.toolTip(),
                                             parent=self)
        self.mainLayout.addWidget(self.nameEdit)
        self.mainLayout.addWidget(self.colorBtn)
        self.mainLayout.addWidget(self.headerColorBtn)
        self.mainLayout.addWidget(elements.Label(text="Description:",
                                                 parent=self, enableMenu=False))
        self.mainLayout.addWidget(self.description)
        self.nameEdit.textChanged.connect(self.onSetName)

    def colourChanged(self, colour):
        self.newData["BackgroundColour"] = colour

    def headerColourChanged(self, colour):
        self.newData["HeaderColour"] = colour

    def onSetName(self, name):
        if name:
            self.newData["Text"] = name


class AttributeEditorWidget(QtWidgets.QWidget):
    def __init__(self, objectModel, parent=None):
        super(AttributeEditorWidget, self).__init__(parent=parent)
        self.initUI()

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
        addAttrBtn.clicked.connect(self.onCreate)
        removeAttrBtn.clicked.connect(self.onRemove)

    def onCreate(self):
        attr = Root(deepcopy(attributemodel.AttributeModel.defaultFields))
        self.treeModel.root.addChild(attr)
        self.treeModel.reload()

    def onRemove(self):
        indices = self.treeview.selectedQIndices()
        model = self.treeview.model
        for item in indices:
            itemParent = model.itemFromIndex(item.parent())
            itemParent.removeRowDataSource(item.row())
        self.treeModel.reload()


class ScriptEditor(QtWidgets.QWidget):
    def __init__(self, objectModel, parent=None):
        super(ScriptEditor, self).__init__(parent=parent)
        self.objectModel = objectModel
        self.initUI()

    def initUI(self):
        self.mainLayout = elements.vBoxLayout(parent=self, spacing=1)
        self.mainLayout.addWidget(elements.Label(text="Command",
                                                 parent=self))
        self.editor = pythoneditor.TextEditor(parent=self)
        self.mainLayout.addWidget(self.editor)


class Root(datasources.BaseDataSource):
    def __init__(self, attribute, *args, **kwargs):
        super(Root, self).__init__(*args, **kwargs)
        self.headers = list(attribute.defaultFields.keys())
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
