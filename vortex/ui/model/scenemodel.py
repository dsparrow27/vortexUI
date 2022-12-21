"""This module is for a standard Qt tree model
"""
import typing

import PySide2
from zoovendor import six
from zoovendor.Qt import QtCore, QtGui, QtWidgets
from zoovendor.six.moves import cPickle
from zoo.libs.pyqt.models import constants

# from zoo.libs.pyqt.models import constants


isCompoundRole = constants.userRoleCount + 2
isPinRole = constants.userRoleCount + 3
isCommentRole = constants.userRoleCount + 4
isInputRole = constants.userRoleCount + 5
isOutputRole = constants.userRoleCount + 6
isBackdropRole = constants.userRoleCount + 7
supportsContextMenuRole = constants.userRoleCount + 8
categoryRole = constants.userRoleCount + 9
secondaryLabelRole = constants.userRoleCount + 10
sizeRole = constants.userRoleCount + 11
minimumSizeRole = constants.userRoleCount + 12
backgroundColorRole = constants.userRoleCount + 13
headerBackgroundRole = constants.userRoleCount + 14
foregroundColorRole = constants.userRoleCount + 15
secondaryLabelColorRole = constants.userRoleCount + 16
edgeColorRole = constants.userRoleCount + 17
headerButtonColorRole = constants.userRoleCount + 18
edgeThicknessRole = constants.userRoleCount + 19
resizerSizeRole = constants.userRoleCount + 20
descriptionRole = constants.userRoleCount + 21
isArrayRole = constants.userRoleCount + 22
isInternalRole = constants.userRoleCount + 23
isElementRole = constants.userRoleCount + 24
isChildRole = constants.userRoleCount + 25
pathRole = constants.userRoleCount + 26
typeRole = constants.userRoleCount + 27
minValueRole = constants.userRoleCount + 28
maxValueRole = constants.userRoleCount + 29
defaultValueRole = constants.userRoleCount + 30
isConnectedRole = constants.userRoleCount + 31
highLightColorRole = constants.userRoleCount + 32


class NodeItem(QtGui.QStandardItem):
    def __init__(self, parent=None):
        super(NodeItem, self).__init__(parent)
        self.objectModel = None

    def setData(self, value: typing.Any, role: int = ...) -> None:
        if role == constants.userObject:
            self.objectModel = value
            return
        super(NodeItem, self).setData(value, role)

    def clone(self) -> QtGui.QStandardItem:
        return super(NodeItem, self).clone()


class AttributeItem(QtGui.QStandardItem):
    def __init__(self, parent=None):
        super(AttributeItem, self).__init__(parent)
        self.attributeModel = None

    def setData(self, value: typing.Any, role: int = ...) -> None:
        if role == constants.userObject:
            self.attributeModel = value
            return
        super(AttributeItem, self).setData(value, role)

    def clone(self) -> QtGui.QStandardItem:
        return super(AttributeItem, self).clone()


class ConnectionItem(QtGui.QStandardItem):
    def clone(self) -> QtGui.QStandardItem:
        return super(ConnectionItem, self).clone()


class SceneModel(QtGui.QStandardItemModel):
    def __init__(self, graph, parent=None):
        super(SceneModel, self).__init__(parent)
        self.graph = graph

    def reload(self):
        """Hard reloads the model, we do this by the modelReset slot, the reason why we do this instead of insertRows()
        is because we expect that the tree structure has already been rebuilt with its children so by calling insertRows
        we would in turn create duplicates.
        """
        self.modelReset.emit()

    def rowCount(self, parent):
        pass

    def columnCount(self, parent):
        pass

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return None
        item = index.internalPointer()
        column = index.column()
        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            return item.data(column)
        elif role == QtCore.Qt.ToolTipRole:
            return item.toolTip(column)
        elif role == QtCore.Qt.DecorationRole:
            return item.icon(column)
        elif role == QtCore.Qt.CheckStateRole and item.isCheckable(column):
            if item.data(column):
                return QtCore.Qt.Checked
            return QtCore.Qt.Unchecked
        elif role == QtCore.Qt.BackgroundRole:
            color = item.backgroundColor(column)
            if color:
                return color
        elif role == QtCore.Qt.ForegroundRole:
            color = item.foregroundColor(column)
            if color:
                return color
        elif role == QtCore.Qt.TextAlignmentRole:
            return item.alignment(index)
        elif role == QtCore.Qt.FontRole:
            return item.font(column)
        elif role in (constants.sortRole, constants.filterRole):
            return item.data(column)
        elif role == constants.enumsRole:
            return item.data(column, constants.enumsRole)
        elif role == constants.userObject:
            return item
        return super(SceneModel, self).data(index, role)

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if not index.isValid():
            return False
        pointer = index.internalPointer()
        if role == QtCore.Qt.EditRole:
            column = index.column()
            hasChanged = pointer.setData(column, value)
            if hasChanged:
                self.dataChanged.emit(index, index, role)
                return True
        return False

    def flags(self, index):
        if not index.isValid():
            return QtCore.Qt.ItemIsDropEnabled
        column = index.column()
        pointer = index.internalPointer()
        flags = QtCore.Qt.ItemIsEnabled
        if pointer.supportsDrag(column):
            flags |= QtCore.Qt.ItemIsDragEnabled
        if pointer.supportsDrop(column):
            flags |= QtCore.Qt.ItemIsDropEnabled
        if pointer.isEditable(column):
            flags |= QtCore.Qt.ItemIsEditable
        if pointer.isSelectable(column):
            flags |= QtCore.Qt.ItemIsSelectable
        if pointer.isEnabled(column):
            flags |= QtCore.Qt.ItemIsEnabled
        if pointer.isCheckable(column):
            flags |= QtCore.Qt.ItemIsUserCheckable
        return flags

    def supportedDropActions(self):
        return QtCore.Qt.CopyAction | QtCore.Qt.MoveAction

    def mimeTypes(self):
        return ["application/x-datasource"]

    def mimeData(self, indices):
        """Encode serialized data from the item at the given index into a QMimeData object."""
        data = []
        for i in indices:
            item = self.itemFromIndex(i)
            pickleData = item.mimeData(i)
            if pickleData:
                data.append(pickleData)

        mimedata = QtCore.QMimeData()
        if data:
            mimedata.setData("application/x-datasource", cPickle.dumps(data))

        return mimedata

    def dropMimeData(self, mimeData, action, row, column, parentIndex):
        if action == QtCore.Qt.IgnoreAction:
            return False
        if not mimeData.hasFormat("application/x-datasource"):
            return super(TreeModel, self).dropMimeData(mimeData, action, row, column, parentIndex)
        data = six.binary_type(mimeData.data("application/x-datasource"))
        items = cPickle.loads(data)
        if not items:
            return False

        dropParent = self.itemFromIndex(parentIndex)
        returnKwargs = dropParent.dropMimeData(items, action)
        if not returnKwargs:
            return False
        self.insertRows(row, len(items), parentIndex, **returnKwargs)
        if action == QtCore.Qt.CopyAction:
            return False  # don't delete just copy over
        return True

    def headerData(self, section, orientation, role):
        if orientation == QtCore.Qt.Horizontal:
            if role == QtCore.Qt.DisplayRole:
                return self.root.headerText(section)
            elif role == QtCore.Qt.DecorationRole:
                icon = self.root.headerIcon()
                if icon.isNull:
                    return
                return icon.pixmap(icon.availableSizes()[-1])
        return None

    def index(self, row, column, parent=QtCore.QModelIndex()):
        if not self.hasIndex(row, column, parent):
            return QtCore.QModelIndex()

        parentItem = self.itemFromIndex(parent)

        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)

        return QtCore.QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QtCore.QModelIndex()

        childItem = index.internalPointer()
        parentItem = childItem.parentSource()
        if parentItem == self.root or parentItem is None:
            return QtCore.QModelIndex()

        return self.createIndex(parentItem.index(), 0, parentItem)

    def insertRow(self, position, parent=QtCore.QModelIndex(), **kwargs):
        return self.insertRows(position, count=1, parent=parent, **kwargs)

    def insertRows(self, position, count, parent=QtCore.QModelIndex(), **kwargs):
        parentItem = self.itemFromIndex(parent)
        position = max(0, min(parentItem.rowCount(), position))
        lastRow = max(0, position + count - 1)

        self.beginInsertRows(parent, position, lastRow)
        parentItem.insertRowDataSources(int(position), int(count), **kwargs)
        self.endInsertRows()

        return True
    # def removeRow(self, position, parent=QtCore.QModelIndex()):
    #     return self.removeRows(position, 1, parent=parent)
    # def removeRows(self, position, count, parent=QtCore.QModelIndex(), **kwargs):
    #     parentNode = self.itemFromIndex(parent)
    #
    #     position = max(0, min(parentNode.rowCount(), position))
    #     lastRow = max(0, position + count - 1)
    #     self.beginRemoveRows(parent, position, lastRow)
    #     result = parentNode.removeRowDataSources(int(position), int(count), **kwargs)
    #     self.endRemoveRows()
    #
    #     return result
    #

    #
    # def moveRow(self, sourceParent, sourceRow, destinationParent, destinationChild):
    #     return self.moveRows(sourceParent, sourceRow, 1, destinationParent, destinationChild)
    #
    # def moveRows(self, sourceParent, sourceRow, count,
    #              destinationParent, destinationChild):
    #     indices = []
    #     for i in range(sourceRow, sourceRow + count):
    #         childIndex = self.index(i, 0, parent=sourceParent)
    #         if childIndex.isValid():
    #             indices.append(childIndex)
    #     mimeData = self.mimeData(indices)
    #     self.removeRows(sourceRow, count, parent=sourceParent)
    #     self.dropMimeData(mimeData, QtCore.Qt.MoveAction, destinationChild, 0, destinationParent)
