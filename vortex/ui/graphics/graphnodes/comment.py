from Qt import QtWidgets, QtGui, QtCore

from vortex.ui.graphics.graphnodes import basenode
from zoo.libs.pyqt.widgets import elements

class BackdropSizer(QtWidgets.QGraphicsItem):
    def __init__(self, parent=None, size=6.0):
        super(BackdropSizer, self).__init__(parent)
        self.setFlag(self.ItemIsSelectable, True)
        self.setFlag(self.ItemIsMovable, True)
        self.setFlag(self.ItemSendsScenePositionChanges, True)
        self.setCursor(QtGui.QCursor(QtCore.Qt.SizeFDiagCursor))
        self._size = size

    def boundingRect(self):
        return QtCore.QRectF(0, 0, self._size, self._size)

    def itemChange(self, change, value):
        if change == self.ItemPositionChange:
            rect = self.boundingRect()
            item = self.parentItem()
            mx, my = item.model.minimumWidth(), item.model.minimumHeight()
            x = mx if value.x() < mx else value.x()
            y = my if value.y() < my else value.y()
            value = QtCore.QPointF(x, y)
            item.model.setWidth(x + rect.width())
            item.model.setHeight(y + rect.height())
            return value
        return super(BackdropSizer, self).itemChange(change, value)

    def _drawResizer(self, painter, option, widget):
        item = self.parentItem()
        if item.model.isSelected():
            colour = item.model.selectedNodeColour()
        else:
            colour = item.model.backgroundColour()
            colour = colour.lighter(150)
        rect = self.boundingRect()
        path = QtGui.QPainterPath()
        path.moveTo(rect.topRight())
        path.lineTo(rect.bottomRight())
        path.lineTo(rect.bottomLeft())
        painter.setBrush(colour)
        painter.setPen(QtCore.Qt.NoPen)
        painter.fillPath(path, painter.brush())

    def paint(self, painter, option, widget):
        """
        Draws the backdrop sizer on the bottom right corner.
        Args:
            painter (QtGui.QPainter): painter used for drawing the item.
            option (QtGui.QStyleOptionGraphicsItem):
                used to describe the parameters needed to draw.
            widget (QtWidgets.QWidget): not used.
        """
        self._drawResizer(painter, option, widget)


class Comment(basenode.QBaseNode):

    def __init__(self, objectModel, parent=None):
        super(Comment, self).__init__(objectModel, parent)
        self.backgroundColour = QtGui.QBrush(self.model.backgroundColour())
        self.cornerRounding = self.model.cornerRounding()
        self.resizer = None
        self.init()

    def init(self):
        super(Comment, self).init()
        layout = elements.vGraphicsLinearLayout(parent=self)
        # layout.set
        self.header = basenode.NodeHeader(self,
                                 self.model.text(),
                                 self.model.secondaryText(),
                                 icon=self.model.icon(),
                                 parent=self)
        self.header.headerButton.hide()
        # self.header.headerTextChanged.connect(self.onHeaderTextChanged)
        # self.header.headerButtonStateChanged.connect(self.onHeaderButtonStateChanged)
        layout.addItem(self.header)
        self.setLayout(layout)
        resizerSize = self.model.resizerSize()
        self.resizer = BackdropSizer(parent=self, size=resizerSize)
        self.resizer.setPos(self.minimumWidth(), self.minimumHeight())

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

        # outline
        if self.isSelected():
            standardPen = QtGui.QPen(self.model.selectedNodeColour(), thickness + 1)
        else:
            standardPen = QtGui.QPen(self.model.edgeColour(), thickness)
        # # outer node edge
        painter.strokePath(roundedPath,
                           standardPen)

        super(Comment, self).paint(painter, option, widget)

