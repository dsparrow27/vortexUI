from zoo.libs.pyqt.widgets.graphics import graphicitems, graphbackdrop
from vortex.ui.graphics import plugwidget
from qt import QtWidgets, QtCore, QtGui


class NodeHeader(QtWidgets.QGraphicsWidget):

    def __init__(self, text, parent=None):
        super(NodeHeader, self).__init__(parent)

        self.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))

        layout = QtWidgets.QGraphicsLinearLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setOrientation(QtCore.Qt.Vertical)
        self.setLayout(layout)
        self._titleWidget = graphicitems.GraphicsText(text, self)
        self._titleWidget.setTextFlags(QtWidgets.QGraphicsItem.ItemIsSelectable & QtWidgets.QGraphicsItem.ItemIsFocusable &
                          QtWidgets.QGraphicsItem.ItemIsMovable)
        _font = QtGui.QFont("Roboto-Bold.ttf", 10)
        self._titleWidget.font = _font
        self._secondarytitle = graphicitems.GraphicsText(text, self)
        self._secondarytitle.setTextFlags(
            QtWidgets.QGraphicsItem.ItemIsSelectable & QtWidgets.QGraphicsItem.ItemIsFocusable &
            QtWidgets.QGraphicsItem.ItemIsMovable)
        _font = QtGui.QFont("Roboto-Bold.ttf", 6)
        self._secondarytitle.font = _font
        layout.addItem(self._titleWidget)
        layout.addItem(self._secondarytitle)

        layout.setAlignment(self._titleWidget, QtCore.Qt.AlignCenter | QtCore.Qt.AlignTop)
        layout.setAlignment(self._secondarytitle, QtCore.Qt.AlignCenter | QtCore.Qt.AlignTop)

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
        self._selected = False

        self.backgroundColour = QtGui.QBrush(self.model.backgroundColour())
        self.cornerRounding = self.model.cornerRounding()
        self.setZValue(1)
        self.setPos(position)
        self.init()

    def init(self):
        layout = QtWidgets.QGraphicsLinearLayout(parent=self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setOrientation(QtCore.Qt.Vertical)
        self.header = NodeHeader(self.model.text(), parent=self)
        self.attributeContainer = graphicitems.ItemContainer(parent=self)
        self.setToolTip(self.model.toolTip())
        layout.addItem(self.header)
        layout.addItem(self.attributeContainer)

        self.setLayout(layout)
        # now bind the attributes from the model if it has any
        for attr in self.model.attributes():
            self.addAttribute(attr)

    def addAttribute(self, attribute):
        self.attributeContainer.addItem(plugwidget.PlugContainer(attribute, parent=self.attributeContainer))

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.setSelected(True)

    def mouseMoveEvent(self, event):
        pos = self.pos() + self.mapToParent(event.pos()) - self.mapToParent(event.lastPos())
        self.setPos(pos)
        for item in self.attributeContainer.items():
            if isinstance(item, plugwidget.PlugContainer):
                item.updateConnections()

    def doubleClickEvent(self, event):
        if self.model.isCompound():
            self.requestExpansion.emit()

    def paint(self, painter, option, widget):
        # main rounded rect
        thickness = self.model.edgeThickness()
        if self.isSelected():
            standardPen = QtGui.QPen(self.model.selectedNodeColour(), thickness)
        else:
            standardPen = QtGui.QPen(self.model.edgeColour(), thickness)

        rect = self.windowFrameRect()
        rounded_rect = QtGui.QPainterPath()
        roundingX = 0.0
        roundingY = int(150.0 * self.cornerRounding / rect.height())
        rounded_rect.addRoundRect(rect,
                                  roundingX,
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
