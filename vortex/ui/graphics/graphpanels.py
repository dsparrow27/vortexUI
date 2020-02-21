from Qt import QtWidgets, QtCore, QtGui
from zoo.libs.pyqt.widgets.graphics import graphicitems
from vortex.ui.graphics import plugwidget


class PanelWidget(QtWidgets.QGraphicsWidget):
    def __init__(self, model, acceptsContextMenu=True, parent=None):
        super(PanelWidget, self).__init__(parent=parent)
        self.setFlag(self.ItemSendsScenePositionChanges)
        self.setFlag(self.ItemIgnoresTransformations)
        self.model = model
        self.leftPanel = Panel(model, ioType="Input", acceptsContextMenu=acceptsContextMenu)
        self.rightPanel = Panel(model, ioType="Output", acceptsContextMenu=acceptsContextMenu)
        self.leftPanel.setMaximumWidth(model.config.panelWidth)
        self.rightPanel.setMaximumWidth(model.config.panelWidth)
        layout = QtWidgets.QGraphicsLinearLayout(parent=self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setOrientation(QtCore.Qt.Horizontal)
        layout.addItem(self.leftPanel)
        layout.addStretch(1)
        layout.addItem(self.rightPanel)
        self.setLayout(layout)


class Panel(QtWidgets.QGraphicsWidget):
    color = QtGui.QColor(0.0, 0.0, 0.0, 125)

    def __init__(self, objectModel, ioType, acceptsContextMenu=False, parent=None):
        super(Panel, self).__init__(parent=parent)
        self.model = objectModel
        self.ioType = ioType
        layout = QtWidgets.QGraphicsLinearLayout(parent=self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(1)
        layout.setOrientation(QtCore.Qt.Vertical)
        self.attributeContainer = graphicitems.ItemContainer(parent=self)
        layout.addItem(self.attributeContainer)
        self.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))
        self.acceptsContextMenu = acceptsContextMenu

        self.setLayout(layout)
        self.setFlags(self.flags() & QtCore.Qt.ItemIsSelectable)
        self.setZValue(100)
        self.refresh()

    def refresh(self):
        currentModel = self.model
        if currentModel is None:
            return
        self.attributeContainer.clear()
        for attr in currentModel.attributes(self.ioType == "Input", self.ioType == "Output",
                                            3):
            self.addAttribute(attr)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.RightButton and self.acceptsContextMenu:
            self._contextMenu(QtGui.QCursor.pos())
            return
        super(Panel, self).mousePressEvent(event)

    def addAttribute(self, attribute):
        plug = plugwidget.PlugContainer(attribute, parent=self.attributeContainer)
        layout = plug.layout()
        if attribute.isInput() and self.ioType == "Input":
            if attribute.isArray() or attribute.isCompound():
                plug.inCrossItem.show()
            plug.inCircle.show()
            plug.outCircle.hide()
        #     # insert the inCircle to the far right
            layout.insertItem(3, plug.inCircle)
            layout.insertItem(2, plug.inCrossItem)
            # we switch this around for panels because the model input would be connected to another input
            # making it difficult to which is the start point and end point of a connection
            plug.inCircle.ioType = "Output"
            layout.insertStretch(2, 1)
        else:
            if attribute.isArray() or attribute.isCompound():
                plug.outCrossItem.show()
            plug.outCircle.show()
            plug.inCircle.hide()
        #     # insert the outCircle to the far left
            layout.insertItem(0, plug.outCircle)
            layout.insertItem(1, plug.outCrossItem)
            layout.itemAt(layout.count()-1)
            plug.inCircle.ioType = "Input"
            plug.setTextAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

        # swap the layout alignment
        plug.setInputAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        plug.layout().setAlignment(plug.inCrossItem, QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        plug.layout().setAlignment(plug.outCrossItem, QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        plug.setOutputAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.attributeContainer.addItem(plug)

    def attributeItem(self, attributeModel):
        for attr in iter(self.attributeContainer.items()):
            if attr.model == attributeModel:
                return attr

    def paint(self, painter, option, widget):
        rect = self.windowFrameRect()
        painter.fillRect(rect, self.color)
        painter.setPen(QtGui.QPen(self.color, 3))
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