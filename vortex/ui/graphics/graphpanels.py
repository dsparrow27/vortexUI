from qt import QtWidgets, QtCore, QtGui
from zoo.libs.pyqt.widgets.graphics import graphicitems
from vortex.ui.graphics import plugwidget


class PanelWidget(QtWidgets.QGraphicsWidget):
    def __init__(self, application, acceptsContextMenu=True, parent=None):
        super(PanelWidget, self).__init__(parent=parent)
        self.setFlag(self.ItemSendsScenePositionChanges)
        self.setFlag(self.ItemIgnoresTransformations)
        self.application = application
        self.leftPanel = Panel(self.application, ioType="Input", acceptsContextMenu=acceptsContextMenu)
        self.rightPanel = Panel(self.application, ioType="Output", acceptsContextMenu=acceptsContextMenu)
        self.leftPanel.setMaximumWidth(application.config.panelWidth)
        self.rightPanel.setMaximumWidth(application.config.panelWidth)
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

    def __init__(self, application, ioType, acceptsContextMenu=False, parent=None):
        super(Panel, self).__init__(parent=parent)
        self.application = application
        self.ioType = ioType
        self.model = application.currentModel
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
        self.setZValue(1000)
        self.refresh()

    def refresh(self):
        currentModel = self.application.currentModel
        if currentModel is None:
            return
        self.attributeContainer.clear()
        for attr in currentModel.attributes(self.ioType == "Input", self.ioType == "Output"):
            self.addAttribute(attr)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.RightButton and self.acceptsContextMenu:
            self._contextMenu(QtGui.QCursor.pos())
            return
        super(Panel, self).mousePressEvent(event)

    def addAttribute(self, attribute):
        plug = plugwidget.PlugContainer(attribute, parent=self.attributeContainer)

        # todo: flip the alignment of the text
        if attribute.isInput():
            plug.outCircle.show()
            plug.inCircle.hide()
        else:
            plug.inCircle.show()
            plug.outCircle.hide()
        self.attributeContainer.addItem(plug)

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
