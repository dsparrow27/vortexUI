"""
Qt model for the vortex ui which bind slithers core engine and vortex GUI.

FYI: Currently this is being prototyped so it pulls and pushes directly to the core without an undo.

graph
    |-node
        |- attribute
            |- connections
"""
import os

import logging

from Qt import QtGui, QtWidgets, QtCore
from vortex import api as vortexApi
from zoo.libs.pyqt.widgets import frame, elements
from zoo.libs.utils import filesystem

logger = logging.getLogger(__name__)


class Config(vortexApi.VortexConfig):
    def registeredNodes(self):
        return {"comment": "organization",
                "sum": "math",
                "float": "math",
                "command": "applications",
                "pin": "organization",
                "backdrop": "organization"}


class Graph(vortexApi.GraphModel):

    def __init__(self, application):
        super(Graph, self).__init__(application)

    def rootNode(self):
        return self._rootNode

    def saveGraph(self, filePath=None):
        model = self.rootNode()
        filePath = os.path.expanduser(filePath)
        filesystem.ensureFolderExists(os.path.dirname(filePath))
        filesystem.saveJson(model.serialize(), filePath)
        self.application.events.modelGraphSaved.emit(filePath)

    def loadFromPath(self, filePath, parent=None):
        graphData = filesystem.loadJson(filePath)
        return self.loadFromDict(graphData, parent=parent)

    def loadFromDict(self, data, parent=None):
        nodes = self.createNodeFromInfo(data, parent=parent)
        self._rootNode = nodes[0]
        self.application.events.modelGraphLoaded.emit(self)
        return self._rootNode

    def createNode(self, nodeType, parent=None):
        registeredNodes = self.config.registeredNodes()
        if nodeType in registeredNodes:
            nodeInfo = {"properties": {"label": nodeType,
                                 "category": "misc",
                                 "secondaryLabel": "bob",
                                 "script": "", "commands": [],
                                 "isPin": nodeType == "pin",
                                 "isBackdrop": nodeType == "backdrop",
                                 "isComment": nodeType == "comment",
                                 "description": ""}
                        }
            nodes = self.createNodeFromInfo(nodeInfo, parent=parent)
            self.application.events.modelNodesCreated.emit(nodes)

    def createNodeFromInfo(self, info, parent=None):
        data = dict(properties=info["properties"],
                    attributes=info.get("attributes", []))
        connections = info.get("connections", [])
        parent = NodeModel(self.config, data, parent=parent)
        createdNodes = [parent]
        remappedNodes = {data["properties"]["label"]: parent}
        for child in info.get("children", []):
            childModel = NodeModel(self.config, child, parent=parent)
            createdNodes.append(childModel)
            name = child["properties"].get("label")
            remappedNodes[name] = childModel

        # handle connections
        for source, destination in connections:
            sourceName, sourceAttrName = source.split("|")[-1].split(".")
            destinationName, destAttrName = destination.split("|")[-1].split(".")
            sourceNode = remappedNodes.get(sourceName)
            destinationNode = remappedNodes.get(destinationName)
            sourceAttr = sourceNode.attribute(sourceAttrName)
            destinationAttr = destinationNode.attribute(destAttrName)
            if not sourceAttr or not destinationAttr:
                continue
            sourceAttr.createConnection(destinationAttr)
        return createdNodes


class NodeModel(vortexApi.ObjectModel):
    def __init__(self, config, properties, parent=None):
        super(NodeModel, self).__init__(config, properties=properties, parent=parent)

    def createAttribute(self, kwargs):
        attr = AttributeModel(self, kwargs)
        self._attributes.append(attr)
        self.sigAddAttribute.emit(attr)

    def attributeWidget(self, parent):
        from vortex.plugins.ui.attributeeditor import attributewidgets
        parentFrame = frame.QFrame(parent=parent)
        layout = elements.vBoxLayout(parentFrame)
        for model in self.attributes():
            dataType = model.type()
            if dataType == "string":
                layout.addWidget(attributewidgets.StringWidget(model, parent=parentFrame))

        return parentFrame


class AttributeModel(vortexApi.AttributeModel):
    def __init__(self, objectModel, properties, parent=None):
        super(AttributeModel, self).__init__(objectModel, properties, parent=parent)

    def elements(self):
        items = []
        name = self.text()
        value = self.value()
        if isinstance(value, (list, tuple)):
            isCompound = len(self.properties.get("children", [])) > 0
            for index, elementValue in enumerate(value):
                item = AttributeModel({"label": "{}[{}]".format(name, index),
                                       "isInput": self.isInput(),
                                       "type": "compound",
                                       "isElement": True,
                                       "value": elementValue,
                                       "isOutput": self.isOutput(),
                                       "isArray": False,
                                       "isCompound": isCompound,
                                       "children": self.properties.get("children", [])
                                       }, objectModel=self.objectModel, parent=self)
                items.append(item)
        return items

    def children(self):
        children = []
        for child in self.properties.get("children", []):
            child["isChild"] = True
            item = AttributeModel(child, objectModel=self.objectModel, parent=self)
            children.append(item)
        return children

    def createConnection(self, attribute):

        if self.canAcceptConnection(attribute):
            if self.isInput():
                self.properties.setdefault("connections", []).append((self, attribute))
            else:
                self.properties.setdefault("connections", []).append((attribute, self))
            return True
        return False

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

    def backgroundColour(self):
        typeMap = self.objectModel.config.attributeMapping.get(self.properties["type"])
        if typeMap:
            return typeMap["colour"]
        return QtGui.QColor(0, 0, 0)
