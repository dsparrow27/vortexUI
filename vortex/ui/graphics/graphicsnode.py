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
        pos = event.pos()
        self.model.setPosition((pos.x(), pos.y()))
        self.scene().updateAllConnections()


class Pin(QBaseNode):

    def __init__(self, objectModel, parent=None):
        super(Pin, self).__init__(objectModel, parent)

    def boundingRect(self):
        return QtCore.QRect(0, 0, 25, 25)

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


class Comment(QBaseNode):

    def __init__(self, objectModel, parent=None):
        super(Comment, self).__init__(objectModel, parent)
        self.backgroundColour = QtGui.QBrush(self.model.backgroundColour())
        self.cornerRounding = self.model.cornerRounding()
        self.init()

    def init(self):
        layout = elements.vGraphicsLinearLayout(parent=self)
        # print(self.model.icon().pixmap(16,16))
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
        thickness = self.model.edgeThickness()
        if self.isSelected():
            standardPen = QtGui.QPen(self.model.selectedNodeColour(), thickness + 1)
        else:
            standardPen = QtGui.QPen(self.model.edgeColour(), thickness)
        rect = self.boundingRect()
        rounded_rect = QtGui.QPainterPath()
        roundingY = self.cornerRounding
        rounded_rect.addRoundRect(rect,
                                  0.0, roundingY
                                  )
        painter.setBrush(self.backgroundColour)
        painter.fillPath(rounded_rect, painter.brush())
        # Title BG
        painter.setPen(QtGui.QPen(self.model.headerColor()))
        titleHeight = self.header.size().height()
        #
        painter.setBrush(self.model.headerColor())
        painter.drawRect(rect.x(), rect.y(), rect.width(), titleHeight)
        # outer node edge
        painter.strokePath(rounded_rect, standardPen)

        super(Comment, self).paint(painter, option, widget)


class Backdrop(QBaseNode):

    def __init__(self, objectModel, parent=None):
        super(Backdrop, self).__init__(objectModel, parent)

    def paint(self, painter, option, widget):
        super(Backdrop, self).paint(painter, option, widget)


class GraphicsNode(QBaseNode):

    def __init__(self, objectModel, parent=None):
        super(GraphicsNode, self).__init__(objectModel, parent=parent)
        self.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))

        self.header = None
        self.attributeContainer = None

        self.backgroundColour = QtGui.QBrush(self.model.backgroundColour())
        self.cornerRounding = self.model.cornerRounding()
        self.gradientStops = [(0.0, self.model.backgroundColour()),
                              (0.001, self.model.backgroundColour().lighter(110)),
                              (0.25, self.model.backgroundColour().lighter(110)),
                              (0.2501, self.model.backgroundColour()),
                              (0.5, self.model.backgroundColour()),
                              (0.501, self.model.backgroundColour().lighter(110)),
                              (0.75, self.model.backgroundColour().lighter(110)),
                              (0.7501, self.model.backgroundColour()),
                              (1.0, self.model.backgroundColour()),
                              ]
        self.init()

    def init(self):
        layout = elements.vGraphicsLinearLayout(parent=self)
        # print(self.model.icon().pixmap(16,16))
        self.header = NodeHeader(self,
                                 self.model.text(),
                                 self.model.secondaryText(),
                                 icon=self.model.icon(),
                                 parent=self)
        self.header.headerTextChanged.connect(self.onHeaderTextChanged)
        self.header.headerButtonStateChanged.connect(self.onHeaderButtonStateChanged)
        self.attributeContainer = graphicitems.ItemContainer(parent=self)

        layout.addItem(self.header)
        layout.addItem(self.attributeContainer)

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
                             childBoundingRect.width() - 20,
                             childBoundingRect.height())

    def paint(self, painter, option, widget):
        # main rounded rect
        thickness = self.model.edgeThickness()
        if self.isSelected():
            standardPen = QtGui.QPen(self.model.selectedNodeColour(), thickness + 1)
        else:
            standardPen = QtGui.QPen(self.model.edgeColour(), thickness)
        rect = self.boundingRect()
        rounded_rect = QtGui.QPainterPath()
        roundingY = self.cornerRounding
        rounded_rect.addRoundRect(rect,
                                  0.0, roundingY
                                  )
        linearGradient = QtGui.QLinearGradient(rect.x(), rect.y(), rect.width() * 0.75, 100)
        linearGradient.setSpread(QtGui.QLinearGradient.RepeatSpread)
        linearGradient.setFinalStop(QtCore.QPoint(25, 50))
        linearGradient.setStops(self.gradientStops)
        painter.setBrush(QtGui.QBrush(linearGradient))
        painter.fillPath(rounded_rect, painter.brush())
        # Title BG
        painter.setPen(QtGui.QPen(self.model.headerColor()))
        titleHeight = self.header.size().height()
        #
        painter.setBrush(self.model.headerColor())
        painter.drawRect(rect.x(), rect.y(), rect.width(), titleHeight)
        # outer node edge
        painter.strokePath(rounded_rect, standardPen)

        super(GraphicsNode, self).paint(painter, option, widget)
