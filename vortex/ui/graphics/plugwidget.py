from zoo.libs.pyqt.widgets.graphics import graphicitems
from vortex.ui.graphics import edge
from qt import QtWidgets, QtCore, QtGui


class PlugItem(QtWidgets.QGraphicsEllipseItem):
    def __init__(self, pen, brush, hOffset, radius, diameter, parent):
        super(PlugItem, self).__init__(parent=parent)
        self.setPen(pen)
        self.setBrush(brush)
        self.setRect(radius, radius, diameter, diameter)

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

    def __init__(self, color, edgeColor, highlightColor, hOffset, parent=None):
        super(Plug, self).__init__(parent=parent)
        size = QtCore.QSizeF(self._diameter, self._diameter)
        self.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed))
        self.setPreferredSize(size)
        self.setWindowFrameMargins(0, 0, 0, 0)
        self._defaultPen = QtGui.QPen(edgeColor, 1.0)
        self._hoverPen = QtGui.QPen(highlightColor, 1.5)
        self._brush = QtGui.QBrush(color)

        self._item = PlugItem(self._defaultPen, self._brush, hOffset, self._radius, self._diameter, parent=self)

        self.setAcceptHoverEvents(True)

    @property
    def color(self):
        return self._item.brush().color()

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
        # super(Plug, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        self.moveEventRequested.emit(self, event)

    def mouseReleaseEvent(self, event):
        self.releaseEventRequested.emit(self, event)


class PlugTextItem(graphicitems.GraphicsText):

    def __init__(self, text, parent=None):
        super(PlugTextItem, self).__init__(text, parent)
        self._parent = parent
        self._mouseDownPosition = QtCore.QPoint()
        self.setTextFlags(QtWidgets.QGraphicsItem.ItemIsSelectable & QtWidgets.QGraphicsItem.ItemIsFocusable &
                          QtWidgets.QGraphicsItem.ItemIsMovable)
        self._item.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)

    def mousePressEvent(self, event):
        self._mouseDownPosition = self.mapToScene(event.pos())

    def mouseMoveEvent(self, event):
        scenePos = self.mapToScene(event.pos())
        # When clicking on an UI port label, it is ambigous which connection point should be activated.
        # We let the user drag the mouse in either direction to select the conneciton point to activate.
        delta = scenePos - self._mouseDownPosition
        parent = self._parent
        if parent is not None:
            if delta.x() < 0:
                if parent.inCircle is not None:
                    parent.inCircle.mousePressEvent(event)
                return
            if parent.outCircle is not None:
                parent.outCircle.mousePressEvent(event)


class PlugContainer(QtWidgets.QGraphicsWidget):
    _radius = 4.5
    _diameter = 2 * _radius

    def __init__(self, attributeModel, parent=None):
        super(PlugContainer, self).__init__(parent)
        self.model = attributeModel
        layout = QtWidgets.QGraphicsLinearLayout(parent=self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        layout.setOrientation(QtCore.Qt.Horizontal)
        self.setLayout(layout)
        self.inCircle = Plug(self.model.itemColour(),
                             self.model.itemEdgeColor(),
                             self.model.highlightColor(),
                             hOffset=0.0, parent=self)
        self.outCircle = Plug(self.model.itemColour(),
                              self.model.itemEdgeColor(),
                              self.model.highlightColor(), hOffset=0.0, parent=self)
        self.inCircle.setToolTip(attributeModel.toolTip())
        self.outCircle.setToolTip(attributeModel.toolTip())

        self.label = PlugTextItem(self.model.text(), parent=self)
        self.label.color = attributeModel.textColour() or QtGui.QColor(200, 200, 200)


        if not attributeModel.isOutput():
            self.outCircle.hide()
        if not attributeModel.isInput():
            self.inCircle.hide()
            # if attributeModel.isOutput():# and not attributeModel.objectModel.isCompound():
            #     layout.addStretch(1)
        self.inCircle.setToolTip(self.model.toolTip())
        self.outCircle.setToolTip(self.model.toolTip())
        layout.addItem(self.inCircle)
        layout.addItem(self.label)
        layout.addItem(self.outCircle)
        layout.setAlignment(self.label, attributeModel.textAlignment())

        self.setInputAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.setOutputAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

        self.label.allowHoverHighlight = True
        self.inCircle.leftMouseButtonClicked.connect(self.onPlugClicked)
        self.outCircle.leftMouseButtonClicked.connect(self.onPlugClicked)
        self.inCircle.moveEventRequested.connect(self.onPlugMove)
        self.outCircle.moveEventRequested.connect(self.onPlugMove)
        self.inCircle.releaseEventRequested.connect(self.onPlugRelease)
        self.outCircle.releaseEventRequested.connect(self.onPlugRelease)
        # used purely to store the connection request transaction
        self._currentConnection = None

    def setLabel(self, label):
        self.label.setText(label)

    def setInputAlignment(self, alignment):
        self.layout().setAlignment(self.inCircle, alignment)

    def setOutputAlignment(self, alignment):
        self.layout().setAlignment(self.outCircle, alignment)

    def addConnection(self, plug):
        self.scene().removeItem(self._currentConnection)
        self._currentConnection = None
        connection = edge.ConnectionEdge(self.outCircle,
                                         plug.inCircle,
                                         curveType=self.uiApplication.config.defaultConnectionShape)
        connection.setLineStyle(self.uiApplication.config.defaultConnectionStyle)
        connection.setWidth(self.uiApplication.config.connectionLineWidth)
        connection.updatePosition()
        scene = self.scene()

        scene.connections.add(connection)
        self.scene().addItem(connection)

    def updateConnections(self):
        self.scene().updateConnectionsForPlug(self)

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
        self._currentConnection.destinationPoint = plug.center()
        self.scene().addItem(self._currentConnection)

    def onPlugMove(self, plug, event):
        newPosition = event.scenePos()
        self._currentConnection.destinationPoint = newPosition

    def onPlugRelease(self, plug, event):
        if self._currentConnection is not None:
            end = self._currentConnection.path().pointAtPercent(1)
            endItem = self.scene().itemAt(end, QtGui.QTransform())
            # if we're a plugItem then offload the connection handling to the model
            # the model will then call the scene.createConnection via a signal
            # this is so we let the client code determine if the connection is legal
            if isinstance(endItem, PlugItem):
                dest = self if self.model.isInput() else endItem.parentObject().parentObject()
                self.model.createConnection(dest.model)
            self.scene().removeItem(self._currentConnection)
            self._currentConnection = None
        self.scene().update()
