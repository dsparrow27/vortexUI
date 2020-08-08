from Qt import QtGui, QtCore


class ObjectModel(QtCore.QObject):
    """ObjectModel class Handles communication between the GUI Elements and the core engine logic,
    Any subclass of ObjectModel must emit the following Signals which require objectModel  or attributeModel
     this will mean you will need to translate any client logic and objects back the objectModel currently
     being referenced.
        addConnectionSig
        removeConnectionSig
        addAttributeSig
        nodeNameChangedSig
        removeAttributeSig
        attributeNameChangedSig
        valueChangedSig
        selectionChangedSig
        parentChangedSig
        progressUpdatedSig

    """
    # constants for attribute visibility
    ATTRIBUTE_VIS_LEVEL_ZERO = 0
    ATTRIBUTE_VIS_LEVEL_ONE = 1
    ATTRIBUTE_VIS_LEVEL_TWO = 2

    # subclass should emit these signals to update the GUI from the core
    sigAddAttribute = QtCore.Signal(object)  # attributeModel
    sigRemoveAttribute = QtCore.Signal(object)  # attributeModel
    sigSelectionChanged = QtCore.Signal(bool)  # bool

    # # signals connected by the graphics scene
    # addConnectionSig = QtCore.Signal(object, object)  # sourceAttrModel, destAttrModel
    # removeConnectionSig = QtCore.Signal(object, object)  # sourceAttributeModel, destinationModel
    #
    # # connected by the GraphicsNode
    sigNodeNameChanged = QtCore.Signal(str)  # objectModel

    # attributeNameChangedSig = QtCore.Signal(object)  # attributeModel
    # parentChangedSig = QtCore.Signal(object, object)  # childObjectModel, parentObjectModel
    # progressUpdatedSig = QtCore.Signal(object, object)  # objectModel
    # requestRefresh = QtCore.Signal()

    def __init__(self, config, parent=None):
        super(ObjectModel, self).__init__()
        self.config = config
        self._parent = parent
        self._children = []
        self._icon = ""
        self._attributes = []
        if parent is not None and self not in parent.children():
            parent._children.append(self)

        # self.sigAddAttribute.connect(self.createAttribute)

    def __repr__(self):
        return "<{}-{}>".format(self.__class__.__name__, self.text())

    def fullPathName(self):
        path = self.text()
        if self._parent is not None:
            return "|".join([self._parent.fullPathName(), path])
        return path

    def icon(self):
        """Icon path for the node

        :rtype: str
        """
        return self._icon

    def isSelected(self):
        """Returns if the node is currently selected

        :rtype: bool
        """
        return False

    def setSelected(self, value):
        """Sets the nodes selection state, gets called from the nodeEditor each time a node is selected.

        :param value: True if the node has been selected in the UI
        :type value: bool
        """
        pass

    def isCompound(self):
        """Returns True if the node is a compound, Compounds a treated as special entities, Eg. Expansion

        :rtype: bool
        """
        return False

    def category(self):
        """This method returns the node category, each node should be associated with one category the default is 'Basic'.
        The category is used for the widgets to organize the node library.

        :return: This node category
        :rtype: str
        """
        return "Basic"

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

    def children(self):
        return self._children

    def __hash__(self):
        return id(self)

    def text(self):
        """The primary node text usually the node name.

        :return: The Text to display
        :rtype: str
        """
        return "primary header"

    def setText(self, value):
        pass

    def secondaryText(self):
        """The Secondary text to display just under the primary text (self.text()).

        :rtype: str
        """
        return ""

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
        return []

    def canCreateAttributes(self):
        """Determines if the user can create attributes on this node.

        :rtype: bool
        """
        return False

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
        return "hello world"

    def properties(self):
        return {}

    def minimumHeight(self):
        return 50

    def minimumWidth(self):
        return 150

    def cornerRounding(self):
        return 5

    def position(self):
        return (0, 0)

    def setPosition(self, position):
        pass

    def width(self):
        return self.minimumWidth()

    def setWidth(self, width):
        pass

    def height(self):
        return self.minimumHeight()

    def setHeight(self, height):
        pass

    # colours
    def backgroundColour(self):
        return QtGui.QColor(50, 50, 50, 225)

    def setBackgroundColour(self, colour):
        pass

    def headerColour(self):
        return QtGui.QColor("#4A71AB")

    def setHeaderColour(self, colour):
        pass

    def headerButtonColour(self):
        return QtGui.QColor(255, 255, 255)

    def selectedNodeColour(self):
        return QtGui.QColor(180, 255, 180, 255)

    def edgeColour(self):
        return QtGui.QColor(0.0, 0.0, 0.0, 255)

    def textColor(self):
        return QtGui.QColor(225, 225, 225)

    def edgeThickness(self):
        return 2

    def resizerSize(self):
        return 12

    def deleteChild(self, child):
        return False

    def delete(self):
        return False

    def supportsContextMenu(self):
        return False

    def contextMenu(self, menu):
        pass

    def attributeWidget(self, parent):
        pass

    def serialize(self):
        return {}

    def copy(self):
        pass

    def paste(self):
        pass
