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

    def __init__(self, size, color, *args, **kwargs):
        super(NodeHeaderButton, self).__init__(*args, **kwargs)
        self.setWindowFrameMargins(0, 0, 0, 0)
        self.color = color
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
        painter.setBrush(self.color)
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


class NodeHeader(QtWidgets.QGraphicsWidget):
    headerButtonStateChanged = QtCore.Signal(int)
    headerTextChanged = QtCore.Signal(str)

    def __init__(self, node, text, secondaryText="", icon=None, parent=None):
        super(NodeHeader, self).__init__(parent)
        self.setWindowFrameMargins(0, 0, 0, 0)
        self.setAcceptedMouseButtons(QtCore.Qt.NoButton)
        self.titleFont = QtGui.QFont("Roboto-Bold.ttf", 8)
        self._node = node
        fontmetrics = QtGui.QFontMetrics(self.titleFont)
        height = fontmetrics.height() * 2
        self.setMaximumHeight(height)
        self.setMinimumHeight(height)
        layout = elements.hGraphicsLinearLayout(parent=self)
        self.headerIcon = HeaderPixmap(pixmap=icon or "", parent=self)
        layout.addItem(self.headerIcon)
        if not icon:
            self.headerIcon.hide()
        self._createLabels(text, secondaryText, layout)
        layout.addStretch(1)
        headerButton = NodeHeaderButton(size=12, color=node.model.headerButtonColor(), parent=self)
        headerButton.stateChanged.connect(self.headerButtonStateChanged.emit)
        layout.addItem(headerButton)
        layout.setAlignment(headerButton, QtCore.Qt.AlignCenter)
        layout.setAlignment(self.titleContainer, QtCore.Qt.AlignCenter)

    def setIcon(self, path):
        self.headerIcon.setPixmap(path)

    def _createLabels(self, primary, secondary, parentLayout):
        self.titleContainer = graphicitems.ItemContainer(QtCore.Qt.Vertical, parent=self)
        self._titleWidget = graphicitems.GraphicsText(primary, parent=self)
        self._titleWidget.textChanged.connect(self.headerTextChanged)
        self._titleWidget.font = self.titleFont
        self._secondarytitle = graphicitems.GraphicsText(secondary, parent=self)
        self._secondarytitle.setTextFlags(QtWidgets.QGraphicsItem.ItemIsSelectable)
        self._secondarytitle.font = QtGui.QFont("Roboto-Bold.ttf", 8)
        self.titleContainer.addItem(self._titleWidget, QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
        self.titleContainer.addItem(self._secondarytitle, QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
        self._secondarytitle.hide()
        parentLayout.addItem(self.titleContainer)

    def setText(self, text):
        self._titleWidget.setText(text)


class QBaseNode(QtWidgets.QGraphicsWidget):
    def __init__(self, objectModel, parent=None):
        super(QBaseNode, self).__init__(parent=parent)
        self.model = objectModel
        self.setZValue(1)
        self.setPos(QtCore.QPoint(*objectModel.position()))
        self.setFlags(self.ItemIsSelectable | self.ItemIsMovable)
        self.setWindowFrameMargins(0, 0, 0, 0)
        self.setMinimumWidth(objectModel.minimumWidth())
        self.setMinimumHeight(objectModel.minimumHeight())
        self.setToolTip(self.model.toolTip())

    def init(self):
        pass

    def mousePressEvent(self, event):
        self.model.setSelected(True)
        super(QBaseNode, self).mousePressEvent(event)

    def setSelected(self, selected):
        self.model.setSelected(True)
        super(QBaseNode, self).setSelected(selected)

    def mouseMoveEvent(self, event):
        scene = self.scene()
        items = scene.selectedNodes()

        for i in items:
            pos = i.pos() + i.mapToParent(event.pos()) - i.mapToParent(event.lastPos())
            i.setPos(pos)
            i.model.setPosition((pos.x(), pos.y()))

        self.scene().updateAllConnections()


class Pin(QBaseNode):
    def __init__(self, objectModel, parent=None):
        super(Pin, self).__init__(objectModel, parent)

    def boundingRect(self):
        return QtCore.QRect(0, 0, 15, 15)

    def paint(self, painter, option, widget):
        rect = self.boundingRect()

        thickness = self.model.edgeThickness()
        if self.isSelected():
            standardPen = QtGui.QPen(self.model.selectedNodeColour(), thickness + 1)
        else:
            standardPen = QtGui.QPen(self.model.edgeColour(), thickness)
        painter.setBrush(self.model.backgroundColour())
        painter.setPen(standardPen)
        painter.drawEllipse(rect)

        super(Pin, self).paint(painter, option, widget)


class ResizerItem(QtWidgets.QGraphicsItem):
    def __init__(self, objectModel, parent=None):
        super(ResizerItem, self).__init__(parent)
        self.setFlag(self.ItemIsSelectable, True)
        self.setFlag(self.ItemIsMovable, True)
        self.setFlag(self.ItemSendsGeometryChanges, True)
        self.setCursor(QtGui.QCursor(QtCore.Qt.SizeFDiagCursor))
        self.setToolTip('double-click auto resize')
        self.objectModel = objectModel

    def boundingRect(self):
        size = self.objectModel.resizerSize()
        parentItem = self.parentItem()
        rect = parentItem.boundingRect()
        width = rect.width()
        height = rect.height()
        thickness = self.objectModel.edgeThickness()
        return QtCore.QRectF(width-size-thickness, height-size-thickness, size,size)

    def itemChange(self, change, value):
        if change == self.ItemPositionChange:
            item = self.parentItem()
            mx = self.objectModel.minimumHeight()
            my = self.objectModel.minimumWidth()
            # size = self.objectModel.minimumHeight()
            # mx,my = size.width(), size.height()
            totalx = mx+value.x()
            totaly = mx+value.y()
            valuex = value.x()
            valuey = value.y()
            if totalx > mx:
                totalx = mx
                valuex = 0
            if totaly > my:
                totaly = my
                valuey = 0

            # x = mx if value.x() < mx else value.x()
            # y = my if value.y() < my else value.y()
            value = QtCore.QPointF(valuex, valuey)
            nodeSize = QtCore.QSizeF(totalx, totaly)
            # item.setMinimumSize(nodeSize)
            print(value, nodeSize)


            # item.on_sizer_pos_changed(value)
        return super(ResizerItem, self).itemChange(change, value)
    # def mouseDoubleClickEvent(self, event):
    #     item = self.parentItem()
    #     item.on_sizer_double_clicked()

    def paint(self, painter, option, widget):
        rect = self.boundingRect()
        if self.objectModel.isSelected():
            color = self.objectModel.selectedNodeColour()
        else:
            color = self.objectModel.backgroundColour()
            color = color.lighter(90)

        path = QtGui.QPainterPath()
        path.moveTo(rect.topRight())
        path.lineTo(rect.bottomRight())
        path.lineTo(rect.bottomLeft())
        painter.setBrush(color)
        painter.setPen(QtCore.Qt.NoPen)
        painter.fillPath(path, painter.brush())


class Comment(QBaseNode):

    def __init__(self, objectModel, parent=None):
        super(Comment, self).__init__(objectModel, parent)
        self.backgroundColour = QtGui.QBrush(self.model.backgroundColour())
        self.cornerRounding = self.model.cornerRounding()
        self._resizer = ResizerItem(objectModel, parent=self)
        self.init()

    def init(self):
        layout = elements.vGraphicsLinearLayout(parent=self)
        self.header = NodeHeader(self,
                                 self.model.text(),
                                 self.model.secondaryText(),
                                 icon=self.model.icon(),
                                 parent=self)
        # self.header.headerTextChanged.connect(self.onHeaderTextChanged)
        # self.header.headerButtonStateChanged.connect(self.onHeaderButtonStateChanged)

        layout.addItem(self.header)

        self.setLayout(layout)

    def paint(self, painter, option, widget):
        # main rounded rect
        rect = self.boundingRect()
        thickness = self.model.edgeThickness()
        backgroundColor = self.model.backgroundColour()

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

        painter.setBrush(QtGui.QBrush(backgroundColor))
        painter.fillPath(roundedPath, painter.brush())

        # header rectangle
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(self.model.headerColor())

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

        super(Comment, self).paint(painter, option, widget)


class Backdrop(Comment):

    def __init__(self, objectModel, parent=None):
        super(Backdrop, self).__init__(objectModel, parent)


class GraphicsNode(QBaseNode):

    def __init__(self, objectModel, parent=None):
        super(GraphicsNode, self).__init__(objectModel, parent=parent)
        self.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))

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
        # self.attributeContainer.hide()
        # self.header.hide()

        self.setLayout(layout)
        # now bind the attributes from the model if it has any
        for attr in self.model.attributes(inputs=True, outputs=True, attributeVisLevel=ATTRIBUTE_VIS_LEVEL_ONE):
            self.addAttribute(attr)
        self._connections()

    def _connections(self):
        # bind the objectModel signals to this qNode
        self.model.sigAddAttribute.connect(self.addAttribute)
        # self.model.attributeNameChangedSig.connect(self.setAttributeName)
        # self.model.nodeNameChangedSig.connect(self.header.setText)
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
                             childBoundingRect.width(),
                             childBoundingRect.height())

    def paint(self, painter, option, widget):
        # main rounded rect
        rect = self.boundingRect()
        thickness = self.model.edgeThickness()
        backgroundColor = self.model.backgroundColour()

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
        linearGradient.setStops([(0.0, backgroundColor),
                                 (0.001, backgroundColor.lighter(110)),
                                 (0.25, backgroundColor.lighter(110)),
                                 (0.2501, backgroundColor),
                                 (0.5, backgroundColor),
                                 (0.501, backgroundColor.lighter(110)),
                                 (0.75, backgroundColor.lighter(110)),
                                 (0.7501, backgroundColor),
                                 (1.0, backgroundColor),
                                 ])

        painter.setBrush(QtGui.QBrush(linearGradient))
        painter.fillPath(roundedPath, painter.brush())

        # header rectangle
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(self.model.headerColor())

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
