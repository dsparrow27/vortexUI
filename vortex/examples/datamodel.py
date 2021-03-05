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

from zoovendor.Qt import QtGui, QtWidgets, QtCore
from vortex import api as vortexApi
from zoo.libs.pyqt.widgets import frame, elements
from zoo.libs.utils import filesystem
from vortex.ui import attributewidgets

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


class Config(vortexApi.VortexConfig):

    def __init__(self):
        super(Config, self).__init__()
        self.registerAttributeWidget("string", attributewidgets.StringWidget)
        self.registerAttributeWidget("path", attributewidgets.PathWidget)
        self.registerAttributeWidget("float", attributewidgets.NumericAttributeWidget)
        self.registerAttributeWidget("int", attributewidgets.NumericAttributeWidget)

    def registeredNodes(self):
        return {"comment": "organization",
                "sum": "math",
                "float": "math",
                "command": "applications",
                "pin": "organization",
                "backdrop": "organization", "compound": "organization"}


class Application(vortexApi.UIApplication):

    def __init__(self, uiConfig):
        super(Application, self).__init__(uiConfig)

    def createNewGraph(self, name=None):
        self._onGraphCreate(name=name)

    def createGraphFromPath(self, filePath, name=None, parent=None):
        graphData = filesystem.loadJson(filePath)
        newGraphInstance = Graph(self, name or "NEWGRAPH")
        newGraphInstance.loadFromDict(graphData, parent=parent)
        self._onGraphCreate(name, newGraphInstance)

    def _onGraphCreate(self, name, graph=None):
        if graph is None:
            graph = Graph(self, name or "NEWGRAPH")
            graph.rootNode = NodeModel(graph, self.config,
                                       properties={},
                                       parent=None
                                       )
        self.sigGraphCreated.emit(graph)


class Graph(vortexApi.GraphModel):

    def __init__(self, application, name):
        super(Graph, self).__init__(application, name)

    def saveGraph(self, filePath=None):
        model = self.rootNode
        filePath = os.path.expanduser(filePath)
        filesystem.ensureFolderExists(os.path.dirname(filePath))
        filesystem.saveJson(model.serialize(), filePath)
        self.application.events.modelGraphSaved.emit(filePath)

    def loadFromPath(self, filePath, parent=None):
        graphData = filesystem.loadJson(filePath)
        return self.loadFromDict(graphData, parent=parent)

    def loadFromDict(self, data, parent=None):
        return self.createNodeFromInfo(data, parent=parent)

    def createNode(self, nodeType, parent=None):
        registeredNodes = self.config.registeredNodes()
        if nodeType in registeredNodes:
            nodeInfo = {"properties": {"label": nodeType,
                                       "category": registeredNodes[nodeType],
                                       "secondaryLabel": nodeType,
                                       "script": "", "commands": [],
                                       "isPin": nodeType == "pin",
                                       "isBackdrop": nodeType == "backdrop",
                                       "isComment": nodeType == "comment",
                                       "isCompound": nodeType == "compound",
                                       "children": [],
                                       "description": ""}
                        }
            nodes = self.createNodeFromInfo(nodeInfo, parent=parent)
            self.application.events.modelNodesCreated.emit(nodes)

    def createNodeFromInfo(self, info, parent=None):
        data = dict(properties=info["properties"],
                    attributes=info.get("attributes", []))
        connections = info.get("connections", [])
        if parent is None:
            parent = self._rootNode
        parent = NodeModel(self, self.config, data, parent=parent)
        createdNodes = [parent]
        remappedNodes = {data["properties"]["label"]: parent}
        for child in info.get("children", []):
            childModel = NodeModel(self, self.config, child, parent=parent)
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

    def customToolbarActions(self, parent):
        action = parent.addAction("Execute")
        action.triggered.connect(self._execute)

    def _execute(self):
        selection = []
        for child in self.rootNode.children(recursive=True):
            if child.isSelected():
                selection.append(child)
                child.properties["edgeColor"] = 255, 0, 0, 1


class NodeModel(vortexApi.ObjectModel):
    def __init__(self, graph, config, properties, parent=None):
        super(NodeModel, self).__init__(graph, config, parent=parent)
        self.properties = properties

    def createAttribute(self, kwargs):
        attr = TestModel(self, kwargs)
        self._attributes.append(attr)
        self.sigAddAttribute.emit(attr)

    def attributeWidget(self, parent):
        parentFrame = frame.QFrame(parent=parent)
        layout = elements.vBoxLayout(parentFrame)
        for model in self.attributes(outputs=False):
            attributeWidget = self.config.attributeWidgetForType(model.type())
            if not attributeWidget:
                continue
            layout.addWidget(attributeWidget(model, parent=parentFrame))
        return parentFrame


class TestModel(vortexApi.AttributeModel):
    def elements(self):
        items = []
        name = self.text()
        value = self.value()
        if isinstance(value, (list, tuple)):
            isCompound = len(self.properties.get("children", [])) > 0
            for index, elementValue in enumerate(value):
                item = TestModel(objectModel=self.objectModel,
                                 properties={"label": "{}[{}]".format(name, index),
                                             "isInput": self.isInput(),
                                             "type": "compound",
                                             "isElement": True,
                                             "value": elementValue,
                                             "isOutput": self.isOutput(),
                                             "isArray": False,
                                             "isCompound": isCompound,
                                             "children": self.properties.get("children", [])
                                             }, parent=self)
                items.append(item)
        return items

    def children(self):
        children = []
        for child in self.properties.get("children", []):
            child["isChild"] = True
            item = TestModel(objectModel=self.objectModel, properties=child, parent=self)
            children.append(item)
        return children

    def deleteConnection(self, attribute):
        connections = self.properties.get("connections", [])
        newConnections = []
        logger.debug("current Connections {}".format(connections))

        for s_, source in connections:
            if source != attribute:
                newConnections.append((self, source))

        logger.debug("new Connections: {}".format(newConnections))
        self.properties["connections"] = newConnections
        return len(connections) != len(newConnections)

    def edgeColour(self):
        return self.backgroundColour().darker()

    def backgroundColour(self):
        typeMap = self.objectModel.config.attributeMapping.get(self.properties["type"])
        if typeMap:
            return typeMap["colour"]
        return QtGui.QColor(0, 0, 0)
