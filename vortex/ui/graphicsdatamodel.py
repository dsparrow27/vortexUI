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

    # signals connected by the graphics scene
    addConnectionSig = QtCore.Signal(object, object)  # sourceAttrModel, destAttrModel
    removeConnectionSig = QtCore.Signal(object, object)  # sourceAttributeModel, destinationModel

    # connected by the GraphicsNode
    addAttributeSig = QtCore.Signal(object)  # attributeModel
    nodeNameChangedSig = QtCore.Signal(object)  # objectModel
    removeAttributeSig = QtCore.Signal(object)  # attributeModel
    attributeNameChangedSig = QtCore.Signal(object)  # attributeModel
    valueChangedSig = QtCore.Signal(object)  # attributeModel
    selectionChangedSig = QtCore.Signal(bool)  # selectionState
    parentChangedSig = QtCore.Signal(object, object)  # childObjectModel, parentObjectModel
    progressUpdatedSig = QtCore.Signal(object, object)  # objectModel
    requestRefresh = QtCore.Signal()

    def __init__(self, config, parent=None):
        super(ObjectModel, self).__init__()
        self.config = config
        self._parent = parent
        self._children = []
        self._icon = ""
        self._attributes = []
        if parent is not None and self not in parent.children():
            parent._children.append(self)

    def __repr__(self):
        return "<{}-{}>".format(self.__class__.__name__, self.text())

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

    def child(self, index):
        """Retrieve's the child objectModel by index

        :param index: The child index
        :type index: int
        :return: The child Node ObjectModel
        :rtype: ::class:`ObjectModel`
        """
        if index in xrange(len(self._children)):
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

    def createAttribute(self, **kwargs):
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

    def minimumHeight(self):
        return 80

    def minimumWidth(self):
        return 150

    def cornerRounding(self):
        return 10

    # colors
    def backgroundColour(self):
        return QtGui.QColor(50, 50, 50, 225)

    def headerColor(self):
        return QtGui.QColor("#4A71AB")

    def headerButtonColor(self):
        return QtGui.QColor(255, 255, 255)

    def selectedNodeColour(self):
        return QtGui.QColor(180, 255, 180, 200)

    def unSelectedNodeColour(self):
        return self.backgroundColour()

    def edgeColour(self):
        return QtGui.QColor(0.0, 0.0, 0.0, 255)

    def edgeThickness(self):
        return 3

    def deleteChild(self, child):
        return False

    def supportsContextMenu(self):
        return False

    def contextMenu(self, menu):
        pass

    def attributeWidget(self, parent):
        pass


class AttributeModel(QtCore.QObject):
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

    def text(self):
        return "attributeName"

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

    def isElement(self):
        if self.parent is not None:
            return self.parent.isArray()

    def isCompound(self):
        return False

    def elements(self):
        return []

    def children(self):
        return []

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

    def itemEdgeColor(self):
        return QtGui.QColor(0, 180, 0)

    def itemColour(self):
        return QtGui.QColor(0, 180, 0)
