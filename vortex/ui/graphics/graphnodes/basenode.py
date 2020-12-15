import os

from zoo.libs.pyqt.widgets.graphics import graphicitems
from Qt import QtWidgets, QtCore, QtGui

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

    def __init__(self, model, parent=None):
        super(NodeHeader, self).__init__(orientation=QtCore.Qt.Horizontal, parent=parent)
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding)
        self.setWindowFrameMargins(0, 0, 0, 0)
        self.setAcceptedMouseButtons(QtCore.Qt.NoButton)

        self.model = model

        self._createLabels(model.text())
        self.headerButton = NodeHeaderButton(size=12, colour=model.headerButtonColour(), parent=self)
        self.headerButton.stateChanged.connect(self.headerButtonStateChanged.emit)

        self.addItem(self.headerButton, QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.setTextColour(self.model.textColour())

    def _createLabels(self, primary):
        self._titleWidget = graphicitems.GraphicsText(primary, parent=self)
        self._titleWidget.multiLineSupported = False
        self._titleWidget.textEditFinished.connect(self.headerTextChanged)
        self.addItem(self._titleWidget, QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
        fontmetrics = QtGui.QFontMetrics(self._titleWidget.font)
        height = fontmetrics.height() * 2
        self.setMinimumHeight(height)
        self.setMaximumHeight(height)

    def setText(self, text):
        self._titleWidget.blockSignals(True)
        self._titleWidget.text = text
        self._titleWidget.blockSignals(False)

    def setTextColour(self, color):
        self._titleWidget.color = color

    def boundingRect(self):
        return QtCore.QRectF(0, 0, self.model.width(), 25)

    def geometry(self):
        return self.boundingRect()

    if os.environ.get("DEBUG", "0") == "1":
        def paint(self, painter, option, widget):
            painter.setBrush(QtCore.Qt.NoBrush)
            painter.setPen(QtGui.QPen(QtCore.Qt.green, 0.75))
            painter.drawRect(self.geometry())
            super(NodeHeader, self).paint(painter, option, widget)


class QBaseNode(QtWidgets.QGraphicsWidget):
    ATTRIBUTE_VIS_LEVEL_ZERO = 0
    ATTRIBUTE_VIS_LEVEL_ONE = 1
    ATTRIBUTE_VIS_LEVEL_TWO = 2

    def __init__(self, objectModel, parent=None):
        super(QBaseNode, self).__init__(parent=parent)
        self.model = objectModel
        self.setZValue(1)
        self.setAcceptHoverEvents(True)
        self.setFlags(self.ItemIsSelectable | self.ItemIsMovable | self.ItemSendsGeometryChanges)
        self.setMinimumSize(objectModel.minimumWidth(), objectModel.minimumHeight())
        self.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))
        self.setToolTip(self.model.toolTip())
        self.shad = QtWidgets.QGraphicsDropShadowEffect(self)
        self.shad.setColor(QtGui.QColor(10,10,10))
        self.shad.setOffset(4)
        self.setGraphicsEffect(self.shad)

    def setPos(self, pos):
        self.model.setPosition((pos.x(), pos.y()))
        super(QBaseNode, self).setPos(pos)

    def resize(self, x, y):
        self.model.setWidth(x)
        self.model.setHeight(y)
        super(QBaseNode, self).resize(x, y)

    def init(self):
        self.setPos(QtCore.QPoint(*self.model.position()))

    def boundingRect(self, *args, **kwargs):
        return QtCore.QRectF(0, 0, self.model.width(), self.model.height())

    def geometry(self):
        return self.boundingRect()

    def setSelected(self, selected):
        self.model.setSelected(True)
        super(QBaseNode, self).setSelected(selected)

    if os.environ.get("DEBUG", "0") == "1":
        def paint(self, painter, option, widget):
            painter.setBrush(QtCore.Qt.NoBrush)
            painter.setPen(QtGui.QPen(QtCore.Qt.green, 0.75))
            painter.drawRect(self.geometry())
            super(QBaseNode, self).paint(painter, option, widget)

    def mouseMoveEvent(self, event):
        scene = self.scene()
        items = scene.selectedNodes()

        for i in items:
            pos = i.pos() + i.mapToParent(event.pos()) - i.mapToParent(event.lastPos())
            i.setPos(pos)

        self.scene().updateAllConnections()
