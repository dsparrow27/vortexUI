import os

from Qt import QtWidgets, QtCore, QtGui
from zoo.libs.pyqt.widgets.graphics import graphicitems
from zoo.libs.pyqt.widgets import elements
from vortex.ui.graphics import plugwidget


class PanelWidget(QtWidgets.QGraphicsWidget):
    leftPanelDoubleClicked = QtCore.Signal(str)
    rightPanelDoubleClicked = QtCore.Signal(str)

    def __init__(self, model, acceptsContextMenu=True, parent=None):
        super(PanelWidget, self).__init__(parent=parent)
        self.setFlags(self.ItemIgnoresTransformations)
        self.setAcceptedMouseButtons(QtCore.Qt.NoButton)
        self.setZValue(1)
        self.leftPanel = Panel(ioType=plugwidget.Plug.INPUT_TYPE, acceptsContextMenu=acceptsContextMenu,
                               parent=self)
        self.rightPanel = Panel(ioType=plugwidget.Plug.OUTPUT_TYPE, acceptsContextMenu=acceptsContextMenu,
                                parent=self)
        self.leftPanel.setMaximumWidth(model.config.panelWidth)
        self.rightPanel.setMaximumWidth(model.config.panelWidth)
        layout = elements.hGraphicsLinearLayout(parent=self)
        layout.addItem(self.leftPanel)
        layout.addStretch(1)
        layout.addItem(self.rightPanel)
        self.setZValue(100)
        self.setLayout(layout)
        self.leftPanel.doubleClicked.connect(self.leftPanelDoubleClicked)
        self.rightPanel.doubleClicked.connect(self.rightPanelDoubleClicked)

    def refresh(self):
        self.leftPanel.refresh()
        self.rightPanel.refresh()

    def geometry(self):
        return self.boundingRect()

    def boundingRect(self):
        for view in self.scene().views():
            return view.viewport().rect()

    if os.environ.get("DEBUG", "0") == "1":
        def paint(self, painter, option, widget):
            painter.setBrush(QtCore.Qt.NoBrush)
            painter.setPen(QtGui.QPen(QtCore.Qt.green, 0.75))
            painter.drawRect(self.geometry())
            super(PanelWidget, self).paint(painter, option, widget)


class Panel(QtWidgets.QGraphicsWidget):
    doubleClicked = QtCore.Signal(str)

    color = QtGui.QColor(20, 20, 20, 125)

    def __init__(self, ioType, acceptsContextMenu=False, parent=None):
        super(Panel, self).__init__(parent=parent)
        self.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))
        self.acceptsContextMenu = acceptsContextMenu
        self.setAcceptDrops(True)
        self.setZValue(100)
        self.ioType = ioType
        self._layout = graphicitems.layouts.vGraphicsLinearLayout(self)
        self.attributeContainer = graphicitems.ItemContainer(parent=self)
        self._layout.addItem(self.attributeContainer)

    @property
    def model(self):
        return self.scene().model

    def refresh(self):
        currentModel = self.model
        if currentModel is None:
            return
        self.attributeContainer.clear()
        for attr in currentModel.attributes(self.ioType == plugwidget.Plug.INPUT_TYPE,
                                            self.ioType == plugwidget.Plug.OUTPUT_TYPE, 3):
            self.addAttribute(attr)

    def mouseDoubleClickEvent(self, event):
        self.doubleClicked.emit(self.ioType)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.RightButton and self.acceptsContextMenu:
            self._contextMenu(QtGui.QCursor.pos())
            return
        print("click")
        super(Panel, self).mousePressEvent(event)

    def dropEvent(self, event):
        print("drop")
        super(Panel, self).dropEvent(event)

    def wheelEvent(self, event):
        event.accept()
        super(Panel, self).wheelEvent(event)

    def addAttribute(self, attribute):
        if attribute.isInput() and self.ioType == plugwidget.Plug.INPUT_TYPE:
            container = plugwidget.CompoundAttributeInputContainer(attribute, parent=self)
        else:
            container = plugwidget.CompoundAttributeOutputContainer(attribute, parent=self)
        self.attributeContainer.addItem(container)

    def attributeItem(self, attributeModel):
        for attr in iter(self.attributeContainer.items()):
            if attr.model == attributeModel:
                return attr

    def geometry(self):
        return self.boundingRect()

    def boundingRect(self):
        parent = self.parentItem()
        rect = parent.boundingRect()
        if self.ioType == plugwidget.Plug.INPUT_TYPE:
            rect.setWidth(150)
            return rect
        rect.setWidth(150)
        rect.setX(rect.topRight().x() - 150)
        return rect

    if os.environ.get("DEBUG", "0") == "1":
        def paint(self, painter, option, widget):
            rect = self.boundingRect()
            painter.setBrush(QtCore.Qt.NoBrush)
            painter.setPen(QtGui.QPen(QtCore.Qt.green, 0.75))
            painter.fillRect(rect, self.color)
            painter.drawRect(self.geometry())
            super(Panel, self).paint(painter, option, widget)
    else:
        def paint(self, painter, option, widget):
            rect = self.boundingRect()
            painter.fillRect(rect, self.color)
            super(Panel, self).paint(painter, option, widget)

    def _contextMenu(self, pos):
        app = self.scene().uiApplication
        menu = app.createContextMenu(app.currentModel)
        if menu:
            menu.exec_(pos)
            self.refresh()

    def handleConnectionDrop(self, model):
        if not model.objectModel.canCreateAttributes():
            return
        print("drop", self.ioType, model)
