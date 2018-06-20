from zoo.libs.pyqt.widgets.graphics import graphicitems
from vortex.ui.graphics import plugwidget
from qt import QtWidgets, QtCore, QtGui

from PySide2 import QtWidgets, QtGui, QtCore


class NodeHeaderButton(QtWidgets.QGraphicsWidget):
    stateChanged = QtCore.Signal(int)

    def __init__(self, size, color, *args, **kwargs):
        super(NodeHeaderButton, self).__init__(*args, **kwargs)
        self.color = color
        self._size = size
        self.setMinimumHeight(size)
        self.setMaximumHeight(size)
        self.setMinimumWidth(size)
        self.setMaximumWidth(size)
        self.state = 0
        self.update()

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            if self.state >= 3:
                self.state = 0
            elif self.state <= 0:
                self.state += 1
            else:
                self.state += 1
            self.stateChanged.emit(self.state)
            self.update()

    def paint(self, painter, option, widget):
        avg = self._size / 3.0
        mid = self._size / 2.0
        if self.state == 0:
            self._stroke(painter, 0, 0, self._size, avg)
            self._stroke(painter, 0, mid, self._size, avg)
            self._stroke(painter, 0, self._size, self._size, avg)
        elif self.state == 1:
            self._solidRect(painter, 0, 0, self._size, avg)
            self._stroke(painter, 0, mid, self._size, avg)
            self._stroke(painter, 0, self._size, self._size, avg)
        elif self.state == 2:
            self._solidRect(painter, 0, 0, self._size, avg)
            self._solidRect(painter, 0, mid, self._size, avg)
            self._stroke(painter, 0, self._size, self._size, avg)
        elif self.state == 3:
            self._solidRect(painter, 0, 0, self._size, avg)
            self._solidRect(painter, 0, mid, self._size, avg)
            self._solidRect(painter, 0, self._size, self._size, avg)
        super(NodeHeaderButton, self).paint(painter, option, widget)

    def _solidRect(self, painter, x, y, width, height):
        rect = QtCore.QRect(x, y, width, height)
        rounded_rect = QtGui.QPainterPath()
        roundingX = 20
        roundingY = int(150.0 * 20 / rect.height())
        rounded_rect.addRoundRect(rect,
                                  roundingX, roundingY
                                  )
        painter.setBrush(self.color)
        painter.fillPath(rounded_rect, painter.brush())

    def _stroke(self, painter, x, y, width, height):
        rect = QtCore.QRect(x, y, width, height)
        rounded_rect = QtGui.QPainterPath()
        roundingX = 20
        roundingY = int(150.0 * 20 / rect.height())
        rounded_rect.addRoundRect(rect,
                                  roundingX, roundingY
                                  )
        painter.strokePath(rounded_rect, QtGui.QPen(self.color, 1))


class NodeHeader(QtWidgets.QGraphicsWidget):
    headerButtonStateChanged = QtCore.Signal(int)

    def __init__(self, node, text, secondaryText="", parent=None):
        super(NodeHeader, self).__init__(parent)
        self._node = node
        self.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))

        layout = QtWidgets.QGraphicsLinearLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setOrientation(QtCore.Qt.Horizontal)
        self.setLayout(layout)
        self._createLabels(text, secondaryText, layout)
        layout.addStretch(1)
        headerButton = NodeHeaderButton(size=12, color=node.model.headerButtonColor())
        headerButton.stateChanged.connect(self.headerButtonStateChanged.emit)
        layout.addItem(headerButton)
        layout.setAlignment(headerButton, QtCore.Qt.AlignCenter | QtCore.Qt.AlignCenter)

    def _createLabels(self, primary, secondary, parentLayout):
        container = graphicitems.ItemContainer(QtCore.Qt.Vertical, parent=self)
        container.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))
        self._titleWidget = graphicitems.GraphicsText(primary, self)
        self._titleWidget.setTextFlags(
            QtWidgets.QGraphicsItem.ItemIsSelectable & QtWidgets.QGraphicsItem.ItemIsFocusable &
            QtWidgets.QGraphicsItem.ItemIsMovable)
        self._titleWidget.font = QtGui.QFont("Roboto-Bold.ttf", 8)
        self._secondarytitle = graphicitems.GraphicsText(secondary, self)
        self._secondarytitle.setTextFlags(
            QtWidgets.QGraphicsItem.ItemIsSelectable & QtWidgets.QGraphicsItem.ItemIsFocusable &
            QtWidgets.QGraphicsItem.ItemIsMovable)
        self._secondarytitle.font = QtGui.QFont("Roboto-Bold.ttf", 6)
        container.addItem(self._titleWidget, QtCore.Qt.AlignCenter | QtCore.Qt.AlignTop)
        container.addItem(self._secondarytitle, QtCore.Qt.AlignCenter | QtCore.Qt.AlignTop)
        parentLayout.addItem(container)

    def setText(self, text):
        self._titleWidget.setText(text)


class GraphicsNode(QtWidgets.QGraphicsWidget):
    requestExpansion = QtCore.Signal()

    def __init__(self, objectModel, position=(0, 0, 0)):
        super(GraphicsNode, self).__init__()
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)
        self.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))
        self.setMinimumWidth(objectModel.minimumWidth())
        self.setMinimumHeight(objectModel.minimumHeight())
        self.model = objectModel

        self.backgroundColour = QtGui.QBrush(self.model.backgroundColour())
        self.cornerRounding = self.model.cornerRounding()
        self.setZValue(1)
        self.setPos(position)
        self.init()

    def isSelected(self):
        return self.model.isSelected()

    def setSelected(self, selected):
        self.model.setSelected(bool(selected))
        super(GraphicsNode, self).setSelected(selected)

    def init(self):
        layout = QtWidgets.QGraphicsLinearLayout(parent=self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setOrientation(QtCore.Qt.Vertical)
        self.header = NodeHeader(self, self.model.text(), self.model.secondaryText(), parent=self)
        self.header.headerButtonStateChanged.connect(self.onHeaderButtonStateChanged)
        self.attributeContainer = graphicitems.ItemContainer(parent=self)
        self.setToolTip(self.model.toolTip())
        layout.addItem(self.header)
        layout.addItem(self.attributeContainer)

        self.setLayout(layout)
        # now bind the attributes from the model if it has any
        for attr in self.model.attributes():
            self.addAttribute(attr)

    def onHeaderButtonStateChanged(self, state):
        pass

    def addAttribute(self, attribute):
        self.attributeContainer.addItem(plugwidget.PlugContainer(attribute, parent=self.attributeContainer))

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.setSelected(True)

    def mouseMoveEvent(self, event):
        scene = self.scene()
        items = scene.selectedNodes()
        for i in items:
            pos = i.pos() + i.mapToParent(event.pos()) - i.mapToParent(event.lastPos())
            i.setPos(pos)
            for item in i.attributeContainer.items():
                if isinstance(item, plugwidget.PlugContainer):
                    item.updateConnections()

    def doubleClickEvent(self, event):
        if self.model.isCompound():
            self.requestExpansion.emit()

    def paint(self, painter, option, widget):
        # main rounded rect
        thickness = self.model.edgeThickness()
        if self.isSelected():
            standardPen = QtGui.QPen(self.model.selectedNodeColour(), thickness + 1)
        else:
            standardPen = QtGui.QPen(self.model.edgeColour(), thickness)

        rect = self.windowFrameRect()
        rounded_rect = QtGui.QPainterPath()
        roundingX = 0.0
        roundingY = int(150.0 * self.cornerRounding / rect.height())
        rounded_rect.addRoundRect(rect,
                                  roundingX, roundingY
                                  )
        painter.setBrush(self.backgroundColour)
        painter.fillPath(rounded_rect, painter.brush())
        # Title BG
        titleHeight = self.header.size().height()
        #
        painter.setBrush(self.model.headerColor())
        painter.drawRoundedRect(0, 0, rect.width(), titleHeight, 0.0, roundingY, QtCore.Qt.AbsoluteSize)
        painter.drawRect(0, 0, rect.width(), titleHeight)

        # horizontal line
        painter.strokePath(rounded_rect, standardPen)

        super(GraphicsNode, self).paint(painter, option, widget)
