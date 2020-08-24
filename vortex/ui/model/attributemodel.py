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

    def __init__(self, objectModel, properties, parent=None):
        """
        :param objectModel: The Node ObjectModel
        :type objectModel: ::class:`ObjectModel`
        """
        super(AttributeModel, self).__init__()
        self.objectModel = objectModel
        self.parent = parent
        self._properties = properties

    @property
    def properties(self):
        return self._properties

    @properties.setter
    def properties(self, properties):
        self._properties = properties

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
        return self._properties.get("label", "unknown")

    def setText(self, text):
        self._properties["label"] = text

    def description(self):
        return self._properties.get("description", "")

    def isInput(self):
        return self._properties.get("isInput", False)

    def isOutput(self):
        return self._properties.get("isOutput", False)

    def setValue(self, value):
        self._properties["value"] = value

    def value(self):
        return self._properties.get("value")

    def isArray(self):
        return self._properties.get("isArray", False)

    def isCompound(self):
        return self._properties.get("isCompound", False)

    def isElement(self):
        return self._properties.get("isElement", False)

    def isChild(self):
        return self._properties.get("isChild", False)

    def hasChildren(self):
        return len(self._properties.get("children", [])) > 0

    def type(self):
        return self._properties.get("type", "string")

    def default(self):
        return self._properties.get("default", 0)

    def min(self):
        return self._properties.get("min", 0)

    def max(self):
        return self._properties.get("max", 9999)

    def setType(self, value):
        self._properties["type"] = value

    def setAsInput(self, value):
        self._properties["isInput"] = value

    def setAsOutput(self, value):
        self._properties["isOutput"] = value

    def setDefault(self, value):
        self._properties["default"] = value

    def setMin(self, value):
        self._properties["min"] = value

    def setMax(self, value):
        self._properties["max"] = value

    def setIsCompound(self, value):
        self._properties["isCompound"] = value

    def setIsArray(self, value):
        self._properties["isArray"] = value

    def textAlignment(self):
        if self.isInput():
            return QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter
        else:
            return QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter

    def elements(self):
        return []

    def children(self):
        return []

    def acceptsMultipleConnections(self):
        if self.isInput():
            return False
        return True

    def isConnected(self):
        if self.properties.get("connections"):
            return True
        return False

    def canAcceptConnection(self, plug):
        if self.isInput() and plug.isInput():
            return False
        elif self.isOutput() and plug.isOutput():
            return False
        elif self.isInput() and self.isConnected():
            return False
        return plug != self

    def connections(self):
        return iter(self.properties.get("connections", []))

    def toolTip(self):
        return self.properties.get("description")

    def createConnection(self, attribute):

        if self.isInput():
            self.properties.setdefault("connections", []).append((self, attribute))
        else:
            self.properties.setdefault("connections", []).append((attribute, self))
        return True

    def deleteConnection(self, attribute):
        connections = self.properties.get("connections", [])
        newConnections = []
        changed = False
        for s_, source in connections:
            if source == attribute:
                newConnections.append((self, source))
                changed = True
        self.properties["connections"] = newConnections
        return changed

    def size(self):
        return QtCore.QSize(150, 30)

    def textColour(self):
        return QtGui.QColor(200, 200, 200)

    def highlightColour(self):
        return QtGui.QColor(255, 255, 255)

    def edgeColour(self):
        return QtGui.QColor(0, 180, 0)

    def backgroundColour(self):
        if self.isConnected():
            return self.edgeColour()
        return QtGui.QColor(25, 25, 25)

    def serialize(self):
        return {
            "label": self.text(),
            "isInput": self.isInput(),
            "type": self.type(),
            "isElement": self.isElement(),
            "isChild": self.isChild(),
            "isOutput": self.isOutput(),
            "isArray": self.isArray(),
            "isCompound": self.isCompound(),
            "children": [child.serialize() for child in self.children()],
            "min": self.min(),
            "max": self.max(),
            "value": self.value(),
            "default": self.default()
        }
