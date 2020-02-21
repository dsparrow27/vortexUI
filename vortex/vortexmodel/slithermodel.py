"""
Qt model for the vortex ui which bind slithers core engine and vortex GUI.

FYI: Currently this is being prototyped so it pulls and pushes directly to the core without an undo.

"""
import logging
from Qt import QtGui, QtWidgets, QtCore
from vortex.ui import application, graphicsdatamodel

logger = logging.getLogger(__name__)

ATTRIBUTE_DISCONNECTED_COLOR = QtGui.QColor(2, 25, 25)
NODECOLORMAP = {}


class Application(application.UIApplication):
    def __init__(self, uiConfig):
        super(Application, self).__init__(uiConfig)
        self.nodes = [{"a": "b"}]
        # self.currentModel = SlitherUIObject(self.nodes[0], self.config)
        # self.currentModel._children = [SlitherUIObject(None, self.config, parent=self.currentModel)]
        # self.models["a"] = self.currentModel

    def initialize(self):
        pass
        # self.onNewNodeRequested.emit({"model": self.currentModel,
        #                               "newTab": True})
        # self.onNewNodeRequested.emit({"model": SlitherUIObject(None, self.config, parent=self.currentModel),
        #                               "newTab": False})

    def onNodeCreated(self, Type):
        print(Type)

    def registeredNodes(self):
        return {"organization": "comment"}


class SlitherUIObject(graphicsdatamodel.ObjectModel):

    def __init__(self, config, parent=None, **kwargs):
        super(SlitherUIObject, self).__init__(config, parent)
        self._icon = kwargs.get("icon", "")
        self._data = kwargs.get("data", {})
        self._attributeData = kwargs.get("attributes", [])
        for attr in self._attributeData:
            self._attributes.append(AttributeModel(attr, self))

    def isSelected(self):
        """Returns if the node is currently selected

        :rtype: bool
        """
        return self._data.get("selected", False)

    def setSelected(self, value):
        """Sets the nodes selection state, gets called from the nodeEditor each time a node is selected.

        :param value: True if the node has been selected in the UI
        :type value: bool
        """
        self._data["selected"] = value

    def isCompound(self):
        """Returns True if the node is a compound, Compounds a treated as special entities, Eg. Expansion

        :rtype: bool
        """
        return self._data.get("isCompound", False)

    def category(self):
        """This method returns the node category, each node should be associated with one category the default is
        'Basic'.
        The category is used for the widgets to organize the node library.

        :return: This node category
        :rtype: str
        """
        return self._data.get("category", "Unknown")

    def text(self):
        """The primary node text usually the node name.

        :return: The Text to display
        :rtype: str
        """
        return self._data.get("label", "")

    def setText(self, value):
        self._data["secondaryLabel"] = str(value)

    def secondaryText(self):
        """The Secondary text to display just under the primary text (self.text()).

        :rtype: str
        """
        return self._data.get("secondaryLabel", "")

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
        return self._attributes

    def canCreateAttributes(self):
        """Determines if the user can create attributes on this node.

        :rtype: bool
        """
        return self._data.get("canCreateAttributes", False)

    def createAttribute(self, **kwargs):
        pass

    def deleteAttribute(self, attribute):
        pass

    def toolTip(self):
        """The Tooltip to display.

        :return: The tooltip which will be display when hovering over the node.
        :rtype: str
        """
        return self._data.get("toolTip", "")

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
        return True

    def contextMenu(self, menu):
        menu.addAction("Edit Node", triggered=self._onEdit)

    def attributeWidget(self, parent):
        pass

    def _onEdit(self, *args, **kwargs):
        print(args, kwargs)
        # script
        # plugs
        # plugs ui
        # plug ui hook
        # UI command


class AttributeModel(graphicsdatamodel.AttributeModel):
    def __init__(self, slitherAttribute, objectModel):
        super(AttributeModel, self).__init__(objectModel)
        self.internalAttr = slitherAttribute
        # print(self.internalAttr)
        # print(self.objectModel)

    def text(self):
        return self.internalAttr.get("label", "unknown")

    def isInput(self):
        return self.internalAttr.get("isInput", False)

    def isOutput(self):
        return self.internalAttr.get("isOutput", False)

    def text(self):
        return "attributeName"

    def setValue(self, value):
        pass

    def value(self):
        return

    def isArray(self):
        return False

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
        return self.internalAttr.get("description")

    def size(self):
        return QtCore.QSize(150, 30)

    def textColour(self):
        return QtGui.QColor(200, 200, 200)

    def highlightColor(self):
        return QtGui.QColor(255, 255, 255)

    def itemEdgeColor(self):
        return QtGui.QColor(0, 180, 0)

    def itemColour(self):
        return QtGui.QColor(0, 180, 0)
