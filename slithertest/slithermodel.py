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
import os

from zoo.core import api

cfg = api.zooFromPath(os.environ["ZOOTOOLS_ROOT"])
cfg.resolver.resolveFromPath(cfg.resolver.environmentPath())
from vortex import startup

startup.initialize()

from Qt import QtGui, QtWidgets, QtCore
from zoo.libs.pyqt.widgets import frame, elements
from vortex import api as vortexApi
from vortex.ui import attributewidgets
from slither import api
from zoo.libs.utils import zlogging

logger = zlogging.getLogger(__name__)


class Application(vortexApi.UIApplication):

    def __init__(self, uiConfig):
        super(Application, self).__init__(uiConfig)
        self.internalApp = api.Application()
        for nType, obj in self.internalApp.registry.nodes.items():
            uiConfig.types[nType] = obj["info"]["category"]


class Config(vortexApi.VortexConfig):

    def __init__(self):
        super(Config, self).__init__()

        self.types = {}
        self.attributeMapping = {
            'kQuaternion': {"colour": QtGui.QColor(230, 115, 115)},
            'kColour': {"colour": QtGui.QColor(130, 217, 159)},
            'kMatrix4': {"color": QtGui.QColor(230, 115, 115)},
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

    def registeredNodes(self):
        return self.types


class Graph(vortexApi.GraphModel):

    def __init__(self, application, name):
        super(Graph, self).__init__(application, name)
        self._internalGraph = application.internalApp.createGraph(name)
        self.rootNode = NodeModel(self._internalGraph.root, self.config,
                                  properties={},
                                  parent=None
                                  )

    def saveGraph(self, filePath=None):
        outputPath = self._internalGraph.saveToFile(filePath)
        if outputPath:
            self.application.events.modelGraphSaved.emit(outputPath)

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
        n = self._internalGraph.createNode(nodeType, nodeType, parent=internalParent)
        if n is not None:
            nodes = self.translateSlitherToVortex(n, parent=parent or self.rootNode)
            self.application.events.modelNodesCreated.emit(nodes)

    def translateSlitherToVortex(self, node, parent=None):
        model = NodeModel(node, self.config,
                          properties={},
                          parent=parent
                          )
        nodes = [model]
        if not node.isCompound():
            return nodes

        for child in node.children:
            nodes.extend(self.translateSlitherToVortex(child, parent=model ))
        return nodes

    def customToolbarActions(self, parent):
        action = parent.addAction("Execute")
        action.triggered.connect(self._execute)

    def _execute(self):
        selection = []
        for child in self.rootNode.children(recursive=True):
            if child.isSelected():
                selection.append(child)
                child.setBackgroundColour(QtGui.QColor(255, 0, 0, 1))


class NodeModel(vortexApi.ObjectModel):
    def __init__(self, internalNode, config, properties=None, parent=None):
        # link the internal NodeUI dict to the UI properties
        # data is stored json compatible
        properties = internalNode.nodeUI
        super(NodeModel, self).__init__(config, properties=properties or {}, parent=parent)
        self.internalNode = internalNode  # type: api.ComputeNode
        for attr in self.internalNode.attributes:
            model = TestModel(attr, self, properties={}, parent=None)
            self._attributes.append(model)

    def text(self):
        return self.internalNode.name

    def attributeWidget(self, parent):
        parentFrame = frame.QFrame(parent=parent)
        layout = elements.vBoxLayout(parentFrame)
        for model in self.attributes(outputs=False):
            wid = self.config.attributeWidgetForType(model.type())
            if wid is not None:
                layout.addWidget(wid(model, parent=parentFrame))
        return parentFrame

    def isCompound(self):
        return self.internalNode.isCompound()


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
        return self.internalAttr.parent.isCompound

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
            return typeMap["colour"]
        return QtGui.QColor(0, 0, 0)

    def value(self):
        return self.internalAttr.value()

    def setValue(self, value):
        self.internalAttr.setValue(value)

    def elements(self):
        elements_ = []
        for element in self.internalAttr.elements:
            item = TestModel(element, objectModel=self.objectModel, properties={}, parent=self)
            elements_.append(item)
        return elements_

    def children(self):

        children = []
        for child in self.internalAttr.children:
            item = TestModel(child, objectModel=self.objectModel, properties={}, parent=self)
            children.append(item)
        return children

    def isConnected(self):
        return self.internalAttr.isConnected()

    def canAcceptConnection(self, plug):
        return self.internalAttr.canConnect(plug.internalAttr)

    def connections(self):
        upstream = self.internalAttr.upstream
        if not upstream:
            return []
        if self.objectModel.isCompound():
            model = self.objectModel
        else:
            model = self.objectModel.parentObject()
        node = model.findChild(upstream.node.name, recursive=False)
        if not node:
            print("unable to find node: {} -> {}".format(self.text(), upstream.node.name))
            return []
        return [(node.attribute(upstream.name()), self)]

    def toolTip(self):
        return self.properties.get("description")

    def createConnection(self, attribute):
        if self.isInput():
            self.internalAttr.connect(attribute.internalAttr)
            self._connections.append((attribute, self))
        else:
            attribute.internalAttr.connect(self.internalAttr)
            self._connections.append((self, attribute))
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


def load():
    return vortexApi.standalone(Application,
                                Graph,
                                Config)
    # filePath=r"C:\Users\dave\Desktop\test.slgraph")


if __name__ == "__main__":
    load()
