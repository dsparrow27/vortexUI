from Qt import QtWidgets, QtCore, QtGui

from zoo.libs.pyqt.widgets.graphics import graphicsview
from zoo.libs.pyqt.widgets.graphics import graphicsscene
from vortex.ui.graphics import plugwidget
from vortex.ui.graphics import graphnodes
from zoo.libs.utils import zlogging
from zoo.libs.pyqt.widgets.graphics import graphbackdrop, graphicitems


logger = zlogging.getLogger(__name__)


class Scene(graphicsscene.GraphicsScene):
    def __init__(self, graph, *args, **kwargs):
        super(Scene, self).__init__(*args, **kwargs)
        self.graph = graph
        self.nodes = {}
        self.connections = set()
        self.selectionChanged.connect(self._onSelectionChanged)

    def _onSelectionChanged(self):
        models = []
        for i in self.nodes.values():
            item = i["qitem"]
            try:
                item.model.setSelected(item.isSelected())
                models.append(item.model)
            except RuntimeError:
                pass
        if models:
            try:
                self.graph.application.events.uiSelectionChanged.emit(models)
            except RuntimeError:
                pass

    def selectedNodes(self):
        return [i["qitem"] for i in self.nodes.values() if i["qitem"].isSelected()]

    def selectionConnections(self):
        return [i["qitem"] for i in self.connections if i["qitem"].isSelected()]

    def createNode(self, model):
        if model.isPin():
            graphNode = graphnodes.Pin(model)
        elif model.isComment():
            graphNode = graphnodes.Comment(model)
        elif model.isBackdrop():
            graphNode = graphnodes.Backdrop(model)
        else:
            graphNode = graphnodes.GraphicsNode(model)
        self.addItem(graphNode)
        self.nodes[hash(model)] = {"qitem": graphNode,
                                   "model": model}
        self.graph.application.events.uiNodesCreated.emit([model])
        return graphNode

    def createNodes(self, objectModels):
        for model in objectModels:
            self.createNode(model)

    def createConnections(self, connections):
        for connection in connections:
            self.createConnectionForModels(*connection)

    def updateAllConnections(self):
        for connection in self.connections:
            connection.updatePosition()

    def connectionsForPlug(self, plug):
        for connection in iter(self.connections):
            source = connection.sourcePlug
            if source == plug or connection.destinationPlug == plug:
                yield connection

    def updateConnectionsForPlug(self, plug):
        for conn in self.connectionsForPlug(plug):
            conn.updatePosition()

    def createConnection(self, source, destination):
        src = source if source.model.isInput() else destination
        dest = destination if destination.model.isOutput() else source
        if src == dest:
            logger.debug("source and destination is the same")
            return
        if not src.model.canAcceptConnection(dest.model):
            return
        newConnection = src.model.createConnection(dest.model)
        if not newConnection:
            return

        newConnection = graphicitems.ConnectionEdge(src.inCircle, dest.outCircle,
                                                    curveType=self.graph.config.defaultConnectionShape,
                                                    colour=src.inCircle.colour)
        newConnection.setLineStyle(self.graph.config.defaultConnectionStyle)
        newConnection.setWidth(self.graph.config.connectionLineWidth)
        newConnection.setZValue(-1)
        newConnection.setCurveType(self.graph.config.defaultConnectionShape)
        self.addItem(newConnection)
        self.connections.add(newConnection)
        return newConnection

    def createConnectionForModels(self, source, destination):
        sourceItem = None
        destinationItem = None
        for hashNode, nodeInfo in self.nodes.items():
            item = nodeInfo["qitem"]
            if isinstance(item, graphnodes.GraphicsNode):
                src = item.attributeItem(source)
                dest = item.attributeItem(destination)
                if src:
                    sourceItem = src
                if dest:
                    destinationItem = dest
                if sourceItem and destinationItem:
                    break
        if sourceItem is not None and destinationItem is not None:
            self.createConnection(sourceItem, destinationItem)

    def deleteNode(self, node):
        """This deletes the given node item from the graphics scene but doesn't call
        model.delete

        :param node:
        :type node:
        :return:
        :rtype:
        """
        key = hash(node)
        if key in self.nodes:
            item = self.nodes[key]["qitem"]
            self.removeItem(item)
            del self.nodes[key]
            return True
        return False

    def deleteConnection(self, connection):
        if connection in self.connections:
            self.connections.remove(connection)
            self.removeItem(connection)
            self.update()
            return True
        return False

    def onDelete(self, selection):
        nodesToDelete = []

        for sel in selection:
            if isinstance(sel, graphicitems.ConnectionEdge):
                if sel.sourcePlug.parentObject().model.deleteConnection(sel.destinationPlug.parentObject().model):
                    self.deleteConnection(sel)
                continue
            elif isinstance(sel, graphnodes.QBaseNode):
                nodesToDelete.append(sel.model)
                deleted = sel.model.delete()
                del self.nodes[hash(sel.model)]
            else:
                continue

            if deleted:
                self.removeItem(sel)

        self.graph.application.events.uiNodesDeleted.emit(nodesToDelete)

    def onSetConnectionStyle(self):
        style = self.sender().text()
        styleValue = self.graph.config.connectionStyles.get(style)
        self.graph.config.defaultConnectionStyle = style
        if styleValue == "Linear":
            for conn in self.connections:
                conn.setAsLinearPath()
        elif styleValue == "Cubic":
            for conn in self.connections:
                conn.setAsCubicPath()
        else:
            for conn in self.connections:
                conn.setLineStyle(styleValue)


class View(graphicsview.GraphicsView):
    requestCopy = QtCore.Signal()
    requestPaste = QtCore.Signal(object)
    nodeDoubleClicked = QtCore.Signal(object)
    requestNodeProperties = QtCore.Signal(object)

    def __init__(self, graph, model, parent=None, setAntialiasing=True):
        super(View, self).__init__(graph.config, parent, setAntialiasing)
        self.application = graph
        self.model = model
        self.newScale = None
        self._plugSelected = None
        self._interactiveEdge = None
        self.pan_active = False
        self.application.setShortcutForWidget(self, "nodeEditor")

    def mouseDoubleClickEvent(self, event):
        # ignore any graphicsitems we don't care about, ie. containers
        items = [i for i in self.items(event.pos()) if not isinstance(i, (graphicitems.ItemContainer,
                                                                          graphnodes.NodeHeader))]
        if not items:
            super(View, self).mouseDoubleClickEvent(event)
            return
        item = items[0]
        modifiers = event.modifiers()
        button = event.buttons()
        model = None
        if isinstance(item, (graphnodes.QBaseNode,)):
            model = item.model
        elif isinstance(item, plugwidget.PlugContainer):
            model = item.model
        elif isinstance(item.parentObject(), graphnodes.QBaseNode):
            item = item.parentObject()
            model = item.model
        if model:
            if button == QtCore.Qt.LeftButton:
                if modifiers == QtCore.Qt.ControlModifier:
                    self.requestNodeProperties.emit(model)
                elif model.isCompound():
                    self.nodeDoubleClicked.emit(model)

        super(View, self).mouseDoubleClickEvent(event)

    def mouseMoveEvent(self, event):
        super(View, self).mouseMoveEvent(event)
        if self._plugSelected:
            if not self._interactiveEdge:
                self.onTempConnectionRequested(self._plugSelected, event)
            else:
                self._interactiveEdge.destinationPoint = self.mapToScene(event.pos())

    def mousePressEvent(self, event):
        button = event.buttons()
        eventPos = event.pos()
        # ignore any graphicsitems we don't care about, ie. containers
        items = [i for i in self.items(eventPos) if not isinstance(i, (graphicitems.ItemContainer,
                                                                       graphnodes.NodeHeader))]
        if button == QtCore.Qt.LeftButton:
            if items:
                item = items[0]
                if isinstance(item, plugwidget.Plug):
                    self._plugSelected = item
                elif isinstance(item, plugwidget.CrossSquare):
                    plug = item.plug()
                    if item.ioType == "input":
                        plug.onExpandInput()
                    else:
                        plug.onExpandOutput()
            else:
                rect = QtCore.QRect(eventPos, QtCore.QSize())
                rect = rect.normalized()
                map_rect = self.mapToScene(rect).boundingRect()
                self.scene().update(map_rect)
                self._rubber_band.setGeometry(rect)
                self._rubber_band.show()

        elif event.button() == QtCore.Qt.MiddleButton and event.modifiers() == QtCore.Qt.AltModifier:
            self.pan_active = True
            self.setCursor(QtCore.Qt.OpenHandCursor)

        elif button == QtCore.Qt.RightButton and items:
            self._contextMenu(event.pos())
        self.parent().nodeLibraryWidget.hide()
        super(View, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):

        if self._plugSelected and not self.pan_active:
            if self._interactiveEdge is not None:
                self.scene().removeItem(self._interactiveEdge)
            self._interactiveEdge = None
            # ignore any graphicsitems we don't care about, ie. containers
            items = [i for i in self.items(event.pos()) if not isinstance(i, (graphicitems.ItemContainer,
                                                                              graphnodes.NodeHeader))]
            if items:
                item = items[0]
                if isinstance(item, plugwidget.Plug):
                    self.scene().createConnection(self._plugSelected.container(), item.container())
            self._plugSelected = None
            return super(View, self).mouseReleaseEvent(event)

        selectedItems = self.scene().selectedNodes()
        for selItem in selectedItems:
            items = selItem.collidingItems(QtCore.Qt.ContainsItemShape)
            if items:
                parentItem = [i for i in items if isinstance(i, graphbackdrop.BackDrop)]
                if not parentItem:
                    selItem.setParentItem(None)
                    continue
                if parentItem[0] == selItem:
                    continue
                selItem.setParentItem(parentItem[0])
            elif selItem.parentItem():
                selItem.setParentItem(None)
        super(View, self).mouseReleaseEvent(event)

    def onTempConnectionRequested(self, plug, event):
        """Trigger when either the inCircle or outCircle is clicked, this method will handle setup of the connection
        object and appropriately call the attributeModel.

        :param plug: Plug class
        :type plug: ::class:`Plug`
        :param event:
        :type event: ::class:`QEvent`
        :return:
        :rtype:
        """
        plug.colour = plug.parentObject().model.backgroundColour()
        self._interactiveEdge = graphicitems.InteractiveEdge(plug,
                                                             curveType=self.config.defaultConnectionShape,
                                                             colour=plug.colour)
        self._interactiveEdge.destinationPoint = plug.center()
        self._interactiveEdge.setLineStyle(self.config.defaultConnectionStyle)
        self._interactiveEdge.setWidth(self.config.connectionLineWidth)
        self._interactiveEdge.setCurveType(self.config.defaultConnectionShape)
        self.scene().addItem(self._interactiveEdge)

    def itemsFromPos(self, pos):
        return [i for i in self.items(pos) if not isinstance(i, (graphicitems.ItemContainer,
                                                                 graphnodes.NodeHeader))]
