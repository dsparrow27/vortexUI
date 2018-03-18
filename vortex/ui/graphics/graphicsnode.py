from zoo.libs.pyqt.widgets.graphics import graphicitems, graphbackdrop
from vortex.ui.graphics import plugwidget
from qt import QtWidgets, QtCore, QtGui


class GraphicsNode(QtWidgets.QGraphicsWidget):
    requestExpansion = QtCore.Signal()

    def __init__(self, objectModel, position=(0,0,0)):
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
        self.headerText = graphicitems.TextContainer(self.model.text(), parent=self)
        self.headerText.title.setTextFlags(QtWidgets.QGraphicsItem.ItemIsFocusable &
                                           QtWidgets.QGraphicsItem.ItemIsMovable)
        self.attributeContainer = graphicitems.ItemContainer(parent=self)
        self.setToolTip(self.model.toolTip())
        layout.addItem(self.headerText)
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
        if self.isSelected():
            standardPen = QtGui.QPen(self.model.selectedNodeColour(), 3)
        else:
            standardPen = QtGui.QPen(self.model.edgeColour(), 3)
        rect = self.windowFrameRect()
        rounded_rect = QtGui.QPainterPath()
        roundingX = int(150.0 * self.cornerRounding / rect.width())
        roundingY = int(150.0 * self.cornerRounding / rect.height())
        rounded_rect.addRoundRect(rect,
                                  roundingX,
                                  roundingY)
        painter.setBrush(self.backgroundColour)
        painter.fillPath(rounded_rect, painter.brush())
        # horizontal line
        labelRect = QtCore.QRectF(rect.left(), rect.top(), rect.width(), 20)
        painter.strokePath(rounded_rect, standardPen)
        painter.setPen(standardPen)
        painter.drawLine(labelRect.bottomLeft(), labelRect.bottomRight())

        super(GraphicsNode, self).paint(painter, option, widget)
