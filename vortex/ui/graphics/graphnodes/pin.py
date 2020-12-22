from zoovendor.Qt import QtGui, QtCore
from vortex.ui.graphics.graphnodes import basenode


class Pin(basenode.QBaseNode):
    def __init__(self, objectModel, parent=None):
        super(Pin, self).__init__(objectModel, parent)
        self.init()

    def boundingRect(self):
        return QtCore.QRect(0, 0, 15, 15)

    def paint(self, painter, option, widget):
        rect = self.boundingRect()

        thickness = self.model.edgeThickness()
        if self.isSelected():
            standardPen = QtGui.QPen(self.model.selectedNodeColour(), thickness + 1)
        else:
            standardPen = QtGui.QPen(self.model.edgeColour(), thickness)
        painter.setBrush(self.model.backgroundColour().lighter(150))
        painter.setPen(standardPen)
        painter.drawEllipse(rect)

        super(Pin, self).paint(painter, option, widget)
