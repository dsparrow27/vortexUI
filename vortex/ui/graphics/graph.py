from Qt import QtWidgets, QtCore, QtGui

from zoo.libs.pyqt.widgets.graphics import graphicsview
from zoo.libs.pyqt.widgets.graphics import graphicsscene
from vortex.ui.graphics import plugwidget
from vortex.ui.graphics import graphnodes


from zoo.libs.pyqt.widgets.graphics import graphbackdrop, graphicitems


class Scene(graphicsscene.GraphicsScene):
    def __init__(self, graph, *args, **kwargs):
        super(Scene, self).__init__(*args, **kwargs)
        self.selectionChanged.connect(self._onSelectionChanged)
        self.uiApplication = graph
        self.nodes = {}
        self.panelWidget = None
        self.connections = set()

    def _onSelectionChanged(self):
        for i in self.nodes.values():
            item = i["qitem"]
            try:
                item.model.setSelected(item.isSelected())
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
        return graphNode

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
        newConnection = graphicitems.ConnectionEdge(source, destination,
                                                    curveType=self.uiApplication.config.defaultConnectionShape,
                                                    colour=source.colour)
        newConnection.setLineStyle(self.uiApplication.config.defaultConnectionStyle)
        newConnection.setWidth(self.uiApplication.config.connectionLineWidth)
        newConnection.setZValue(-1)
        self.addItem(newConnection)
        self.connections.add(newConnection)
        return newConnection

    def deleteNode(self, node):
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
        for sel in selection:
            if isinstance(sel, graphicitems.ConnectionEdge):
                if sel.sourcePlug.parentObject().model.deleteConnection(sel.destinationPlug.parentObject().model):
                    self.deleteConnection(sel)
                continue
            elif isinstance(sel, graphnodes.QBaseNode):
                deleted = sel.model.delete()
                del self.nodes[hash(sel.model)]
            elif isinstance(sel, graphbackdrop.BackDrop):
                deleted = self.deleteBackDrop(sel)
            else:
                continue
            if deleted:
                self.removeItem(sel)

    def onSetConnectionStyle(self):
        style = self.sender().text()
        styleValue = self.uiApplication.config.connectionStyles.get(style)
        self.uiApplication.config.defaultConnectionStyle = style
        if styleValue == "linear":
            for conn in self.connections:
                conn.setAsLinearPath()
        elif styleValue == "cubic":
            for conn in self.connections:
                conn.setAsCubicPath()
        else:
            for conn in self.connections:
                conn.setLineStyle(styleValue)


class View(graphicsview.GraphicsView):
    requestCopy = QtCore.Signal()
    requestPaste = QtCore.Signal(object)
    nodeDoubleClicked = QtCore.Signal(object)
    panelWidgetDoubleClicked = QtCore.Signal(str)
    requestNodeProperties = QtCore.Signal(object)

    def __init__(self, graph, model, parent=None, setAntialiasing=True):
        super(View, self).__init__(graph.config, parent, setAntialiasing)
        self.application = graph
        self.model = model
        self.newScale = None
        self.panelWidget = None
        self._plugSelected = None
        self._interactiveEdge = None
        self.updateRequested.connect(self.rescaleGraphWidget)
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
        if isinstance(item, (graphnodes.QBaseNode, )):
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
        if self.pan_active:
            self.rescaleGraphWidget()

    def mousePressEvent(self, event):
        button = event.buttons()
        self._origin_pos = event.pos()
        self.previousMousePos = event.pos()
        # ignore any graphicsitems we don't care about, ie. containers
        items = [i for i in self.items(event.pos()) if not isinstance(i, (graphicitems.ItemContainer,
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
                rect = QtCore.QRect(self.previousMousePos, QtCore.QSize())
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
        QtWidgets.QGraphicsView.mousePressEvent(self, event)

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
                    self.onConnectionRequested(self._plugSelected, item)
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

    def wheelEvent(self, event):
        super(View, self).wheelEvent(event)
        self.rescaleGraphWidget()

    def rescaleGraphWidget(self):
        if self.panelWidget is None:
            return

        rect = self.viewport().rect()
        leftCorner = self.mapToScene(0, 0).toPoint()
        sceneRect = self.mapToScene(rect).boundingRect()
        self.panelWidget.setGeometry(leftCorner.x(),
                                     leftCorner.y(),
                                     sceneRect.width(),
                                     sceneRect.height())

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
        self._interactiveEdge.setLineStyle(self.config.defaultConnectionStyle)
        self._interactiveEdge.setWidth(self.config.connectionLineWidth)
        self._interactiveEdge.destinationPoint = plug.center()
        self.scene().addItem(self._interactiveEdge)

    def onConnectionRequested(self, source, destination):
        source = source if source.ioType == "Output" else destination
        destination = destination if destination.ioType == "Input" else source

        if source == destination:
            return

        if not source.container().model.createConnection(destination.container().model):
            return
        self.scene().createConnection(source, destination)

    def itemsFromPos(self, pos):
        return [i for i in self.items(pos) if not isinstance(i, (graphicitems.ItemContainer,
                                                                 graphnodes.NodeHeader))]