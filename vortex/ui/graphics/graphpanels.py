from qt import QtWidgets, QtCore, QtGui
from zoo.libs.pyqt.widgets.graphics import graphicitems
from vortex.ui.graphics import plugwidget


class Panel(QtWidgets.QGraphicsWidget):
    color = QtGui.QColor(0.0, 0.0, 0.0, 125)


    def __init__(self, acceptsContextMenu=False, parent=None):
        super(Panel, self).__init__(parent=parent)

        layout = QtWidgets.QGraphicsLinearLayout(parent=self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(1)
        layout.setOrientation(QtCore.Qt.Vertical)

        self.attributeContainer = graphicitems.ItemContainer(parent=self)
        layout.addItem(self.attributeContainer)
        self.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding))
        self.acceptsContextMenu = acceptsContextMenu
        self.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        self.setFlags(self.flags() & QtCore.Qt.ItemIsSelectable)
        self.setZValue(1000)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.RightButton and self.acceptsContextMenu:
            self._contextMenu(QtGui.QCursor.pos())
            return
        super(Panel, self).mousePressEvent(event)

    def addAttribute(self, attribute):
        plug = plugwidget.PlugContainer(attribute, parent=self.attributeContainer)
        if attribute.isInput():
            plug.setInputAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        else:
            plug.setOutputAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.attributeContainer.addItem(plug)

    def paint(self, painter, option, widget):
        rect = self.windowFrameRect()
        painter.fillRect(rect, self.color)
        painter.setPen(QtGui.QPen(self.color, 3))
        super(Panel, self).paint(painter, option, widget)
