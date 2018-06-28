from qt import QtGui, QtCore, QtWidgets


class ConnectionEdge(QtWidgets.QGraphicsPathItem):
    """Class to deal with the Connection path between two plugs
    You set the style of the path with setLineStyle(QtCore.Qt.Style)
    """
    contextMenuRequested = QtCore.Signal(object)
    defaultColor = QtGui.QColor(138, 200, 0)
    selectedColor = QtGui.QColor(255, 255, 255)
    hoverColor = QtGui.QColor(255, 255, 255)
    CUBIC = 0
    LINEAR = 1

    def __init__(self, source, destination=None, curveType=CUBIC):
        super(ConnectionEdge, self).__init__()
        self.curveType = curveType
        self._sourcePlug = source
        self._destinationPlug = destination
        self._sourcePoint = source.center()
        self._destinationPoint = destination.center() if destination is not None else None
        self.defaultPen = QtGui.QPen(source.color, 1.25, style=QtCore.Qt.DashLine)
        self.defaultPen.setDashPattern([1, 2, 2, 1])
        self.selectedPen = QtGui.QPen(self.selectedColor, 1.7, style=QtCore.Qt.DashLine)
        self.selectedPen.setDashPattern([1, 2, 2, 1])

        self.hoverPen = QtGui.QPen(self.hoverColor, 1.7, style=QtCore.Qt.DashLine)
        self.selectedPen.setDashPattern([1, 2, 2, 1])
        self.hovering = False

        self.setPen(self.defaultPen)
        self.setZValue(-1)
        self.setFlags(self.ItemIsFocusable | self.ItemIsSelectable | self.ItemIsMovable)
        # if self._sourcePlug and self._destinationPlug:
        #     self.connect(self._sourcePlug, self._destinationPlug)
        self.update()

    def setLineStyle(self, qStyle):
        self.defaultPen.setStyle(qStyle)
        self.selectedPen.setStyle(qStyle)
        self.hoverPen.setStyle(qStyle)

    def setAsLinearPath(self):
        path = QtGui.QPainterPath()
        path.moveTo(self._sourcePoint)
        path.lineTo(self._destinationPoint)
        self.curveType = ConnectionEdge.LINEAR
        self.setPath(path)

    def setAsCubicPath(self):
        path = QtGui.QPainterPath()

        path.moveTo(self._sourcePoint)
        dx = self._destinationPoint.x() - self._sourcePoint.x()
        dy = self._destinationPoint.y() - self._sourcePoint.y()
        ctrl1 = QtCore.QPointF(self._sourcePoint.x() + dx * 0.50, self._sourcePoint.y() + dy * 0.1)
        ctrl2 = QtCore.QPointF(self._sourcePoint.x() + dx * 0.50, self._sourcePoint.y() + dy * 0.9)
        path.cubicTo(ctrl1, ctrl2, self._destinationPoint)
        self.curveType = ConnectionEdge.CUBIC
        self.setPath(path)

    def hoverLeaveEvent(self, event):
        super(ConnectionEdge, self).hoverEnterEvent(event)
        self.hovering = False
        self.update()

    def hoverEnterEvent(self, event):
        super(ConnectionEdge, self).hoverEnterEvent(event)
        self.hovering = True
        self.update()

    def paint(self, painter, option, widget):

        if self.isSelected():
            painter.setPen(self.selectedPen)
        elif self.hovering:
            painter.setPen(self.hoverPen)
        else:
            painter.setPen(self.defaultPen)
        painter.drawPath(self.path())

    def updatePosition(self):
        """Update the position of the start and end of the edge
        """
        self._destinationPoint = self.destinationPlug.center()
        self._sourcePoint = self.sourcePlug.center()
        self.updatePath()

    def updatePath(self):
        if self.curveType == ConnectionEdge.CUBIC:
            self.setAsCubicPath()
        else:
            self.setAsLinearPath()

    def connect(self, src, dest):
        """Create a connection between the src plug and the destination plug
        :param src: Plug
        :param dest: Plug
        :return: None
        """
        if not src and dest:
            return
        self._sourcePlug = src
        self._destinationPlug = dest
        src.addConnection(self)
        dest.addConnection(self)

    def disconnect(self):
        """Remove the connection between the source and destination plug
        """
        self._sourcePlug.removeConnection(self)
        self._destinationPlug.removeConnection(self)
        self._sourcePlug = None
        self._destinationPlug = None

    @property
    def sourcePoint(self):
        """Return the source point
        :return: QtCore.QPointF()
        """
        return self._sourcePoint

    @sourcePoint.setter
    def sourcePoint(self, point):
        """Sets the source point and updates the path
        :param point: QtCore.QPointF
        """
        self._sourcePoint = point
        self.updatePath()

    @property
    def destinationPoint(self):
        """return the destination point
        :return: QtCore.QPointF
        """
        return self._destinationPoint

    @destinationPoint.setter
    def destinationPoint(self, point):
        """Sets the destination point and updates the path
        :param point: QtCore.QPointF
        """
        self._destinationPoint = point
        self.updatePath()

    @property
    def sourcePlug(self):
        """Return the source plug
        :return: Plug
        """
        return self._sourcePlug

    @sourcePlug.setter
    def sourcePlug(self, plug):
        """Sets the source plug and update the path
        :param plug: Plug
        """
        self._sourcePlug = plug
        self._sourcePoint = plug.center()
        self._sourcePlug.parentObject().connections.add(plug)
        self.updatePath()

    @property
    def destinationPlug(self):
        """Returns the destination plug
        :return: Plug
        """
        return self._destinationPlug

    @destinationPlug.setter
    def destinationPlug(self, plug):
        self._destinationPlug = plug
        self._destinationPoint = plug.center()
        self._destinationPlug.parentObject().connections.add(self)
        self.updatePath()

    def close(self):
        """
        """
        if self.scene() is not None:
            self.scene().removeItem(self)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            event.accept()
            if self.isSelected():
                self.setSelected(False)
            else:
                self.setSelected(True)

            self.update()
        self._destinationPoint = event.pos()

    def mouseMoveEvent(self, event):
        self._destinationPoint = self.mapToScene(event.pos())

    def contextMenuEvent(self, event):
        menu = QtWidgets.QMenu(self)

        self.contextMenuRequested.emit(menu)
        menu.exec_(event.scenePos())
        event.setAccepted(True)
