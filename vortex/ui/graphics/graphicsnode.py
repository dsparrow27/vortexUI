import PySide2

from zoo.libs.pyqt.widgets.graphics import graphicitems
from zoo.libs.pyqt.widgets import elements
from vortex.ui.graphics import plugwidget
from Qt import QtWidgets, QtCore, QtGui

from PySide2 import QtWidgets, QtGui, QtCore

ATTRIBUTE_VIS_LEVEL_ZERO = 0
ATTRIBUTE_VIS_LEVEL_ONE = 1
ATTRIBUTE_VIS_LEVEL_TWO = 2


class NodeHeaderButton(QtWidgets.QGraphicsWidget):
    stateChanged = QtCore.Signal(int)

    def __init__(self, size, colour, *args, **kwargs):
        super(NodeHeaderButton, self).__init__(*args, **kwargs)
        self.setWindowFrameMargins(0, 0, 0, 0)
        self.colour = colour
        self._size = size
        self.setMinimumHeight(size)
        self.setMaximumHeight(size)
        self.setMinimumWidth(size)
        self.setMaximumWidth(size)
        self.state = 0
        self._defaultPen = QtGui.QPen(QtGui.QColor(0.0, 0.0, 0.0))

    def boundingRect(self, *args, **kwargs):
        return QtCore.QRectF(0, 0, self._size, self._size)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            if self.state >= ATTRIBUTE_VIS_LEVEL_TWO:
                self.state = ATTRIBUTE_VIS_LEVEL_ZERO
            elif self.state <= ATTRIBUTE_VIS_LEVEL_ZERO:
                self.state += ATTRIBUTE_VIS_LEVEL_ONE
            else:
                self.state += ATTRIBUTE_VIS_LEVEL_ONE
            self.stateChanged.emit(self.state)
            self.update()

    def paint(self, painter, option, widget):
        painter.setPen(self._defaultPen)
        avg = self._size / 3.0
        mid = self._size / 2.0
        if self.state == ATTRIBUTE_VIS_LEVEL_ZERO:
            self._solidRect(painter, 0, 0, self._size, avg)
            self._stroke(painter, 0, mid, self._size, avg)
            self._stroke(painter, 0, self._size, self._size, avg)
        elif self.state == ATTRIBUTE_VIS_LEVEL_ONE:
            self._solidRect(painter, 0, 0, self._size, avg)
            self._solidRect(painter, 0, mid, self._size, avg)
            self._stroke(painter, 0, self._size, self._size, avg)
        elif self.state == ATTRIBUTE_VIS_LEVEL_TWO:
            self._solidRect(painter, 0, 0, self._size, avg)
            self._solidRect(painter, 0, mid, self._size, avg)
            self._solidRect(painter, 0, self._size, self._size, avg)
        super(NodeHeaderButton, self).paint(painter, option, widget)

    def _solidRect(self, painter, x, y, width, height):
        rect = QtCore.QRect(x, y, width, height)
        painter.setBrush(self.colour)
        painter.drawRect(rect)

    def _stroke(self, painter, x, y, width, height):
        rect = QtCore.QRect(x, y, width, height)
        painter.setPen(self._defaultPen)
        painter.setBrush(QtGui.QBrush(QtGui.QColor(0.0, 0.0, 0.0, 0.0)))
        painter.drawRect(rect)


class HeaderPixmap(QtWidgets.QGraphicsWidget):
    def __init__(self, pixmap, parent):
        super(HeaderPixmap, self).__init__(parent)
        self.setWindowFrameMargins(0, 0, 0, 0)
        self.pixmap = QtGui.QPixmap()
        if pixmap:
            self.setPixmap(pixmap.pixmap(32, 32))

        self.pixItem = QtWidgets.QGraphicsPixmapItem(parent=self)

    def setPixmap(self, path):
        self.pixmap = QtGui.QPixmap(path)
        self.pixItem = QtWidgets.QGraphicsPixmapItem(self.pixmap, self)


class NodeHeader(graphicitems.ItemContainer):
    headerButtonStateChanged = QtCore.Signal(int)
    headerTextChanged = QtCore.Signal(str)

    def __init__(self, node, text, secondaryText="", icon=None, parent=None):
        self._node = node
        super(NodeHeader, self).__init__(orientation=QtCore.Qt.Horizontal, parent=parent)
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding)
        self.setWindowFrameMargins(0, 0, 0, 0)
        self.setAcceptedMouseButtons(QtCore.Qt.NoButton)
        self.titleFont = QtGui.QFont("Roboto-Bold", 8)
        fontmetrics = QtGui.QFontMetrics(self.titleFont)
        height = fontmetrics.height() * 2
        self.setMinimumHeight(height)
        self.setMaximumHeight(height)

        self._createLabels(text)
        headerButton = NodeHeaderButton(size=12, colour=node.model.headerButtonColour(), parent=self)
        headerButton.stateChanged.connect(self.headerButtonStateChanged.emit)
        self.addItem(headerButton, QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

    def _createLabels(self, primary):
        self._titleWidget = graphicitems.GraphicsText(primary, parent=self)
        self._titleWidget.textChanged.connect(self.headerTextChanged)
        self._titleWidget.font = self.titleFont
        self.addItem(self._titleWidget, QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)

    def setText(self, text):
        self._titleWidget.blockSignals(True)
        self._titleWidget.text = text
        self._titleWidget.blockSignals(False)


class QBaseNode(QtWidgets.QGraphicsWidget):
    def __init__(self, objectModel, parent=None):
        super(QBaseNode, self).__init__(parent=parent)
        self.model = objectModel
        self.setZValue(1)

        self.setFlags(self.ItemIsSelectable | self.ItemIsMovable)
        self.setWindowFrameMargins(0, 0, 0, 0)
        self.setMinimumSize(objectModel.minimumWidth(), objectModel.minimumHeight())
        self.setPreferredSize(objectModel.minimumWidth(), objectModel.minimumHeight())
        self.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))
        self.setToolTip(self.model.toolTip())

        self._resizerRect = QtCore.QRectF()
        self._resizerSelected = False

    def init(self):
        rect = self.boundingRect()
        resizerSize = self.model.resizerSize()
        self._resizerRect = QtCore.QRectF(rect.right() - resizerSize, rect.bottom() - resizerSize, resizerSize,
                                          resizerSize)
        self._resizerSelected = False
        self.setPos(QtCore.QPoint(*self.model.position()))

    def mousePressEvent(self, event):

        if self._resizerRect.contains(event.pos()):
            self._resizerSelected = True
            return
        self.model.setSelected(True)
        super(QBaseNode, self).mousePressEvent(event)

    def setSelected(self, selected):
        self.model.setSelected(True)
        super(QBaseNode, self).setSelected(selected)

    def mouseMoveEvent(self, event):
        scene = self.scene()
        if self._resizerSelected:
            pos = event.pos()
            self.resize(QtCore.QSizeF(pos.x(), pos.y()))
            self.scene().updateAllConnections()
            return
        items = scene.selectedNodes()

        for i in items:
            pos = i.pos() + i.mapToParent(event.pos()) - i.mapToParent(event.lastPos())
            i.setPos(pos)
            i.model.setPosition((pos.x(), pos.y()))

        self.scene().updateAllConnections()

    def mouseReleaseEvent(self, event):
        self._resizerSelected = False

        super(QBaseNode, self).mouseReleaseEvent(event)

    def _drawResizer(self, painter, option, widget, rect):
        if self.model.isSelected():
            colour = self.model.selectedNodeColour()
        else:
            colour = self.model.backgroundColour()
            colour = colour.lighter(150)

        path = QtGui.QPainterPath()
        resizerSize = self.model.resizerSize()
        rect = QtCore.QRectF(rect.right() - resizerSize, rect.bottom() - resizerSize, resizerSize,
                             resizerSize)
        self._resizerRect = rect
        path.moveTo(rect.topRight())
        path.lineTo(rect.bottomRight())
        path.lineTo(rect.bottomLeft())
        painter.setBrush(colour)
        painter.setPen(QtCore.Qt.NoPen)
        painter.fillPath(path, painter.brush())


class Pin(QBaseNode):
    def __init__(self, objectModel, parent=None):
        super(Pin, self).__init__(objectModel, parent)
        self.init()

    def boundingRect(self):
        return QtCore.QRect(0, 0, 15, 15)

    def paint(self, painter, option, widget):
        rect = self.boundingRect()

        thickness = self.model.edgeThickness()
        if self.isSelected():
            standardPen = QtGui.QPen(self.model.selectedNodeColour(), thickness + 1)
        else:
            standardPen = QtGui.QPen(self.model.edgeColour(), thickness)
        painter.setBrush(self.model.backgroundColour().lighter(150))
        painter.setPen(standardPen)
        painter.drawEllipse(rect)

        super(Pin, self).paint(painter, option, widget)


class Comment(QBaseNode):

    def __init__(self, objectModel, parent=None):
        super(Comment, self).__init__(objectModel, parent)
        self.backgroundColour = QtGui.QBrush(self.model.backgroundColour())
        self.cornerRounding = self.model.cornerRounding()
        self.init()

    def init(self):
        layout = elements.vGraphicsLinearLayout(parent=self)
        # layout.set
        self.header = NodeHeader(self,
                                 self.model.text(),
                                 self.model.secondaryText(),
                                 icon=self.model.icon(),
                                 parent=self)
        # self.header.headerTextChanged.connect(self.onHeaderTextChanged)
        # self.header.headerButtonStateChanged.connect(self.onHeaderButtonStateChanged)

        layout.addItem(self.header)

        self.setLayout(layout)
        super(Comment, self).init()

    def paint(self, painter, option, widget):
        # main rounded rect
        rect = self.boundingRect()
        thickness = self.model.edgeThickness()
        backgroundColour = self.model.backgroundColour()

        titleHeight = 25
        rounding = self.cornerRounding
        nodeWidth = int(rect.width())
        nodeHeight = int(rect.height())
        headerRect = QtCore.QRectF(rect.x(), rect.y(), nodeWidth, titleHeight)
        bodyRect = QtCore.QRectF(rect.x(), rect.y(), nodeWidth, nodeHeight)

        # body rectangle
        roundedPath = QtGui.QPainterPath()

        roundedPath.addRoundedRect(bodyRect,
                                   rounding, rounding)

        painter.setBrush(QtGui.QBrush(backgroundColour))
        painter.fillPath(roundedPath, painter.brush())

        # header rectangle
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(self.model.headerColour())

        painter.drawRoundedRect(headerRect,
                                rounding, rounding)
        painter.drawRect(0, rounding, nodeWidth, titleHeight - rounding)
        # resizer
        self._drawResizer(painter, option, widget, bodyRect)

        # outline
        if self.isSelected():
            standardPen = QtGui.QPen(self.model.selectedNodeColour(), thickness + 1)
        else:
            standardPen = QtGui.QPen(self.model.edgeColour(), thickness)
        # # outer node edge
        painter.strokePath(roundedPath,
                           standardPen)

        super(Comment, self).paint(painter, option, widget)


class Backdrop(Comment):

    def __init__(self, objectModel, parent=None):
        super(Backdrop, self).__init__(objectModel, parent)


class GraphicsNode(QBaseNode):

    def __init__(self, objectModel, parent=None):
        super(GraphicsNode, self).__init__(objectModel, parent=parent)

        self.cornerRounding = self.model.cornerRounding()
        self.header = NodeHeader(self,
                                 self.model.text(),
                                 self.model.secondaryText(),
                                 icon=self.model.icon(),
                                 parent=self)
        self.attributeContainer = graphicitems.ItemContainer(parent=self)
        self.init()

    def init(self):
        layout = elements.vGraphicsLinearLayout(parent=self)

        self.header.headerTextChanged.connect(self.onHeaderTextChanged)
        self.header.headerButtonStateChanged.connect(self.onHeaderButtonStateChanged)
        layout.addItem(self.header)
        layout.addItem(self.attributeContainer)

        # self.setLayout(layout)
        # now bind the attributes from the model if it has any
        for attr in self.model.attributes(inputs=True, outputs=True, attributeVisLevel=ATTRIBUTE_VIS_LEVEL_ONE):
            self.addAttribute(attr)
        self._connections()
        super(GraphicsNode, self).init()

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
        self.attributeContainer.clear()
        for attr in self.model.attributes(inputs=True, outputs=True, attributeVisLevel=state):
            self.addAttribute(attr)

    def setAttributeName(self, attribute, name):
        attr = self.attributeItem(attribute)
        if attr:
            attr.setText(name)

    def addAttribute(self, attribute):
        container = plugwidget.PlugContainer(attribute, parent=self.attributeContainer)
        if attribute.isInput():
            index = container.layout().count() - 2

            if attribute.isArray() or attribute.isCompound():
                container.inCrossItem.show()
        else:
            if attribute.isArray() or attribute.isCompound():
                container.outCrossItem.show()
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
