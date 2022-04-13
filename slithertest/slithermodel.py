# """
# Qt model for the vortex ui which bind slithers core engine and vortex GUI.
#
# FYI: Currently this is being prototyped so it pulls and pushes directly to the core without an undo.
#
# graph
#     |-node
#         |- attribute
#             |- connections
# """
import pprint

from zoovendor.Qt import QtGui, QtWidgets, QtCore
from vortex import api as vortexApi
from vortex.ui import attributewidgets
from slither import api
from zoo.core.util import zlogging
from nodewidgets import pythonnode

logger = zlogging.getLogger(__name__)


class Application(vortexApi.UIApplication):

    def __init__(self, uiConfig):
        super(Application, self).__init__(uiConfig)
        self.internalApp = api.Application()
        for nType, obj in self.internalApp.registry.nodeTypes.items():
            uiConfig.types[nType] = obj["info"]["category"]
        self.internalApp.events.graphCreated.connect(self._onGraphCreate)

    def _onGraphCreate(self, _, graph):
        newGraphInstance = Graph(self, graph.name, graph=graph)
        newGraphInstance.rootNode = NodeModel(graph.root, newGraphInstance, self.config,
                                              parent=None
                                              )
        self.sigGraphCreated.emit(newGraphInstance)

    def createNewGraph(self, name=None):
        self.internalApp.createGraph(name)

    def createGraphFromPath(self, filePath, name=None, parent=None):
        if self.graphNoteBook is None or self.graphType is None:
            return
        self.internalApp.createGraphFromPath(name, filePath)


class Config(vortexApi.VortexConfig):

    def __init__(self):
        super(Config, self).__init__()

        self.types = {}
        self.attributeMapping = {
            'kQuaternion': {"colour": QtGui.QColor(230, 115, 115)},
            'kColour': {"colour": QtGui.QColor(130, 217, 159)},
            'kMatrix4': {"colour": QtGui.QColor(230, 115, 115)},
            'multi': {"colour": QtGui.QColor(230, 115, 115)},
            'kVector2D': {"colour": QtGui.QColor(130, 217, 159)},
            'kVector3D': {"colour": QtGui.QColor(130, 217, 159)},
            "kFile": {"colour": QtGui.QColor(217, 190, 108)},
            "kDirectory": {"colour": QtGui.QColor(217, 190, 108)},
            "kBool": {"colour": QtGui.QColor(230, 153, 99)},
            "kDict": {"colour": QtGui.QColor(204.0, 127.5, 163.20000000000002)},
            "kFloat": {"colour": QtGui.QColor(168, 217, 119)},
            "integer": {"colour": QtGui.QColor(98, 207, 217)},
            "kList": {"colour": QtGui.QColor(56.000040000000006, 47.99992500000001, 45.00010500000001)},
            "kString": {"colour": QtGui.QColor(217, 190, 108)}
        }
        self.registerAttributeWidget("kString", attributewidgets.StringWidget)
        self.registerAttributeWidget("kFile", attributewidgets.PathWidget)
        self.registerAttributeWidget("kDirectory", attributewidgets.PathWidget)
        self.registerAttributeWidget("kFloat", attributewidgets.NumericAttributeWidget)
        self.registerAttributeWidget("kInt", attributewidgets.NumericAttributeWidget)
        self.registerAttributeWidget("kBool", attributewidgets.BoolAttributeWidget)

    def registeredNodes(self):
        return self.types


class Graph(vortexApi.GraphModel):

    def __init__(self, application, name, graph):
        super(Graph, self).__init__(application, name)
        self._internalGraph = graph
        self.rootNode = None
        self.application.internalApp.events.nodeCreated.connect(self._onCreateNode, sender=self._internalGraph)
        self.application.internalApp.events.nodeDeleted.connect(self._onDeleteNode, sender=self._internalGraph)
        self.application.internalApp.events.connectionsCreated.connect(self._onConnectionCreated,
                                                                       sender=self._internalGraph)
        self.application.internalApp.events.connectionsDeleted.connect(self._onConnectionDeleted,
                                                                       sender=self._internalGraph)

    def _onCreateNode(self, _, node):
        if node is not None:
            parent = node.parent
            if self.rootNode and self.rootNode.internalNode != parent:
                parent = self.rootNode.findChild(parent.name)
            else:
                parent = self.rootNode
            newNodes = self.translateSlitherToVortex(node, parent=parent)
            self.sigNodesCreated.emit(newNodes)

    def _onDeleteNode(self, _, node):
        print("deleteNodeSig", node)

    def _onConnectionCreated(self, _, sourcePlug, destinationPlug):
        sourceNode = self.rootNode.findChild(sourcePlug.node.name)
        destinationNode = self.rootNode.findChild(destinationPlug.node.name)
        if sourceNode is not None and destinationNode is not None:
            sourceModel = sourceNode.attribute(sourcePlug.name())
            destinationModel = destinationNode.attribute(destinationPlug.name())
            if sourceModel is not None and destinationModel is not None:
                sourceModel.addConnection(sourceModel, destinationModel)
                self.sigConnectionCreated.emit(sourceModel, destinationModel)

    def _onConnectionDeleted(self, _, sourcePlug, destinationPlug):
        print("delete connection", sourcePlug, destinationPlug)

    def saveGraph(self, filePath=None):
        outputPath = self._internalGraph.saveToFile(filePath)
        if outputPath:
            self.application.sigGraphSaved.emit(outputPath)

    def loadFromPath(self, filePath, parent=None):
        self._internalGraph.loadFromFile(filePath)
        return self.translateSlitherToVortex(self._internalGraph.root, parent=parent or self.rootNode)

    def loadFromDict(self, data, parent=None):
        return self.createNodeFromInfo(data, parent=parent)

    def createNode(self, nodeType, parent=None):
        if parent:
            internalParent = parent.internalNode
        else:
            internalParent = None
        self._internalGraph.createNode(nodeType, nodeType, parent=internalParent)

    def translateSlitherToVortex(self, node, parent=None):
        model = NodeModel(node, self, self.config,
                          parent=parent
                          )
        nodes = [model]
        if not node.isCompound():
            return nodes

        for child in node.children:
            nodes.extend(self.translateSlitherToVortex(child, parent=model))
        return nodes

    def customToolbarActions(self, parent):
        action = parent.addAction("Execute")
        action.triggered.connect(self._execute)

    def _execute(self):
        # pprint.pprint(self._internalGraph.serialize())
        self._internalGraph.execute(self.rootNode.internalNode, self.application.internalApp.STANDARDEXECUTOR)


class NodeModel(vortexApi.ObjectModel):
    def __init__(self, internalNode, graph, config, parent=None):
        # link the internal NodeUI dict to the UI properties
        # data is stored json compatible
        super(NodeModel, self).__init__(graph, config, parent=parent)
        self.internalNode = internalNode  # type: api.ComputeNode
        if hasattr(self.internalNode, "attributes"):
            for attr in self.internalNode.attributes:
                model = TestModel(attr, self, properties={}, parent=None)
                self._attributes.append(model)
        internalNode.graph.application.events.nodeNameChanged.connect(self._onNodeNameChanged, sender=internalNode)
        internalNode.graph.application.events.nodeDirtyChanged.connect(self._onNodeDirtyChanged, sender=internalNode)
        internalNode.graph.application.events.attributeCreated.connect(self._onAttributeCreated, sender=internalNode)
        internalNode.graph.application.events.attributeDeleted.connect(self._onAttributeDeleted, sender=internalNode)

    def _onNodeNameChanged(self, sender, node, oldName, name):
        self.sigNodeNameChanged.emit(name)

    def _onNodeDirtyChanged(self, sender, node, state):
        self.setEdgeColour(QtGui.QColor(255, 0, 0) if state else QtGui.QColor(0.0, 0.0, 0.0, 255))

    def _onAttributeCreated(self, sender, node, attribute):
        parent = attribute.parent
        if parent is not None:
            parent = self.attribute(parent.name)
        attr = TestModel(attribute, self, properties={}, parent=parent)
        self._attributes.append(attr)
        self.sigAttributeCreated.emit(attr)

    def _onAttributeDeleted(self, sender, node, attribute):
        for index in range(self.attributes()):
            if self._attributes[index].internalAttr == attribute:
                del self._attributes[index]
                break

    def _attributeNameChanged(self, sender, attribute, oldName, name):
        for attrModel in self.attributes():
            if attrModel.internalAttr == attribute:
                self.sigAttributeNameChanged.emit(attrModel, name)

    def _attributeValueChanged(self, sender, attribute, value):
        self.sigAttributeValueChanged.emit(attribute, value)

    @property
    def properties(self):
        return self.internalNode.nodeUI

    @properties.setter
    def properties(self, properties):
        self.internalNode.nodeUI = properties

    def text(self):
        return self.internalNode.name

    def setText(self, text):
        self.internalNode.setName(str(text))

    def attributeWidget(self, parent):
        nodeWidget = pythonnode.BaseNodeWidget(self, parent=parent)

        return nodeWidget

    def graphicsWidget(self, parent):
        if self.image() != "":
            return NodeImage(self, parent=parent)

    def isCompound(self):
        return self.internalNode.isCompound()

    def canCreateAttributes(self):
        return self.isCompound() or self.internalNode.type() == "python"

    def createAttribute(self, attributeDefinition):
        attrDef = api.AttributeDefinition(name=attributeDefinition["label"],
                                          input=attributeDefinition.get("isInput", False),
                                          output=attributeDefinition.get("isOutput", False),
                                          type_=self.internalNode.graph.application.registry.dataTypeClass(
                                              attributeDefinition["type"]),
                                          default=attributeDefinition.get("default"),
                                          required=attributeDefinition.get("required", False),
                                          doc=attributeDefinition.get("description", ""),
                                          internal=attributeDefinition.get("internal", False),
                                          array=attributeDefinition.get("isArray", False),
                                          compound=attributeDefinition.get("isCompound", False))
        self.internalNode.createAttribute(attrDef)

    def deleteAttribute(self, attribute):
        pass

    def image(self):
        return ""

    def delete(self):
        super(NodeModel, self).delete()


class TestModel(vortexApi.AttributeModel):

    def __init__(self, internalAttr, objectModel, properties, parent=None):
        super(TestModel, self).__init__(objectModel, properties, parent)
        self.internalAttr = internalAttr  # type: api.Attribute
        self._connections = []

    def text(self):
        return self.internalAttr.name()

    def setText(self, text):
        self.internalAttr.setName(str(text))

    def isChild(self):
        return self.parent is not None and self.parent.isCompound()

    def isElement(self):
        return self.parent is not None and self.parent.isArray()

    def isInput(self):
        return self.internalAttr.isInput()

    def isOutput(self):
        return self.internalAttr.isOutput()

    def isCompound(self):
        return self.internalAttr.isCompound

    def isArray(self):
        return self.internalAttr.isArray

    def edgeColour(self):
        return self.backgroundColour().darker()

    def type(self):
        return self.internalAttr.type().Type

    def backgroundColour(self):
        typeMap = self.objectModel.config.attributeMapping.get(self.internalAttr.type().Type)
        if typeMap:
            return typeMap.get("colour", QtGui.QColor(0, 0, 0))
        return QtGui.QColor(0, 0, 0)

    def value(self):
        return self.internalAttr.value()

    def setValue(self, value):
        self.internalAttr.setValue(value)

    def elements(self):
        elements_ = []
        if not self.isArray():
            return elements_
        for element in self.internalAttr.elements:
            item = TestModel(element, objectModel=self.objectModel, properties={}, parent=self)
            elements_.append(item)
        return elements_

    def children(self):

        children = []
        if not self.isCompound():
            return children
        for child in self.internalAttr.children:
            item = TestModel(child, objectModel=self.objectModel, properties={}, parent=self)
            children.append(item)
        return children

    def isConnected(self):
        return self.internalAttr.isConnected()

    def canAcceptConnection(self, plug):
        return self.internalAttr.canConnect(self.internalAttr, plug.internalAttr)

    def connections(self):
        connections = []
        for upstream in self.internalAttr.upstream():
            selfNode = self.objectModel
            node = None
            if upstream.isInput():  # dealing with the parent compound node
                node = self.objectModel.parentObject()
                model = None
            elif self.isOutput():
                model = selfNode
            else:
                model = self.objectModel.parentObject()
            if model:
                node = model.findChild(upstream.node.name, recursive=False)
            if not node:
                print("Unable to find node: {} -> {}".format(self.text(), upstream.node.name))
                continue
            connections.append((node.attribute(upstream.name()), self))
        return connections

    def toolTip(self):
        return self.properties.get("description")

    def addConnection(self, source, destination):
        self._connections.append((source, destination))

    def createConnection(self, attribute):
        if self.isInput():
            self.internalAttr.connect(attribute.internalAttr)
            self.addConnection(attribute, self)
        else:
            attribute.internalAttr.connect(self.internalAttr)
            self.addConnection(self, attribute)
        return True

    def deleteConnection(self, attribute):
        if self.isInput() and self.internalAttr.isConnectedTo(attribute.internalAttr):
            if self.internalAttr.disconnect():
                logger.debug("Removed Connection: {}".format(attribute))
                try:
                    self._connections.remove((attribute, self))
                except ValueError:
                    print("not on UI attribute ...connections")
                return True
        elif attribute.isInput() and attribute.internalAttr.isConnectedTo(self.internalAttr):
            return attribute.deleteConnection(self)
        return False


class NodeImage(QtWidgets.QGraphicsWidget):
    def __init__(self, model, parent=None):
        super(NodeImage, self).__init__(parent=parent)
        self.objectModel = model
        image = QtGui.QImage()
        image.load(model.image())
        self.image = image.scaledToWidth(model.width() - (model.edgeThickness() * 2))

    def paint(self, painter, option, widget):
        painter.drawImage(QtCore.QPoint(self.objectModel.edgeThickness(), 0), self.image)
        super(NodeImage, self).paint(painter, option, widget)

    def boundingRect(self):
        return self.image.rect()

    def geometry(self):
        return self.boundingRect()


def load():
    return vortexApi.standalone(Application,
                                Graph,
                                Config)


if __name__ == "__main__":
    load()
