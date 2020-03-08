"""
Qt model for the vortex ui which bind slithers core engine and vortex GUI.

FYI: Currently this is being prototyped so it pulls and pushes directly to the core without an undo.

graph
    |-node
        |- attribute
            |- connections
"""
import os

from vortex import startup

startup.initialize()

import logging
import sys
import pprint

from Qt import QtGui, QtWidgets, QtCore
from vortex import api as vortexApi
from zoo.libs.utils import filesystem
from zoo.libs import iconlib

logger = logging.getLogger(__name__)


class Graph(vortexApi.GraphModel):

    def __init__(self, application):
        super(Graph, self).__init__(application)

    def rootNode(self):
        return self._rootNode

    def saveGraph(self, model, filePath=None):
        pprint.pprint(model.serialize())
        filePath = os.path.expanduser("~/vortexGraph/example.vgrh")
        filesystem.ensureFolderExists(os.path.dirname(filePath))
        filesystem.saveJson(model.serialize(), filePath)
        self.graphSaved.emit(filePath)

    def loadFromPath(self, filePath, parent=None):
        graphData = filesystem.loadJson(filePath)
        self.loadFromDict(graphData, parent=parent)

    def loadFromDict(self, data, parent=None):
        root = NodeModel.deserialize(self.config, data, parent=parent)
        self._rootNode = root
        self.graphLoaded.emit(self)
        return root

    def createNode(self, nodeType, parent=None):
        registeredNodes = self.config.registeredNodes()
        if nodeType in registeredNodes:
            nodeInfo = {"data": {"label": nodeType,
                                 "category": "misc",
                                 "secondaryLabel": "bob",
                                 "script": "", "commands": [],
                                 "isPin": nodeType == "pin",
                                 "isBackdrop": nodeType == "backdrop",
                                 "isComment": nodeType == "comment",
                                 "description": ""}
                        }
            newNode = NodeModel.deserialize(self.config, nodeInfo, parent=parent)
            self.nodeCreated.emit(newNode)


class NodeModel(vortexApi.ObjectModel):
    defaults = {
        "text": "",
    }

    @classmethod
    def deserialize(cls, config, data, parent=None):
        newObject = cls(config, parent=parent, **data)
        for child in data.get("children", []):
            NodeModel.deserialize(config, child, parent=newObject)
        return newObject

    def __init__(self, config, parent=None, **kwargs):
        super(NodeModel, self).__init__(config, parent)
        self._data = kwargs.get("data", {})
        self._icon = self._data.get("icon")
        if self._icon is not None:
            self._icon = iconlib.icon(self._icon)
        self._attributeData = kwargs.get("attributes", [])
        for attr in self._attributeData:
            self._attributes.append(AttributeModel(attr, self))

    def isSelected(self):
        """Returns if the node is currently selected

        :rtype: bool
        """
        return self._data.get("selected", False)

    def delete(self):
        if self.isCompound():
            for child in self._children:
                child.delete()
        parent = self.parentObject()
        if parent:
            return parent.deleteChild(self)
        return False

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

    def isPin(self):
        return self._data.get("isPin", False)

    def isComment(self):
        return self._data.get("isComment", False)

    def isBackdrop(self):
        return self._data.get("isBackdrop", False)

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
        self._data["label"] = str(value)
        self.sigNodeNameChanged.emit(str(value))

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
        return self._data.get("canCreateAttributes", True)

    def createAttribute(self, kwargs):
        attr = AttributeModel(kwargs, self)
        self._attributes.append(attr)
        self.sigAddAttribute.emit(attr)

    def deleteAttribute(self, attribute):
        pass

    def toolTip(self):
        """The Tooltip to display.

        :return: The tooltip which will be display when hovering over the node.
        :rtype: str
        """
        return self._data.get("toolTip", "")

    def position(self):
        return self._data.get("position", (0.0, 0.0))

    def setPosition(self, position):
        self._data["position"] = position

    # colors
    def backgroundColour(self):
        return QtGui.QColor(*self._data.get("backgroundColour", (40, 40, 40, 255)))

    def headerColour(self):
        return QtGui.QColor(*self._data.get("headerColour", (71, 115, 149, 255)))

    def edgeColour(self):
        return QtGui.QColor(*self._data.get("edgeColour", (0.0, 0.0, 0.0, 255)))

    def deleteChild(self, child):

        for currentChild in self._children:
            if currentChild == child:
                self._children.remove(child)
                child.delete()
                return True

        return False

    def supportsContextMenu(self):
        return True

    def serialize(self):
        connections = []
        for attr in self._attributes:
            conns = attr.internalAttr.get("connections", [])
            for currentNodeAttr, source in conns:
                connections.append((source.fullPathName(), currentNodeAttr.fullPathName()))
        return {"data": self._data,
                "attributes": [attr.serialize() for attr in self._attributes],
                "children": [child.serialize() for child in self._children],
                "connections": connections
                }


class AttributeModel(vortexApi.AttributeModel):
    def __init__(self, data, objectModel, parent=None):
        super(AttributeModel, self).__init__(objectModel, parent=parent)
        self.internalAttr = data

    def text(self):
        return self.internalAttr.get("label", "unknown")

    def setText(self, text):
        self.internalAttr["label"] = text

    def isInput(self):
        return self.internalAttr.get("isInput", False)

    def isOutput(self):
        return self.internalAttr.get("isOutput", False)

    def setValue(self, value):
        self.internalAttr["value"] = value

    def value(self):
        return self.internalAttr.get("value")

    def isArray(self):
        return self.internalAttr.get("isArray", False)

    def isCompound(self):
        return self.internalAttr.get("isCompound", False)

    def isElement(self):
        return self.internalAttr.get("isElement", False)

    def isChild(self):
        return self.internalAttr.get("isChild", False)

    def hasChildren(self):
        return len(self.internalAttr.get("children", [])) > 0

    def type(self):
        return self.internalAttr.get("type", "string")

    def default(self):
        return self.internalAttr.get("default", "")

    def min(self):
        return self.internalAttr.get("min", 0)

    def max(self):
        return self.internalAttr.get("max", 9999)

    def setType(self, value):
        self.internalAttr["type"] = value

    def setAsInput(self, value):
        self.internalAttr["isInput"] = value

    def setAsOutput(self, value):
        self.internalAttr["isOutput"] = value

    def setDefault(self, value):
        self.internalAttr["default"] = value

    def setMin(self, value):
        self.internalAttr["min"] = value

    def setMax(self, value):
        self.internalAttr["max"] = value

    def setIsCompound(self, value):
        self.internalAttr["isCompound"] = value

    def setIsArray(self, value):
        self.internalAttr["isArray"] = value

    def elements(self):
        items = []
        name = self.text()
        value = self.value()
        if isinstance(value, (list, tuple)):
            isCompound = len(self.internalAttr.get("children", [])) > 0
            for index, elementValue in enumerate(value):
                item = AttributeModel({"label": "{}[{}]".format(name, index),
                                       "isInput": self.isInput(),
                                       "type": "compound",
                                       "isElement": True,
                                       "value": elementValue,
                                       "isOutput": self.isOutput(),
                                       "isArray": False,
                                       "isCompound": isCompound,
                                       "children": self.internalAttr.get("children", [])
                                       }, objectModel=self.objectModel, parent=self)
                items.append(item)
        return items

    def children(self):
        children = []
        for child in self.internalAttr.get("children", []):
            child["isChild"] = True
            item = AttributeModel(child, objectModel=self.objectModel, parent=self)
            children.append(item)
        return children

    def canAcceptConnection(self, plug):
        if self.isInput() and plug.isInput():
            return False
        elif self.isOutput() and plug.isOutput():
            return False
        elif self.isInput() and self.isConnected():
            return False
        return plug != self

    def isConnected(self):
        if self.internalAttr.get("connections"):
            return True
        return False

    def createConnection(self, attribute):
        if self.canAcceptConnection(attribute):
            self.internalAttr.setdefault("connections", []).append((self, attribute))
            return True
        return False

    def deleteConnection(self, attribute):
        connections = self.internalAttr.get("connections", [])
        newConnections = []
        changed = False
        for s_, source in connections:
            if source != attribute:
                newConnections.append((self, source))
                changed = True
        self.internalAttr["connections"] = newConnections
        return changed

    def toolTip(self):
        return self.internalAttr.get("description")

    def backgroundColour(self):
        typeMap = self.objectModel.config.attributeMapping.get(self.internalAttr["type"])
        if typeMap:
            return typeMap["colour"]
        return QtGui.QColor(0, 0, 0)

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


class Config(vortexApi.VortexConfig):
    def registeredNodes(self):
        return {"comment": "organization",
                "sum": "math",
                "float": "math",
                "command": "applications",
                "pin": "organization",
                "backdrop": "organization"}


if __name__ == "__main__":
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    app = QtWidgets.QApplication(sys.argv)
    from zoo.libs.pyqt import stylesheet
    stylesheet.loadDefaultFonts()
    stylesheet.loadDefaultFonts()

    uiConfig = Config()
    vortexApp = vortexApi.UIApplication(uiConfig)
    ui = vortexApi.ApplicationWindow(vortexApp)
    vortexApp.registerGraphType(Graph)
    vortexApp.createGraphFromPath(os.path.join(os.environ["VORTEX"], "vortex/examples/example.vgrh"))

    logger.debug("Completed boot process")

    sys.exit(app.exec_())
