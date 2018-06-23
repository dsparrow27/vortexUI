from qt import QtGui, QtCore


class ObjectModel(QtCore.QObject):
    def __init__(self, config, parent=None):
        super(ObjectModel, self).__init__()
        self.config = config
        self._parent = parent
        self._children = []
        self._icon = QtGui.QIcon()
        if parent is not None and self not in parent.children():
            parent._children.append(self)

    def icon(self):
        return self._icon

    def isSelected(self):
        return False

    def setSelected(self, value):
        pass

    def isCompound(self):
        return False

    def category(self):
        """This method returns the node category, each node should be associated with one category the default is 'Basic'.
        The category is used for the widgets to organize the node library.

        :return: This node category
        :rtype: str
        """
        return "Basic"

    def icon(self):
        return QtGui.QIcon()

    def parentObject(self):
        return self._parent

    def child(self, index):
        if index in range(len(self._children)):
            return self._children[index]

    def children(self):
        return self._children

    def __hash__(self):
        return id(self)

    def text(self):
        return "primary header"

    def secondaryText(self):
        return ""

    def attributes(self, inputs=True, outputs=True):
        return []

    def canCreateAttributes(self):
        return False

    def createAttribute(self, **kwargs):
        pass

    def deleteAttribute(self, attribute):
        pass

    def hasAttribute(self, name):
        return True

    def toolTip(self):
        return "hello world"

    def minimumHeight(self):
        return 80

    def minimumWidth(self):
        return 150

    def cornerRounding(self):
        return 10

    # colors
    def backgroundColour(self):
        return QtGui.QColor(31, 33, 34, 255)

    def headerColor(self):
        return QtGui.QColor("#4A71AB")

    def headerButtonColor(self):
        return QtGui.QColor(255, 255, 255)

    def selectedNodeColour(self):
        return QtGui.QColor(180, 255, 180, 255)

    def unSelectedNodeColour(self):
        return self.backgroundColour()

    def edgeColour(self):
        return QtGui.QColor(0.0, 0.0, 0.0, 255)

    def edgeThickness(self):
        return 2

    def deleteChild(self, child):
        return False

    def supportsContextMenu(self):
        return False

    def contextMenu(self, menu):
        pass


class AttributeModel(QtCore.QObject):
    def __init__(self, objectModel):
        super(AttributeModel, self).__init__()
        self.objectModel = objectModel

    def __hash__(self):
        return id(self)

    def text(self):
        return "attributeName"

    def setText(self, text):
        return False

    def canAcceptConnection(self, plug):
        return True

    def acceptsMultipleConnections(self):
        if self.isInput():
            return False
        return True

    def isConnected(self):
        return False

    def createConnection(self, attribute):
        return False

    def deleteConnection(self, attribute):
        return False

    def toolTip(self):
        return "Im a tooltip for attributes"

    def size(self):
        return QtCore.QSize(150, 30)

    def textColour(self):
        return QtGui.QColor(200, 200, 200)

    def isInput(self):
        return True

    def isOutput(self):
        return True

    def highlightColor(self):
        return QtGui.QColor(255, 255, 255)

    def itemColour(self):
        return QtGui.QColor(0, 180, 0)


class InAttributeModel(AttributeModel):
    def isInput(self):
        return True

    def isOutput(self):
        return False


class OutAttributeModel(AttributeModel):
    def isInput(self):
        return False

    def isOutput(self):
        return True
