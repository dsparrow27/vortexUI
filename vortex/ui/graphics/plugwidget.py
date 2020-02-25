from zoo.libs.pyqt.widgets.graphics import graphicitems
from Qt import QtWidgets, QtCore, QtGui


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
        self.ioType = ioType
        self.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed))
        self.setPreferredSize(size)
        self.setWindowFrameMargins(0, 0, 0, 0)
        self._defaultPen = QtGui.QPen(edgeColor, 2.5)
        self._hoverPen = QtGui.QPen(highlightColor, 3.0)
        self._defaultBrush = QtGui.QBrush(color)
        self._currentBrush = QtGui.QBrush(color)
        self.xPos = -5.0 if self.ioType == "Input" else +5.0
        self.setAcceptHoverEvents(True)

    def container(self):
        return self.parentObject()

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
            event.accept()
        elif btn == QtCore.Qt.RightButton:
            event.accept()

    def paint(self, painter, options, widget=None):
        rect = self.boundingRect()
        painter.setBrush(self._currentBrush)

        painter.setPen(self._defaultPen)
        painter.drawEllipse(rect)

    def boundingRect(self):
        return QtCore.QRectF(
            self.xPos,
            0.0,
            self._diameter,
            self._diameter,
        )


class CrossSquare(QtWidgets.QGraphicsWidget):
    leftMouseButtonClicked = QtCore.Signal()
    hoverEventRequested = QtCore.Signal()

    def __init__(self, ioType, parent=None):
        super(CrossSquare, self).__init__(parent)
        size = QtCore.QSizeF(Plug._diameter, Plug._diameter)
        self.ioType = ioType
        self.expanded = False
        self.isElement = False
        self.isChild = False
        self.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed))
        self.setPreferredSize(size)
        self.setWindowFrameMargins(0, 0, 0, 0)
        self.hide()
        self.lines = [QtCore.QLineF(QtCore.QPoint(Plug._diameter * 0.5, 3.0),
                                    QtCore.QPoint(Plug._diameter * 0.5, Plug._diameter - 3.0)),
                      QtCore.QLineF(QtCore.QPoint(3.0, Plug._diameter * 0.5),
                                    QtCore.QPoint(Plug._diameter - 3.0, Plug._diameter * 0.5))
                      ]

    def plug(self):
        return self.parentObject()

    #
    def mousePressEvent(self, event):
        btn = event.button()
        if btn == QtCore.Qt.LeftButton and not self.isElement or not self.isChild:
            event.accept()

    def mouseHoverEvent(self, event):
        super(CrossSquare, self).mouseHoverEvent(event)
        self.hoverEventRequested.emit()

    def paint(self, painter, options, widget=None):
        painter.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255, 255), 0.3))
        # draw the square
        if self.isElement or self.isChild:
            parentHeight = self.parentObject().size().height()
            lines = [QtCore.QLineF(QtCore.QPoint(Plug._diameter * 0.5, Plug._diameter * 0.5),
                                   QtCore.QPoint(Plug._diameter * 0.5, -parentHeight)),
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
            Plug._diameter,
            Plug._diameter,
        )


class PlugContainer(graphicitems.ItemContainer):

    def __init__(self, attributeModel, parent=None):
        super(PlugContainer, self).__init__(QtCore.Qt.Horizontal, parent)
        self.model = attributeModel
        self.childContainers = []
        self.inCrossItem = CrossSquare(ioType="input", parent=self)
        self.outCrossItem = CrossSquare(ioType="output", parent=self)
        self.inCrossItem.hoverEventRequested.connect(self.onExpandInput)
        self.outCrossItem.hoverEventRequested.connect(self.onExpandOutput)
        self.inCircle = Plug(self.model.itemColour(),
                             self.model.itemEdgeColor(),
                             self.model.highlightColor(), "Input",
                             parent=self)
        self.outCircle = Plug(self.model.itemColour(),
                              self.model.itemEdgeColor(),
                              self.model.highlightColor(), "Output",
                              parent=self)
        self.inCircle.setToolTip(attributeModel.toolTip())
        self.outCircle.setToolTip(attributeModel.toolTip())

        self.label = graphicitems.GraphicsText(self.model.text(), parent=self)
        self.label.text.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
        self.label.color = attributeModel.textColour() or QtGui.QColor(200, 200, 200)
        self.label.allowHoverHighlight = True

        if not attributeModel.isOutput():
            self.outCircle.hide()
        if not attributeModel.isInput():
            self.inCircle.hide()
        self.addItem(self.inCircle, QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.addItem(self.inCrossItem, QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.addItem(self.label, attributeModel.textAlignment())
        self.addItem(self.outCrossItem, QtCore.Qt.AlignVCenter)
        self.addItem(self.outCircle, QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

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

    def expand(self):
        parentContainer = self.parentObject()
        if self.model.isArray():
            children = reversed(self.model.elements())
        else:
            children = reversed(self.model.children())
        if not children:
            return
        selfIndex = parentContainer.indexOf(self) + 1
        isElement = self.model.isElement()
        isChild = self.model.isChild()
        for element in children:
            elementContainer = PlugContainer(attributeModel=element, parent=self)
            elementContainer.inCrossItem.isElement = isElement
            elementContainer.inCrossItem.isChild = isChild
            elementContainer.outCrossItem.isElement = isElement
            elementContainer.outCrossItem.isChild = isChild
            parentContainer.insertItem(selfIndex, elementContainer)
            self.childContainers.append(elementContainer)
            if element.isInput():
                index = elementContainer.layout().count() - 2
                if element.isArray() or element.isCompound() or element.isElement() or element.isChild():
                    elementContainer.inCrossItem.show()
            else:
                if element.isArray() or element.isCompound() or element.isElement() or element.isChild():
                    elementContainer.outCrossItem.show()
                index = 2
            elementContainer.layout().insertStretch(index, 1)

    def onExpandInput(self):
        parentContainer = self.parentObject()
        if self.inCrossItem.expanded:
            removeChildContainers(self, parentContainer)
        else:
            self.expand()
        self.inCrossItem.expanded = not self.inCrossItem.expanded
        self.update()

    def onExpandOutput(self):
        parentContainer = self.parentObject()
        if self.outCrossItem.expanded:
            removeChildContainers(self, parentContainer)
            self._removeChildContainers(parentContainer)
            return
        else:
            self.expand()
        self.outCrossItem.expanded = not self.outCrossItem.expanded
        self.update()


def removeChildContainers(plugContainer, parentContainer):
    for container in plugContainer.childContainers:
        parentContainer.removeItem(container)
    plugContainer.childContainers = []
