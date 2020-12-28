from zoovendor.Qt import QtGui, QtCore


class ObjectModel(QtCore.QObject):
    """ObjectModel class Handles communication between the GUI Elements and the core engine logic,
    Any subclass of ObjectModel must emit the following Signals which require objectModel  or attributeModel
     this will mean you will need to translate any client logic and objects back the objectModel currently
     being referenced.

    """
    # constants for attribute visibility
    ATTRIBUTE_VIS_LEVEL_ZERO = 0
    ATTRIBUTE_VIS_LEVEL_ONE = 1
    ATTRIBUTE_VIS_LEVEL_TWO = 2

    # subclass should emit these signals to update the GUI from the core
    sigAttributeCreated = QtCore.Signal(object)  # attributeModel
    sigAttributeRemoved = QtCore.Signal(object)  # attributeModel
    # sigSelectionChanged = QtCore.Signal(bool)  # bool
    sigAttributeNameChanged = QtCore.Signal(object, str)
    sigAttributeValueChanged = QtCore.Signal(object)
    # Node level signals
    sigNodeNameChanged = QtCore.Signal(str)
    sigBackgroundColourChanged = QtCore.Signal(object)
    sigEdgeColourChanged = QtCore.Signal(object)

    def __init__(self, graph, config, parent=None):
        super(ObjectModel, self).__init__()
        self.graph = graph
        self.config = config
        self._parent = parent
        self._children = []  # type: list[ObjectModel]
        self._icon = ""
        self._attributes = []
        if parent is not None and self not in parent.children():
            parent.children().append(self)

    def __repr__(self):
        return "<{}-{}>".format(self.__class__.__name__, self.text())

    @property
    def properties(self):
        return {}

    @properties.setter
    def properties(self, properties):
        pass

    def fullPathName(self):
        path = self.text()
        if self._parent is not None:
            return "/".join([self._parent.fullPathName(), path])
        return path

    def icon(self):
        """Icon path for the node

        :rtype: str
        """
        return self.properties.get("icon", "")

    def isSelected(self):
        """Returns if the node is currently selected

        :rtype: bool
        """
        return self.properties.get("selected", False)

    def setSelected(self, value):
        """Sets the nodes selection state, gets called from the nodeEditor each time a node is selected.

        :param value: True if the node has been selected in the UI
        :type value: bool
        """
        self.properties["selected"] = value

    def isCompound(self):
        """Returns True if the node is a compound, Compounds a treated as special entities, Eg. Expansion

        :rtype: bool
        """
        return self.properties.get("isCompound", False)

    def isPin(self):
        return self.properties.get("isPin", False)

    def isComment(self):
        return self.properties.get("isComment", False)

    def isBackdrop(self):
        return self.properties.get("isBackdrop", False)

    def category(self):
        """This method returns the node category, each node should be associated with one category the default is
        'Basic'.
        The category is used for the widgets to organize the node library.

        :return: This node category
        :rtype: str
        """
        return self.properties.get("category", "Unknown")

    def text(self):
        """The primary node text usually the node name.

        :return: The Text to display
        :rtype: str
        """
        return self.properties.get("label", "")

    def setText(self, value):
        self.properties["label"] = str(value)

    def secondaryText(self):
        """The Secondary text to display just under the primary text (self.text()).

        :rtype: str
        """
        return self.properties.get("secondaryLabel", "")

    def canCreateAttributes(self):
        """Determines if the user can create attributes on this node.

        :rtype: bool
        """
        return self.properties.get("canCreateAttributes", True)

    def parentObject(self):
        """Parent Object Model, should be a compound node.

        :return: The parent compound ObjectModel
        :rtype: ::class:`ObjectModel`
        """
        return self._parent

    def root(self):
        def _iterParents(objectModel):
            parent = objectModel.parentObject()
            while parent is not None:
                yield parent
                parent = parent.parentObject()

        current = self
        for node in _iterParents(self):
            if node is None:
                return current
            current = node
        return current

    def child(self, index):
        """Retrieve's the child objectModel by index

        :param index: The child index
        :type index: int
        :return: The child Node ObjectModel
        :rtype: ::class:`ObjectModel`
        """
        if index in range(len(self._children)):
            return self._children[index]

    def children(self, recursive=False):
        if recursive:
            children = []
            for child in self._children:
                children.append(child)
                for sub in child.children(recursive=recursive):
                    children.append(sub)
            return children
        return self._children

    def findChild(self, name, recursive=False):
        for child in self._children:
            if child.text() == name:
                return child
            if recursive and child.isCompound():
                child.findChild(name, recursive)

    def __hash__(self):
        return id(self)

    def attribute(self, name):
        """Return the attributeModel by name.

        :param name: The attribute name.
        :type name: str
        :return: An existing AttributeModel of this node
        :rtype: ::class:`ObjectModel` or None
        """
        for attr in self.attributes():
            if attr.text() == name:
                return attr

    def attributes(self, inputs=True, outputs=True, attributeVisLevel=0):
        """List of Attribute models to display on the node.

        :param inputs: return inputs
        :type inputs: bool
        :param outputs: Return outputs
        :type outputs: bool
        :param attributeVisLevel:
        :type attributeVisLevel: int
        :return: Returns a list of AttributeModels containing inputs and outputs(depending of parameters)
        :rtype: list(::class::`AttributeModel`)
        """
        for attribute in self._attributes:
            if inputs and attribute.isInput():
                yield attribute
            elif outputs and attribute.isOutput():
                yield attribute

    def createAttribute(self, attributeDefinition):
        pass

    def deleteAttribute(self, attribute):
        pass

    def hasAttribute(self, name):
        return self.attribute(name) is not None

    def toolTip(self):
        """The Tooltip to display.

        :return: The tooltip which will be display when hovering over the node.
        :rtype: str
        """
        return self.properties.get("toolTip", "")

    def position(self):
        return self.properties.get("position", (0.0, 0.0))

    def setPosition(self, position):
        self.properties["position"] = position

    def width(self):
        return self.properties.get("width", self.minimumWidth())

    def setWidth(self, width):
        self.properties["width"] = width

    def height(self):
        return self.properties.get("height", self.minimumHeight())

    def setHeight(self, height):
        self.properties["height"] = height

    def minimumHeight(self):
        return 50

    def minimumWidth(self):
        return 150

    def cornerRounding(self):
        return 5

    # colors
    def backgroundColour(self):
        return QtGui.QColor(*self.properties.get("backgroundColour", (40, 40, 40, 255)))

    def setBackgroundColour(self, colour):
        self.properties["backgroundColour"] = colour.red(), colour.green(), colour.blue(), colour.alpha()
        self.sigBackgroundColourChanged.emit(colour)

    def headerColour(self):
        return QtGui.QColor(*self.properties.get("headerColour", (71, 115, 149, 255)))

    def textColour(self):
        color = self.properties.get("textColour")
        if color is None:
            return QtGui.QColor(225, 225, 225)
        return QtGui.QColor(*color)

    def setTextColour(self, colour):
        self.properties["textColour"] = colour.red(), colour.green(), colour.blue(), colour.alpha()

    def setSecondaryTextColour(self, colour):
        self.properties["secondaryTextColour"] = colour.red(), colour.green(), colour.blue(), colour.alpha()

    def secondaryTextColour(self):
        color = self.properties.get("secondaryTextColour")
        if color is None:
            return QtGui.QColor(225, 225, 225)
        return QtGui.QColor(*color)

    def setHeaderColour(self, colour):
        self.properties["headerColour"] = colour.red(), colour.green(), colour.blue(), colour.alpha()

    def edgeColour(self):
        return QtGui.QColor(*self.properties.get("edgeColour", (0.0, 0.0, 0.0, 255)))

    def setEdgeColour(self, colour):
        self.properties["edgeColour"] = colour.red(), colour.green(), colour.blue(), colour.alpha()
        self.sigEdgeColourChanged.emit(colour)

    def headerButtonColour(self):
        return QtGui.QColor(255, 255, 255)

    def selectedNodeColour(self):
        return QtGui.QColor(180, 255, 180, 255)

    def edgeThickness(self):
        return 2

    def resizerSize(self):
        return 12

    def deleteChild(self, child):
        for currentChild in self._children:
            if currentChild == child:
                self._children.remove(child)
                child.delete()
                return True

        return False

    def delete(self):
        if self.isCompound():
            for child in self._children:
                child.delete()
        parent = self.parentObject()
        if parent:
            return parent.deleteChild(self)
        return False

    def supportsContextMenu(self):
        return False

    def contextMenu(self, menu):
        pass

    def attributeWidget(self, parent):
        pass

    def graphicsWidget(self, parent):
        pass

    def serialize(self):
        connections = []
        for attr in self._attributes:
            conns = attr.properties.get("connections", [])
            for currentNodeAttr, source in conns:
                connections.append((source.fullPathName(), currentNodeAttr.fullPathName()))
        children = []
        for child in self._children:
            childInfo = child.serialize()
            connections.extend(childInfo["connections"])
            children.append(childInfo)
            if self.isCompound():
                del childInfo["connections"]
        return {"properties": self.properties,
                "attributes": [attr.serialize() for attr in self._attributes],
                "children": children,
                "connections": connections
                }

    def copy(self):
        pass

    def paste(self):
        pass
