import os

from zoo.libs.pyqt.widgets.graphics import graphicitems
from Qt import QtWidgets, QtCore, QtGui


class PlugContainer(graphicitems.ItemContainer):
    expandedSig = QtCore.Signal()

    def __init__(self, attributeModel, parent=None):
        super(PlugContainer, self).__init__(QtCore.Qt.Horizontal, parent)
        self.model = attributeModel
        self.childContainers = []
        self.inCrossItem = CrossSquare(ioType=Plug.INPUT_TYPE, parent=self)
        self.outCrossItem = CrossSquare(ioType=Plug.OUTPUT_TYPE, parent=self)
        self.inCrossItem.hoverEventRequested.connect(self.onExpandInput)
        self.outCrossItem.hoverEventRequested.connect(self.onExpandOutput)
        self.inCircle = InputPlug(self.model.backgroundColour(),
                                  self.model.edgeColour(),
                                  self.model.highlightColour(),
                                  parent=self)
        self.outCircle = OutputPlug(self.model.backgroundColour(),
                                    self.model.edgeColour(),
                                    self.model.highlightColour(),
                                    parent=self)
        self.inCircle.setToolTip(attributeModel.toolTip())
        self.outCircle.setToolTip(attributeModel.toolTip())

        self.label = graphicitems.GraphicsText(self.model.text(), parent=self)
        self.label.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
        self.label.colour = attributeModel.textColour()
        self.label.allowHoverHighlight = True
        self.addItems()

    def addItems(self):
        """This method allows for overloading the layout of the items
        """
        self.addItem(self.inCircle, QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.addItem(self.inCrossItem, QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.addItem(self.label, self.model.textAlignment())
        self.addItem(self.outCrossItem, QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.addItem(self.outCircle, QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

        if not self.model.isOutput():
            self.outCircle.hide()
        else:
            if self.model.isArray() or self.model.isCompound() or self.model.isChild() or self.model.isElement():
                self.outCrossItem.show()
        if not self.model.isInput():
            self.inCircle.hide()
        else:
            if self.model.isArray() or self.model.isCompound() or self.model.isChild() or self.model.isElement():
                self.inCrossItem.show()

    def setLabel(self, label):
        self.label.setText(label)

    def inputPlug(self):
        return self.inCircle

    def outputPlug(self):
        return self.outCircle

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
        self.prepareGeometryChange()
        selfIndex = parentContainer.indexOf(self) + 1
        for element in children:
            self.createChildContainer(element, selfIndex, parentContainer)

    def createChildContainer(self, child, parentIndex, parentContainer):
        elementContainer = PlugContainer(attributeModel=child, parent=self)
        elementContainer.inCrossItem.isElement = child.isElement()
        elementContainer.inCrossItem.isChild = child.isChild()
        elementContainer.inCrossItem.hasChildren = child.hasChildren()
        elementContainer.outCrossItem.isElement = child.isElement()
        elementContainer.outCrossItem.isChild = child.isChild()
        elementContainer.outCrossItem.hasChildren = child.hasChildren()
        parentContainer.insertItem(parentIndex, elementContainer)
        elementContainer.expandedSig.connect(self.expandedSig.emit)
        self.childContainers.append(elementContainer)
        if child.isInput():
            index = elementContainer.layout().count() - 2
            if child.isArray() or child.isCompound():
                elementContainer.inCrossItem.show()
        else:
            if child.isArray() or child.isCompound():
                elementContainer.outCrossItem.show()
            index = 2
        elementContainer.layout().insertStretch(index, 1)

    def onExpandInput(self):
        parentContainer = self.parentObject()
        # todo handle connections
        if self.inCrossItem.expanded:
            removeChildContainers(self, parentContainer)
        else:
            self.expand()
        self.inCrossItem.expanded = not self.inCrossItem.expanded
        self.expandedSig.emit()

    def onExpandOutput(self):
        parentContainer = self.parentObject()
        # todo handle connections
        if self.outCrossItem.expanded:
            removeChildContainers(self, parentContainer)
        else:
            self.expand()
        self.outCrossItem.expanded = not self.outCrossItem.expanded
        self.expandedSig.emit()

    if os.environ.get("DEBUG", "0") == "1":
        def paint(self, painter, option, widget):
            painter.setBrush(QtCore.Qt.NoBrush)
            painter.setPen(QtGui.QPen(QtCore.Qt.blue, 0.75))
            painter.drawRect(self.geometry())
            super(PlugContainer, self).paint(painter, option, widget)


class CompoundAttributeInputContainer(PlugContainer):
    """Specialized Plug container for compound where the order of child items need to be reversed.

    Output Order: Plug->crosshair->Text
    Input Order: Text->crosshair->Plug
    """

    def addItems(self):
        if self.model.isChild() or self.model.isElement():
            self.addItem(self.inCircle, QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
            self.addItem(self.inCrossItem, QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
            self.layout().addStretch(1)
            self.addItem(self.label, self.model.textAlignment())
            self.addItem(self.outCrossItem, QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            self.addItem(self.outCircle, QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            showCross = True
        else:
            self.addItem(self.inCircle, QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
            self.addItem(self.inCrossItem, QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
            self.layout().addStretch(1)
            self.addItem(self.label, self.model.textAlignment())
            self.addItem(self.outCrossItem, QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            self.addItem(self.outCircle, QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            showCross = False

        self.inCircle.hide()
        self.inCrossItem.hide()
        if self.model.isArray() or self.model.isCompound() or showCross:
            self.outCrossItem.show()
        else:
            self.outCrossItem.hide()

    def createChildContainer(self, child, parentIndex, parentContainer):
        elementContainer = CompoundAttributeInputContainer(attributeModel=child, parent=self)
        elementContainer.inCrossItem.isChild = child.isChild()
        self.childContainers.append(elementContainer)
        parentContainer.insertItem(parentIndex, elementContainer)
        elementContainer.inCrossItem.isElement = child.isElement()
        elementContainer.inCrossItem.hasChildren = child.hasChildren()
        elementContainer.inCrossItem.isChild = child.isChild()
        elementContainer.outCrossItem.isElement = child.isElement()
        elementContainer.outCrossItem.isChild = child.isChild()
        elementContainer.outCrossItem.hasChildren = child.hasChildren()
        elementContainer.expandedSig.connect(self.expandedSig.emit)


class CompoundAttributeOutputContainer(PlugContainer):
    def addItems(self):
        if self.model.isChild() or self.model.isElement():
            self.addItem(self.inCircle, QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
            self.addItem(self.inCrossItem, QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
            self.addItem(self.label, self.model.textAlignment())
            self.layout().addStretch(1)
            self.addItem(self.outCrossItem, QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            self.addItem(self.outCircle, QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            showCross = True
        else:
            self.addItem(self.inCircle, QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
            self.addItem(self.inCrossItem, QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
            self.addItem(self.label, self.model.textAlignment())
            self.layout().addStretch(1)
            self.addItem(self.outCrossItem, QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            self.addItem(self.outCircle, QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            showCross = False

        if self.model.isArray() or self.model.isCompound() or showCross:
            self.inCrossItem.show()
        else:
            self.inCrossItem.hide()
        self.outCircle.hide()
        self.outCrossItem.hide()

    def createChildContainer(self, child, parentIndex, parentContainer):
        elementContainer = CompoundAttributeOutputContainer(attributeModel=child, parent=self)
        elementContainer.inCrossItem.isChild = child.isChild()
        self.childContainers.append(elementContainer)
        parentContainer.insertItem(parentIndex, elementContainer)
        elementContainer.inCrossItem.isElement = child.isElement()
        elementContainer.inCrossItem.hasChildren = child.hasChildren()
        elementContainer.inCrossItem.isChild = child.isChild()
        elementContainer.outCrossItem.isElement = child.isElement()
        elementContainer.outCrossItem.isChild = child.isChild()
        elementContainer.outCrossItem.hasChildren = child.hasChildren()
        elementContainer.expandedSig.connect(self.expandedSig.emit)


class Plug(QtWidgets.QGraphicsWidget):
    _diameter = 2 * 6
    INPUT_TYPE = 0
    OUTPUT_TYPE = 1
    ioType = ""
    xPos = 0

    def __init__(self, colour, edgeColour, highlightColour, parent=None):
        super(Plug, self).__init__(parent=parent)
        self.setAcceptHoverEvents(True)
        size = QtCore.QSizeF(self._diameter, self._diameter)
        self.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed))
        self.setPreferredSize(size)
        self._defaultPen = QtGui.QPen(edgeColour, 2.5)
        self._hoverPen = QtGui.QPen(highlightColour, 3.0)
        self._defaultBrush = QtGui.QBrush(colour)
        self._currentBrush = QtGui.QBrush(colour)
        self.setPos(self.xPos, 0)

    def container(self):
        return self.parentObject()

    @property
    def colour(self):
        return self._currentBrush.color()

    @colour.setter
    def colour(self, colour):
        self._currentBrush = QtGui.QBrush(colour)
        self.update()

    def highlight(self):
        self._currentBrush = QtGui.QBrush(self.colour.lighter())

    def unhighlight(self):
        self._currentBrush = QtGui.QBrush(self._defaultBrush)
        self.update()

    def center(self):
        for view in self.scene().views():
            rect = self.boundingRect()
            transform = self.deviceTransform(view.viewportTransform())
            return view.mapToScene(transform.m31() + rect.width() * 0.5, transform.m32() + rect.height() * 0.5)

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

    if os.environ.get("DEBUG", "0") == "1":
        def paint(self, painter, option, widget):
            painter.setBrush(QtCore.Qt.NoBrush)
            painter.setPen(QtGui.QPen(QtCore.Qt.red, 0.75))
            painter.drawRect(self.geometry())
            super(Plug, self).paint(painter, option, widget)
    else:
        def paint(self, painter, options, widget=None):
            rect = self.boundingRect()
            painter.setBrush(self._currentBrush)

            painter.setPen(self._defaultPen)
            painter.drawEllipse(rect)
            super(Plug, self).paint(painter, options, widget)

    def geometry(self):
        return self.boundingRect()

    def boundingRect(self):
        return QtCore.QRectF(
            0.0,
            0.0,
            self._diameter,
            self._diameter,
        )


class InputPlug(Plug):
    ioType = Plug.INPUT_TYPE
    xPos = 5.0


class OutputPlug(Plug):
    ioType = Plug.OUTPUT_TYPE
    xPos = -5.0


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
        self.hasChildren = False
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
        if (self.isElement or self.isChild) and not self.hasChildren:
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
        super(CrossSquare, self).paint(painter, options, widget)

    def boundingRect(self):
        return QtCore.QRectF(
            0,
            0,
            Plug._diameter,
            Plug._diameter,
        )


def removeChildContainers(plugContainer, parentContainer):
    for container in plugContainer.childContainers:
        removeChildContainers(container, parentContainer)
        parentContainer.removeItem(container)
    plugContainer.childContainers = []
