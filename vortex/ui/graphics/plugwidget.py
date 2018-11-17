from zoo.libs.pyqt.widgets.graphics import graphicitems
from vortex.ui.graphics import edge
from qt import QtWidgets, QtCore, QtGui


class Plug(QtWidgets.QGraphicsWidget):
    rightMouseButtonClicked = QtCore.Signal(object, object)
    leftMouseButtonClicked = QtCore.Signal(object, object)
    moveEventRequested = QtCore.Signal(object, object)
    releaseEventRequested = QtCore.Signal(object, object)
    _diameter = 2 * 6
    INPUT_TYPE = 0
    OUTPUT_TYPE = 1

    def __init__(self, color, edgeColor, highlightColor, ioType, parent=None):
        super(Plug, self).__init__(parent=parent)
        size = QtCore.QSizeF(self._diameter, self._diameter)
        self.ioType = ""
        self.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed))
        self.setPreferredSize(size)
        self.setWindowFrameMargins(0, 0, 0, 0)
        self._defaultPen = QtGui.QPen(edgeColor, 2.5)
        self._hoverPen = QtGui.QPen(highlightColor, 3.0)
        self._defaultBrush = QtGui.QBrush(color)
        self._currentBrush = QtGui.QBrush(color)
        self.setAcceptHoverEvents(True)

    @property
    def color(self):
        return self._currentBrush.color()

    @color.setter
    def color(self, color):
        self._currentBrush = QtGui.QBrush(color)
        self.update()

    def highlight(self):
        self._currentBrush = QtGui.QBrush(self.color.lighter())

    def unhighlight(self):
        self._currentBrush = QtGui.QBrush(self._defaultBrush)
        self.update()

    def center(self):
        rect = self.boundingRect()
        center = QtCore.QPointF(rect.x() + rect.width() * 0.5, rect.y() + rect.height() * 0.5)
        return self.mapToScene(center)

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

    def paint(self, painter, options, widget=None):
        painter.setBrush(self._currentBrush)

        painter.setPen(self._defaultPen)
        painter.drawEllipse(0.0, 0.0, self._diameter, self._diameter)

    def boundingRect(self):
        return QtCore.QRectF(
            0.0,
            0.0,
            self._diameter + 2.5,
            self._diameter + 2.5,
        )


class CrossSquare(QtWidgets.QGraphicsWidget):
    leftMouseButtonClicked = QtCore.Signal()

    def __init__(self, parent=None):
        super(CrossSquare, self).__init__(parent)
        size = QtCore.QSizeF(Plug._diameter, Plug._diameter)
        self.expanded = False
        self.isElement = False
        self.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed))
        self.setPreferredSize(size)
        self.setWindowFrameMargins(0, 0, 0, 0)
        self.hide()
        self.lines = [QtCore.QLineF(QtCore.QPoint(Plug._diameter * 0.5, 3.0),
                                    QtCore.QPoint(Plug._diameter * 0.5, Plug._diameter - 3.0)),
                      QtCore.QLineF(QtCore.QPoint(3.0, Plug._diameter * 0.5),
                                    QtCore.QPoint(Plug._diameter - 3.0, Plug._diameter * 0.5))
                      ]

    def mousePressEvent(self, event):
        btn = event.button()
        if btn == QtCore.Qt.LeftButton and not self.isElement:
            self.leftMouseButtonClicked.emit()

    def paint(self, painter, options, widget=None):
        painter.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255, 1.0), 0.25))
        # draw the square

        if self.isElement:
            parentHeight = self.parentObject().size().height()
            lines = [QtCore.QLineF(QtCore.QPoint(Plug._diameter*0.5, Plug._diameter*0.5),
                                   QtCore.QPoint(Plug._diameter*0.5, -(parentHeight -Plug._diameter))),
                     QtCore.QLineF(QtCore.QPoint(Plug._diameter * 0.5, Plug._diameter * 0.5),
                                   QtCore.QPoint(Plug._diameter, Plug._diameter * 0.5))]
            painter.drawLines(lines)
        # draw the center cross
        else:
            painter.drawRect(0, 0, Plug._diameter, Plug._diameter)
            if self.expanded:
                # if we have expanded just draw the horizontal line
                painter.drawLines(self.lines[1:])
            else:
                painter.drawLines(self.lines)

    def boundingRect(self):
        return QtCore.QRectF(
            0,
            0,
            Plug._diameter + 0.25,
            Plug._diameter + 0.25,
        )


class PlugContainer(graphicitems.ItemContainer):

    def __init__(self, attributeModel, parent=None):
        super(PlugContainer, self).__init__(QtCore.Qt.Horizontal, parent)
        self.model = attributeModel
        self.childContainers = []
        self.inCrossItem = CrossSquare(parent=self)
        self.outCrossItem = CrossSquare(parent=self)

        self.inCircle = Plug(self.model.itemColour(),
                             self.model.itemEdgeColor(),
                             self.model.highlightColor(), "Input",
                             parent=self)
        self.outCircle = Plug(self.model.itemColour(),
                              self.model.itemEdgeColor(),
                              self.model.highlightColor(), "Output", parent=self)
        self.inCircle.setToolTip(attributeModel.toolTip())
        self.outCircle.setToolTip(attributeModel.toolTip())

        self.label = graphicitems.GraphicsText(self.model.text(), parent=self)
        self.label.setTextFlags(QtWidgets.QGraphicsItem.ItemIsSelectable & QtWidgets.QGraphicsItem.ItemIsFocusable &
                                QtWidgets.QGraphicsItem.ItemIsMovable)

        self.label.text.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
        self.label.color = attributeModel.textColour() or QtGui.QColor(200, 200, 200)

        if not attributeModel.isOutput():
            self.outCircle.hide()
        if not attributeModel.isInput():
            self.inCircle.hide()
        self.inCircle.setToolTip(self.model.toolTip())
        self.outCircle.setToolTip(self.model.toolTip())
        self.addItem(self.inCircle, QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.addItem(self.inCrossItem, QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.addItem(self.label, attributeModel.textAlignment())
        self.addItem(self.outCrossItem, QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.addItem(self.outCircle, QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.label.allowHoverHighlight = True
        self.inCircle.leftMouseButtonClicked.connect(self.onPlugClicked)
        self.outCircle.leftMouseButtonClicked.connect(self.onPlugClicked)
        self.inCircle.moveEventRequested.connect(self.onPlugMove)
        self.outCircle.moveEventRequested.connect(self.onPlugMove)
        self.inCircle.releaseEventRequested.connect(self.onPlugRelease)
        self.outCircle.releaseEventRequested.connect(self.onPlugRelease)
        self.inCrossItem.leftMouseButtonClicked.connect(self.onExpandInput)
        self.outCrossItem.leftMouseButtonClicked.connect(self.onExpandOutput)
        # used purely to store the connection request transaction
        self._currentConnection = None

    def setLabel(self, label):
        self.label.setText(label)

    def hideInput(self):
        self.inCircle.hide()

    def hideOutput(self):
        self.outCircle.hide()

    def showInput(self):
        self.inCircle.show()

    def showOutput(self):
        self.outCircle.show()

    def setTextAlignment(self, alignment):
        self.layout().setAlignment(self.label, alignment)

    def setInputAlignment(self, alignment):
        self.layout().setAlignment(self.inCircle, alignment)

    def setOutputAlignment(self, alignment):
        self.layout().setAlignment(self.outCircle, alignment)

    def addConnection(self, plug):
        plug.outCircle.color = plug.model.itemColour()
        self.inCircle.color = self.model.itemColour()
        connection = edge.ConnectionEdge(plug.outCircle, self.inCircle,
                                         curveType=self.model.objectModel.config.defaultConnectionShape,
                                         color=plug.outCircle.color)
        connection.setLineStyle(self.model.objectModel.config.defaultConnectionStyle)
        connection.setWidth(self.model.objectModel.config.connectionLineWidth)
        connection.updatePosition()
        plug.outCircle.color = plug.model.itemColour()
        self.inCircle.color = self.model.itemColour()
        scene = self.scene()

        scene.connections.add(connection)
        return connection

    def updateConnections(self):
        self.scene().updateConnectionsForPlug(self)

    def expand(self):
        parentContainer = self.parentObject()
        if self.model.isArray():
            if self.inCrossItem.expanded:
                for container in self.childContainers:
                    parentContainer.removeItem(container)
                    self.scene().removeItem(container)
                self.childContainers = []
                return
            else:
                children = reversed(self.model.elements())
        else:
            children = reversed(self.model.children())
        selfIndex = parentContainer.indexOf(self) + 1
        for element in children:
            elementContainer = PlugContainer(attributeModel=element, parent=self)
            elementContainer.inCrossItem.isElement = True
            elementContainer.outCrossItem.isElement = True
            parentContainer.insertItem(selfIndex, elementContainer)
            self.childContainers.append(elementContainer)
            if element.isInput():
                index = elementContainer.layout().count() - 2
                if element.isArray() or element.isCompound() or element.isElement():
                    elementContainer.inCrossItem.show()
            else:
                if element.isArray() or element.isCompound() or element.isElement():
                    elementContainer.outCrossItem.show()
                index = 2
            elementContainer.layout().insertStretch(index, 1)

    def onExpandInput(self):
        self.expand()
        self.inCrossItem.expanded = not self.inCrossItem.expanded
        self.update()

    def onExpandOutput(self):
        self.expand()
        self.outCrossItem.expanded = not self.outCrossItem.expanded
        self.update()

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
        plug.color = plug.parentObject().model.itemColour()
        self._currentConnection = edge.ConnectionEdge(plug,
                                                      curveType=self.model.objectModel.config.defaultConnectionShape,
                                                      color=plug.color)
        self._currentConnection.setLineStyle(self.model.objectModel.config.defaultConnectionStyle)
        self._currentConnection.setWidth(self.model.objectModel.config.connectionLineWidth)
        self._currentConnection.destinationPoint = plug.center()
        self.scene().addItem(self._currentConnection)

    def onPlugMove(self, plug, event):
        newPosition = event.scenePos()
        self._currentConnection.destinationPoint = newPosition

    def onPlugRelease(self, plug, event):
        scene = self.scene()
        if self._currentConnection is not None:
            end = self._currentConnection.path().pointAtPercent(1)
            endItem = self.scene().itemAt(end, QtGui.QTransform())
            # if we're a plugItem then offload the connection handling to the model
            # the model will then call the scene.createConnection via a signal
            # this is so we let the client code determine if the connection is legal

            if isinstance(endItem, Plug):
                endItem = endItem.parentObject()
                if endItem.model.isInput():
                    endItem.model.createConnection(plug.parentObject().model)
                else:
                    plug.parentObject().model.createConnection(endItem.model)
            # could be the side panel, just use the left panel
            elif endItem == scene.panelWidget.leftPanel:
                scene.panelWidget.leftPanel.handleConnectionDrop(plug.parentObject().model)
            elif endItem == scene.panelWidget.rightPanel:
                scene.panelWidget.rightPanel.handleConnectionDrop(plug.parentObject().model)
            scene.removeItem(self._currentConnection)
            self._currentConnection = None
        scene.update()
