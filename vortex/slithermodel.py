from slither import api
from qt import QtGui
from vortex.ui.graphics import graphicsdatamodel
from vortex.ui import application

print api
ATTRIBUTETYPEMAP = {'Quaternion': QtGui.QColor(126.999945, 24.999944999999997, 24.999944999999997),
                    'color': QtGui.QColor(22.999980000000015, 255, 255),
                    'matrix4': QtGui.QColor(174.99987000000002, 130.00001999999998, 114.99990000000001),
                    'multi': QtGui.QColor(255, 255, 255),
                    'vector2D': QtGui.QColor(147.000105, 102.0, 156.000075),
                    'vector3D': QtGui.QColor(184.99994999999998, 126.999945, 184.99994999999998),
                    bool: QtGui.QColor(38.00010000000001, 73.99998000000001, 114.000045),
                    dict: QtGui.QColor(204.0, 127.5, 163.20000000000002),
                    float: QtGui.QColor(133.000095, 102.0, 147.99996000000002),
                    int: QtGui.QColor(133.000095, 102.0, 147.99996000000002),
                    list: QtGui.QColor(56.000040000000006, 47.99992500000001, 45.00010500000001),
                    str: QtGui.QColor(244.9999965, 214.999935, 59.99997)
                    }
NODECOLORMAP = {}


class Application(application.UIApplication):
    def __init__(self, uiConfig):
        app = api.initialize()
        super(Application, self).__init__(uiConfig, app)
        self.currentModel = SlitherUIObject(app.root, self.config)

    def initialize(self):
        self.onNewNodeRequested.emit({"model": self.currentModel,
                                      "newTab": True})
        self._apiApplication.events.nodeCreated.connect(self.uiNodeForCore)

    def uiNodeForCore(self, node):
        """Called by the core api to added node to current model

        :param node:
        :type node:
        :return:
        :rtype:
        """

        self.onNewNodeRequested.emit({"model": SlitherUIObject(node, self.config, parent=self.currentModel),
                                      "newTab": node.isCompound()})

    def onNodeCreated(self, Type):
        name = Type
        self._apiApplication.createNode(name, Type, parent=self.currentModel.slitherNode)

    def registeredNodes(self):
        return self._apiApplication.nodeRegistry.nodes.keys()


class SlitherUIObject(graphicsdatamodel.ObjectModel):

    def __init__(self, slitherNode, config, parent=None):
        super(SlitherUIObject, self).__init__(config, parent)
        self.slitherNode = slitherNode

        if self.isCompound():

            self._children = map(SlitherUIObject, slitherNode.children)
        else:
            self._children = []

    def isCompound(self):
        return self.slitherNode.isCompound()

    def children(self):
        return self._children

    def __hash__(self):
        return id(self)

    def text(self):
        return self.slitherNode.name

    def attributes(self, inputs=True, outputs=True):
        attrs = []
        if inputs:
            attrs.extend([AttributeModel(i, self) for i in self.slitherNode.inputs()])
        if outputs:
            attrs.extend([AttributeModel(i, self) for i in self.slitherNode.outputs()])
        return attrs

    def createAttribute(self, **kwargs):
        pass

    def deleteAttribute(self, attribute):
        pass

    def deleteChild(self, child):

        if self.isCompound():
            result = self.slitherNode.removeChild(child.slitherNode)
            if result:
                self._children.remove(child)
                return True
        return False

    def delete(self):
        parent = self.parentObject()
        # print parent, self.text()
        if parent is not None:
            return parent.deleteChild(self)
        return False


class AttributeModel(graphicsdatamodel.AttributeModel):
    def __init__(self, slitherAttribute, objectModel):
        super(AttributeModel, self).__init__(objectModel)
        self.internalAttr = slitherAttribute

    def text(self):
        return self.internalAttr.name()

    def setText(self, text):
        self.internalAttr.setName(str(text))

    def canAcceptConnection(self, plug):
        return self.internalAttr.canConnect(plug.internalAttr)

    def createConnection(self, attribute):
        if self.internalAttr.isInput():
            self.internalAttr.connectUpstream(attribute.internalAttr)
        else:
            attribute.internalAttr.connectUpstream(self.internalAttr)
        return True

    def deleteConnection(self, attribute):
        if self.internalAttr.isConnectedTo(attribute.internalAttr):
            if self.internalAttr.isInput():
                self.internalAttr.disconnect()
            else:
                attribute.internalAttr.disconnect()
            return True
        return False

    def toolTip(self):
        return self.internalAttr.definition.documentation()

    def isInput(self):
        return self.internalAttr.isInput()

    def isOutput(self):
        return self.internalAttr.isOutput()

    def itemColour(self):
        Map = ATTRIBUTETYPEMAP.get(self.internalAttr.type().Type)
        if Map:
            return Map
        return super(AttributeModel, self).itemColour()
