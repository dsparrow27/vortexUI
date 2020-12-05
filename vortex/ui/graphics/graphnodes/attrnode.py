import os

from zoo.libs.pyqt.widgets.graphics import graphicitems
from zoo.libs.pyqt.widgets import elements
from vortex.ui.graphics import plugwidget
from vortex.ui.graphics.graphnodes import basenode

from Qt import QtWidgets, QtCore, QtGui


class Container(graphicitems.ItemContainer):

    def __init__(self, orientation=QtCore.Qt.Vertical, parent=None):
        super(Container, self).__init__(orientation, parent)

    if os.environ.get("DEBUG", "0") == "1":
        def paint(self, painter, option, widget):
            painter.setPen(QtGui.QPen(QtCore.Qt.cyan, 0.75))
            painter.drawRect(self.geometry())
            super(Container, self).paint(painter, option, widget)


class GraphicsNode(basenode.QBaseNode):

    def __init__(self, objectModel, parent=None):
        super(GraphicsNode, self).__init__(objectModel, parent=parent)

        self.cornerRounding = self.model.cornerRounding()
        self.header = basenode.NodeHeader(self.model,
                                          parent=self)
        self.attributeContainer = Container(parent=self)
        self.attributeContainer.setPos(self.header.y(), 0)
        self.layout = None
        self.customWidget = None
        self.init()

    def init(self):
        super(GraphicsNode, self).init()
        self.layout = elements.vGraphicsLinearLayout(parent=self)

        self.header.headerTextChanged.connect(self.onHeaderTextChanged)
        self.header.headerButton.hide()

        self.layout.addItem(self.header)
        self.layout.addItem(self.attributeContainer)
        self.createModelCustomWidget()
        # now bind the attributes from the model if it has any
        visited = set()
        for attr in self.model.attributes(inputs=False, outputs=True, attributeVisLevel=self.ATTRIBUTE_VIS_LEVEL_ONE):
            name = attr.text()
            if name in visited:
                continue
            visited.add(name)
            self.addAttribute(attr)
        for attr in self.model.attributes(inputs=True, outputs=False, attributeVisLevel=self.ATTRIBUTE_VIS_LEVEL_ONE):
            name = attr.text()
            if name in visited:
                continue
            visited.add(name)
            self.addAttribute(attr)
        self._connections()

    def createModelCustomWidget(self):
        customWidget = self.model.graphicsWidget(parent=self)
        if customWidget is None:
            return
        self.customWidget = customWidget
        layout = self.layout
        layout.addItem(customWidget)

    def _connections(self):
        # bind the objectModel signals to this qNode
        self.model.sigAddAttribute.connect(self.addAttribute)
        self.model.sigAttributeNameChanged.connect(self.setAttributeName)
        self.model.sigNodeNameChanged.connect(self.header.setText)
        self.model.sigRemoveAttribute.connect(self.removeAttribute)
        self.model.sigSelectionChanged.connect(self.setSelected)

    def onHeaderTextChanged(self, text):
        self.model.setText(text)

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
        self.updateSizeFromAttributes()
        container.expandedSig.connect(self.updateSizeFromAttributes)

    def updateSizeFromAttributes(self):
        height = 0
        layout = self.layout
        for index in range(layout.count()):
            child = layout.itemAt(index)
            rect = child.boundingRect()
            height += rect.height()
        for child in self.attributeContainer.items():
            rect = child.boundingRect()
            height += rect.height()
        self.prepareGeometryChange()
        self.model.setHeight(height)

    def removeAttribute(self, attribute):
        for index, item in enumerate(self.attributeContainer.items()):
            if item.objectModel == attribute:
                self.attributeContainer.removeItemAtIndex(index)
                self.updateSizeFromAttributes()
                return True
        return False

    def attributeItem(self, attributeModel):
        for attr in iter(self.attributeContainer.items()):
            if attr.model == attributeModel:
                return attr

    if os.environ.get("DEBUG", "0") == "1":
        def paint(self, painter, option, widget):
            painter.setBrush(QtCore.Qt.NoBrush)
            painter.setPen(QtGui.QPen(QtCore.Qt.green, 0.75))
            painter.drawRect(self.geometry())
            super(GraphicsNode, self).paint(painter, option, widget)
    else:
        def paint(self, painter, option, widget):
            # main rounded rect
            rect = self.boundingRect()
            thickness = self.model.edgeThickness()
            backgroundColour = self.model.backgroundColour()
            self.header.setTextColour(self.model.textColour())
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
