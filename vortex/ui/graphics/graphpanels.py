from qt import QtWidgets, QtCore, QtGui
from zoo.libs.pyqt.widgets.graphics import graphicitems
from vortex.ui.graphics import plugwidget


class Panel(QtWidgets.QGraphicsWidget):
    color = QtGui.QColor(0.0, 0.0, 0.0, 125)

    def __init__(self, maximumWidth=99999, parent=None):
        super(Panel, self).__init__(parent=parent)

        layout = QtWidgets.QGraphicsLinearLayout(parent=self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(1)
        layout.setOrientation(QtCore.Qt.Vertical)

        self.attributeContainer = graphicitems.ItemContainer(parent=self)
        layout.addItem(self.attributeContainer)
        self.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding))

        self.setMinimumWidth(maximumWidth)
        self.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.RightButton:
            self._contextMenu(QtCore.QPoint(event.pos().x(), event.pos().y()))
            return
        super(Panel, self).mousePressEvent(event)

    def _contextMenu(self, pos):
        menu = QtWidgets.QMenu()
        menu.addAction("addAttribute")
        menu.exec_(pos)

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
