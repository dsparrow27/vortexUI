from Qt import QtGui, QtCore


class AttributeModel(QtCore.QObject):
    defaultFields = {"label": "value",
                     "description": "",
                     "isInput": True,
                     "isOutput": False,
                     "type": "multi",
                     "isArray": False,
                     "isCompound": False,
                     "default": 0.0,
                     "value": 0.0,
                     "min": 0.0,
                     "max": 99999999,
                     }

    def __init__(self, objectModel, parent=None):
        """
        :param objectModel: The Node ObjectModel
        :type objectModel: ::class:`ObjectModel`
        """
        super(AttributeModel, self).__init__()
        self.objectModel = objectModel
        self.parent = parent

    def __repr__(self):
        return "<{}-{}>".format(self.__class__.__name__, self.text())

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __ne__(self, other):
        return hash(self) != hash(other)

    def __hash__(self):
        return id(self)

    def fullPathName(self):
        return self.objectModel.fullPathName() + "." + self.text()

    def text(self):
        return "attributeName"

    def description(self):
        return ""

    def setValue(self, value):
        pass

    def value(self):
        return

    def textAlignment(self):
        if self.isInput():
            return QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter
        else:
            return QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter

    def setText(self, text):
        return False

    def isArray(self):
        return False

    def setIsArray(self):
        pass

    def isElement(self):
        if self.parent is not None:
            return self.parent.isArray()

    def isCompound(self):
        return False

    def type(self):
        pass

    def default(self):
        pass

    def min(self):
        pass

    def max(self):
        pass

    def setType(self, value):
        pass

    def setAsInput(self, value):
        pass

    def setAsOutput(self, value):
        pass

    def setDefault(self, value):
        pass

    def setMin(self, value):
        pass

    def setMax(self, value):
        pass

    def setIsCompound(self, value):
        pass

    def setIsArray(self, value):
        pass

    def elements(self):
        return []

    def children(self):
        return []

    def hasChildren(self):
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

    def highlightColour(self):
        return QtGui.QColor(255, 255, 255)

    def edgeColour(self):
        return QtGui.QColor(25, 25, 25)

    def backgroundColour(self):
        return QtGui.QColor(0, 180, 0)

    def serialize(self):
        return {}
