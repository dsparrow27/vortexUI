from zoo.libs.pyqt.widgets.graphics import graphicitems
from vortex.ui.graphics import edge
from qt import QtWidgets, QtCore, QtGui


class PlugItem(QtWidgets.QGraphicsEllipseItem):
    def __init__(self, pen, brush, hOffset, radius, diameter, parent):
        super(PlugItem, self).__init__(parent=parent)
        self.setPen(pen)
        self.setBrush(brush)
        self.setPos(hOffset, radius)
        self.setRect(-radius, -radius, diameter, diameter)

    def center(self):
        rect = self.boundingRect()
        center = QtCore.QPointF(rect.x() + rect.width() * 0.5, rect.y() + rect.height() * 0.5)
        return self.mapToScene(center)


class Plug(QtWidgets.QGraphicsWidget):
    rightMouseButtonClicked = QtCore.Signal(object, object)
    leftMouseButtonClicked = QtCore.Signal(object, object)
    moveEventRequested = QtCore.Signal(object, object)
    releaseEventRequested = QtCore.Signal(object, object)
    _radius = 4.5
    _diameter = 2 * _radius
    INPUT_TYPE = 0
    OUTPUT_TYPE = 1

    def __init__(self, color, highlightColor, hOffset, parent=None):
        super(Plug, self).__init__(parent=parent)
        size = QtCore.QSizeF(self._diameter, self._diameter)
        self.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed))
        self.setPreferredSize(size)
        self.setWindowFrameMargins(0, 0, 0, 0)
        self._defaultPen = QtGui.QPen(color, 1.0)
        self._hoverPen = QtGui.QPen(highlightColor, 1.5)
        self._brush = QtGui.QBrush(color)

        self._item = PlugItem(self._defaultPen, self._brush, hOffset, self._radius, self._diameter, parent=self)

        self.setAcceptHoverEvents(True)

    @property
    def color(self):
        return self._item.brush.color()

    @color.setter
    def color(self, color):
        self._item.setBrush(QtGui.QBrush(color))

    def highlight(self):
        self._item.setBrush(QtGui.QBrush(self._item.brush().color().lighter()))

    def unhighlight(self):
        self._item.setBrush(self._brush)

    def center(self):
        rect = self._item.boundingRect()
        center = QtCore.QPointF(rect.x() + rect.width() * 0.5, rect.y() + rect.height() * 0.5)
        return self._item.mapToScene(center)

    def hoverEnterEvent(self, event):
        self.highlight()
        super(Plug, self).hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.unhighlight()
        super(Plug, self).hoverLeaveEvent(event)

    def mousePressEvent(self, event):
        btn = event.button()
        if btn == QtCore.Qt.LeftButton:
            self.leftMouseButtonClicked.emit(self, event)
        elif btn == QtCore.Qt.RightButton:
            self.rightMouseButtonClicked.emit(self, event)

    def mouseMoveEvent(self, event):
        self.moveEventRequested.emit(self, event)

    def mouseReleaseEvent(self, event):
        self.releaseEventRequested.emit(self, event)


class PlugContainer(QtWidgets.QGraphicsWidget):
    _radius = 4.5
    _diameter = 2 * _radius

    def __init__(self, attributeModel, parent=None):
        super(PlugContainer, self).__init__(parent)
        self.model = attributeModel
        layout = QtWidgets.QGraphicsLinearLayout(parent=self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setOrientation(QtCore.Qt.Horizontal)
        self.setLayout(layout)
        self.inCircle = Plug(self.model.itemColour(), self.model.highlightColor(), hOffset=0.0, parent=self)
        self.outCircle = Plug(self.model.itemColour(), self.model.highlightColor(), hOffset=Plug._diameter, parent=self)
        self.inCircle.setToolTip(attributeModel.toolTip())
        self.outCircle.setToolTip(attributeModel.toolTip())

        self.label = graphicitems.GraphicsText(self.model.text(), parent=self)
        self.label.color = attributeModel.textColour() or QtGui.QColor(200, 200, 200)
        self.label.setTextFlags(QtWidgets.QGraphicsItem.ItemIsSelectable & QtWidgets.QGraphicsItem.ItemIsFocusable &
                                QtWidgets.QGraphicsItem.ItemIsMovable)
        layout.addItem(self.inCircle)
        if not attributeModel.isOutput():
            self.outCircle.hide()
        if not attributeModel.isInput():
            self.inCircle.hide()
            if attributeModel.isOutput():
                layout.addStretch(1)
        layout.addItem(self.label)
        layout.addItem(self.outCircle)
        layout.setAlignment(self.label, QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        self.setInputAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.setOutputAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

        self.label.allowHoverHighlight = True
        self.inCircle.leftMouseButtonClicked.connect(self.onPlugClicked)
        self.outCircle.leftMouseButtonClicked.connect(self.onPlugClicked)
        self.inCircle.moveEventRequested.connect(self.onPlugMove)
        self.outCircle.moveEventRequested.connect(self.onPlugMove)
        self.inCircle.releaseEventRequested.connect(self.onPlugRelease)
        self.outCircle.releaseEventRequested.connect(self.onPlugRelease)
        # stores the plug to plug connections
        self.connections = set()
        # used purely to store the connection request transaction
        self._currentConnection = None

    def setInputAlignment(self, alignment):
        self.layout().setAlignment(self.inCircle, alignment)

    def setOutputAlignment(self, alignment):
        self.layout().setAlignment(self.outCircle, alignment)

    def addConnection(self, plug):
        plugModel = plug.parentObject().model
        if not self.model.canAcceptConnection(plugModel):
            return
        result = self.model.createConnection(plugModel)
        if not result:
            return
        if self.model.isInput():
            connection = edge.ConnectionEdge(self, plug)
        else:
            connection = edge.ConnectionEdge(plug, self)
        self.connections.add(connection)
        self.connectionAdded.emit(connection)


    def removeConnection(self, edge):
        self.connections.remove(edge)
        self.connectionRemoved.emit(edge)

    def disconnectAll(self):
        self.connections.clear()
        self.cleared.emit()

    def updateConnections(self):

        for connection in self.connections:
            connection.updatePosition()

    # handle connection methods
    def onPlugClicked(self, plug, event):
        """Trigger when either the inCircle or outCircle is clicked, this method will handle setup of the connection
        object and appropriately call the attributeModel.
        :param plug: Plug class
        :type plug: ::class:`Plug`
        :param event:
        :type event: ::class:`QEvent`
        :return:
        :rtype:
        """
        self._currentConnection = edge.ConnectionEdge(plug)
        self._currentConnection.destinationPoint = event.scenePos()
        self.scene().addItem(self._currentConnection)

    def onPlugMove(self, plug, event):
        newPosition = event.scenePos()
        self._currentConnection.destinationPoint = newPosition

    def onPlugRelease(self, plug, event):
        if self._currentConnection is not None:
            end = self._currentConnection.path().pointAtPercent(1)
            endItem = self.scene().itemAt(end, QtGui.QTransform())
            if isinstance(endItem, PlugItem):
                model = endItem.parentObject().parentObject().model
                if self.model.canAcceptConnection(model):
                    self.model.createConnection(model)
                    self._currentConnection.destinationPlug = endItem
                    self.connections.add(self._currentConnection)
                    self.scene().update()
                    return

            self.scene().removeItem(self._currentConnection)
            self._currentConnection = None
        self.scene().update()
