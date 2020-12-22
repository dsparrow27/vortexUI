from vortex.ui.graphics.graphnodes import comment
from vortex.ui.graphics.graphnodes import basenode
from zoovendor.Qt import QtCore


class Backdrop(comment.Comment):

    def __init__(self, objectModel, parent=None):
        super(Backdrop, self).__init__(objectModel, parent)
        self.setZValue(-1.2)
        self.itemGroup = None

    def mouseMoveEvent(self, event):
        scene = self.scene()
        items = scene.selectedNodes()
        lastPos = event.lastPos()
        eventPos = event.pos()
        for i in items:
            pos = i.pos() + i.mapToParent(eventPos) - i.mapToParent(lastPos)
            i.setPos(pos)
        for item in scene.collidingItems(self, QtCore.Qt.ContainsItemBoundingRect):
            if not isinstance(item, basenode.QBaseNode):
                continue
            pos = item.pos() + item.mapToParent(eventPos) - item.mapToParent(lastPos)
            item.setPos(pos)
        self.scene().updateAllConnections()
