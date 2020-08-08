from zoo.libs.pyqt.widgets.graphics import graphicitems
from zoo.libs.pyqt.widgets import elements
from vortex.ui.graphics import plugwidget
from vortex.ui.graphics.graphnodes import basenode

from Qt import QtWidgets, QtCore, QtGui



class GraphicsNode(basenode.QBaseNode):

    def __init__(self, objectModel, parent=None):
        super(GraphicsNode, self).__init__(objectModel, parent=parent)

        self.cornerRounding = self.model.cornerRounding()
        self.header = basenode.NodeHeader(self,
                                 self.model.text(),
                                 self.model.secondaryText(),
                                 icon=self.model.icon(),
                                 parent=self)
        self.attributeContainer = graphicitems.ItemContainer(parent=self)
        self.init()

    def init(self):
        super(GraphicsNode, self).init()
        layout = elements.vGraphicsLinearLayout(parent=self)

        self.header.headerTextChanged.connect(self.onHeaderTextChanged)
        self.header.headerButtonStateChanged.connect(self.onHeaderButtonStateChanged)
        self.header.headerButton.hide()

        layout.addItem(self.header)
        layout.addItem(self.attributeContainer)
        # now bind the attributes from the model if it has any
        for attr in self.model.attributes(inputs=True, outputs=True, attributeVisLevel=self.ATTRIBUTE_VIS_LEVEL_ONE):
            self.addAttribute(attr)
        self._connections()

    def _connections(self):
        # bind the objectModel signals to this qNode
        self.model.sigAddAttribute.connect(self.addAttribute)
        # self.model.attributeNameChangedSig.connect(self.setAttributeName)
        self.model.sigNodeNameChanged.connect(self.header.setText)
        self.model.sigRemoveAttribute.connect(self.removeAttribute)
        self.model.sigSelectionChanged.connect(self.setSelected)

    def onHeaderTextChanged(self, text):
        self.model.setText(text)

    def onHeaderButtonStateChanged(self, state):
        pass
        # self.attributeContainer.clear()
        # for attr in self.model.attributes(inputs=True, outputs=True, attributeVisLevel=state):
        #     self.addAttribute(attr)

    def setAttributeName(self, attribute, name):
        attr = self.attributeItem(attribute)
        if attr:
            attr.setText(name)

    def addAttribute(self, attribute):
        container = plugwidget.PlugContainer(attribute, parent=self.attributeContainer)
        if attribute.isInput():
            index = container.layout().count() - 2
        else:
            index = 2
        container.layout().insertStretch(index, 1)
        self.attributeContainer.addItem(container)

    def removeAttribute(self, attribute):
        for index, item in enumerate(self.attributeContainer.items()):
            if item.objectModel == attribute:
                self.attributeContainer.removeItemAtIndex(index)
                return True
        return False

    def attributeItem(self, attributeModel):
        for attr in iter(self.attributeContainer.items()):
            if attr.model == attributeModel:
                return attr

    def boundingRect(self, *args, **kwargs):
        childBoundingRect = self.childrenBoundingRect(*args, **kwargs)
        self.model.setHeight(childBoundingRect.height())
        return QtCore.QRectF(0, 0,
                             (childBoundingRect.width() - plugwidget.Plug._diameter * 2) + 1,
                             childBoundingRect.height())

    def paint(self, painter, option, widget):
        # main rounded rect
        rect = self.boundingRect()
        thickness = self.model.edgeThickness()
        backgroundColour = self.model.backgroundColour()

        titleHeight = self.header.size().height()
        rounding = self.cornerRounding
        nodeWidth = int(rect.width())
        nodeHeight = int(rect.height())
        headerRect = QtCore.QRectF(rect.x(), rect.y(), nodeWidth, titleHeight)
        bodyRect = QtCore.QRectF(rect.x(), rect.y(), nodeWidth, nodeHeight)

        # body rectangle
        roundedPath = QtGui.QPainterPath()

        roundedPath.addRoundedRect(bodyRect,
                                   rounding, rounding)

        linearGradient = QtGui.QLinearGradient(rect.x(), rect.y(), rect.width() * 0.75, 100)
        linearGradient.setSpread(QtGui.QLinearGradient.RepeatSpread)
        linearGradient.setFinalStop(QtCore.QPoint(25, 50))
        linearGradient.setStops([(0.0, backgroundColour),
                                 (0.001, backgroundColour.lighter(110)),
                                 (0.25, backgroundColour.lighter(110)),
                                 (0.2501, backgroundColour),
                                 (0.5, backgroundColour),
                                 (0.501, backgroundColour.lighter(110)),
                                 (0.75, backgroundColour.lighter(110)),
                                 (0.7501, backgroundColour),
                                 (1.0, backgroundColour),
                                 ])

        painter.setBrush(QtGui.QBrush(linearGradient))
        painter.fillPath(roundedPath, painter.brush())

        # header rectangle
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(self.model.headerColour())

        painter.drawRoundedRect(headerRect,
                                rounding, rounding)
        painter.drawRect(0, rounding, nodeWidth, titleHeight - rounding)

        # outline
        if self.isSelected():
            standardPen = QtGui.QPen(self.model.selectedNodeColour(), thickness + 1)
        else:
            standardPen = QtGui.QPen(self.model.edgeColour(), thickness)
        # # outer node edge
        painter.strokePath(roundedPath,
                           standardPen)

        super(GraphicsNode, self).paint(painter, option, widget)