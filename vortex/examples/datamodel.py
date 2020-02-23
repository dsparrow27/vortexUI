"""
Qt model for the vortex ui which bind slithers core engine and vortex GUI.

FYI: Currently this is being prototyped so it pulls and pushes directly to the core without an undo.

"""

from vortex import startup

startup.initialize()

import logging
import sys
import pprint

from Qt import QtGui, QtWidgets, QtCore
from vortex import api as vortexApi

logger = logging.getLogger(__name__)


class Application(vortexApi.UIApplication):
    def __init__(self, uiConfig):
        super(Application, self).__init__(uiConfig)

    def registeredNodes(self):
        return {"comment": "organization",
                "sum": "math",
                "float": "math"}

    def saveGraph(self, model):
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        pprint.pprint(model.serialize())
        print(model)
        # print ("saving", filePath)

    def loadGraph(self, filePath):
        print("loading", filePath)


class SlitherUIObject(vortexApi.ObjectModel):

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

    def position(self):
        return self._data.get("position", (0.0, 0.0))

    def setPosition(self, position):
        self._data["position"] = position

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

        for currentChild in self._children:
            if currentChild == child:
                self._children.remove(child)
                child.delete()
                return True

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

    def fullPathName(self):
        return self.text()

    def serialize(self):
        return {"data": self._data,
                "attributes": [attr.serialize() for attr in self._attributes],
                "children": [child.serialize() for child in self._children]
                },


class AttributeModel(vortexApi.AttributeModel):
    def __init__(self, data, objectModel):
        super(AttributeModel, self).__init__(objectModel)
        self.internalAttr = data

    def fullPathName(self):
        return self.objectModel.fullPathName() + "." + self.text()

    def text(self):
        return self.internalAttr.get("label", "unknown")

    def setText(self, text):
        self.internalAttr["label"] = text

    def isInput(self):
        return self.internalAttr.get("isInput", False)

    def isOutput(self):
        return self.internalAttr.get("isOutput", False)

    def setValue(self, value):
        pass

    def value(self):
        return

    def isArray(self):
        return self.internalAttr.get("isArray", False)

    def isCompound(self):
        return self.internalAttr.get("isCompound", False)

    def isElement(self):
        return self.internalAttr.get("isElement", False)

    def elements(self):
        items = []
        for a in range(10):
            item = AttributeModel({"label": "value{}".format(a),
                                   "isInput": True,
                                   "type": "multi",
                                   "isElement": True,
                                   "isOutput": False}, self.objectModel)
            items.append(item)
        return items

    def children(self):
        return []

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
            self.internalAttr.setdefault("connections", {})[
                attribute.fullPathName() + "|" + self.fullPathName()] = attribute
            return True
        return False

    def deleteConnection(self, attribute):
        key = attribute.fullPathName() + "|" + self.fullPathName()
        connection = self.internalAttr.get("connections", {}).get(key)
        if connection:
            del self.internalAttr["connections"][key]
            return True
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
        typeMap = self.objectModel.config.attributeMapping.get(self.internalAttr["type"])
        if typeMap:
            return typeMap["color"]
        return QtGui.QColor(0, 0, 0)

    def serialize(self):
        return self.internalAttr


def data():
    nodes = [
        {"data": {"label": "float1",
                  "category": "math",
                  "secondaryLabel": "bob",
                  "script": "", "commands": [],
                  "description": ""},
         "attributes": [{"label": "value",
                         "isInput": True,
                         "type": "float",
                         "isOutput": False},
                        {"label": "output",
                         "isInput": False,
                         "type": "float",
                         "isOutput": True},

                        ]
         },
        {"data": {"label": "float2",
                  "category": "math",
                  "secondaryLabel": "bob",
                  "script": "", "commands": [],
                  "description": ""},
         "attributes": [
             {"label": "value",
              "isInput": True,
              "type": "float",
              "isOutput": False},
             {"label": "output",
              "isInput": False,
              "type": "float",
              "isOutput": True}]
         },
        {"data": {"label": "sum",
                  "category": "math",
                  "secondaryLabel": "bob",
                  "script": "", "commands": [],
                  "description": ""},
         "attributes": [{"label": "values",
                         "isInput": True,
                         "isArray": True,
                         "type": "multi",
                         "isOutput": False},
                        {"label": "output",
                         "isInput": False,
                         "isArray": False,
                         "type": "multi",
                         "isOutput": True}
                        ]
         },
        {"data": {"label": "search",
                  "category": "strings",
                  "secondaryLabel": "bob",
                  "script": "",
                  "commands": [],
                  "description": ""},
         "attributes": [{"label": "search", "isInput": True, "type": "string", "isOutput": False},
                        {"label": "toReplace", "isInput": True, "type": "string", "isOutput": False},
                        {"label": "replace", "isInput": True, "type": "string", "isOutput": False},
                        {"label": "result", "isInput": False, "type": "string", "isOutput": True}]},

    ]
    return nodes


if __name__ == "__main__":
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    app = QtWidgets.QApplication(sys.argv)

    uiConfig = vortexApi.VortexConfig()
    vortexApp = Application(uiConfig)

    ui = vortexApi.ApplicationWindow(vortexApp)

    root = SlitherUIObject(uiConfig, None)
    # add a tab te the notebook
    editor = ui.noteBook.addPage(root)
    # add a bunch of nodes to the root
    for n in data():
        editor.addNode(SlitherUIObject(uiConfig, parent=root, **n))

    logger.debug("Completed boot process")

    sys.exit(app.exec_())
