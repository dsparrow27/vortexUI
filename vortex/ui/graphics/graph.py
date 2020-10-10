import json

from Qt import QtWidgets, QtCore, QtGui

from zoo.libs.pyqt.widgets.graphics import graphicsview
from zoo.libs.pyqt.widgets.graphics import graphicsscene
from vortex.ui.graphics import plugwidget
from vortex.ui.graphics import graphnodes
from vortex.ui import utils
from zoo.libs.utils import zlogging
from zoo.libs.pyqt.widgets.graphics import graphbackdrop, graphicitems

logger = zlogging.getLogger(__name__)


class View(graphicsview.GraphicsView):
    """

    :param graph:
    :type graph: :class:`vortex.ui.model.graphmodel.Graph`
    :param model:
    :type model: :class:`vortex.ui.model.objectmodel.ObjectModel`
    :param parent:
    :type parent: :class:`:class:`vortex.ui.views.grapheditor.View``
    :param setAntialiasing:
    :type setAntialiasing: bool
    """
    nodeDoubleClicked = QtCore.Signal(object)
    requestNodeProperties = QtCore.Signal(object)
    compoundExpansionSig = QtCore.Signal(object)
    compoundAsCurrentSig = QtCore.Signal(object)

    def __init__(self, graph, parent=None, setAntialiasing=True):

        super(View, self).__init__(graph.config, parent, setAntialiasing)
        self.graph = graph
        self.newScale = None
        self._plugSelected = None
        self._interactiveEdge = None
        self.pan_active = False

    @property
    def model(self):
        return self.scene().model

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
        self.parent().nodeLibraryWidget.hide()
        super(View, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):

        if self._plugSelected and not self.pan_active:
            if self._interactiveEdge is not None:
                self.scene().removeItem(self._interactiveEdge)
            self._interactiveEdge = None
            # ignore any graphics items we don't care about, ie. containers
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

    def keyPressEvent(self, event):
        if event.matches(QtGui.QKeySequence.Copy):
            selectedNodes = self.scene().selectedNodes()
            if selectedNodes:
                data = {"application": "vortex",
                        "parent": selectedNodes[0].model.parentObject().fullPathName()
                        }
                for item in selectedNodes:
                    data.setdefault("data", []).append(item.model.serialize())
                mimeData = QtCore.QMimeData()
                mimeData.setText(json.dumps(data))
                QtWidgets.QApplication.instance().clipboard().setMimeData(mimeData)
            return

        elif event.matches(QtGui.QKeySequence.Paste):
            clipboard = QtWidgets.QApplication.instance().clipboard()
            mimeData = clipboard.mimeData()
            if mimeData.hasText():
                try:
                    data = json.loads(mimeData.text())
                    if data.get("application", "") == "vortex":
                        for node in data["data"]:
                            try:
                                del node["connections"]
                            except KeyError:
                                pass
                            nodes = self.graph.loadFromDict(node, self.model)
                            self.scene.createNodes(nodes)

                except json.decoder.JSONDecodeError:
                    logger.error("unable to paste in compatible format", exc_info=True)
            return

        elif event.key() == QtCore.Qt.Key_I:
            selected = self.scene().selectedNodes()
            compounds = []
            for sel in selected:
                if sel in compounds:
                    logger.error("Please select only one compound to expand")
                    return
                if sel.model.isCompound():
                    compounds.append(sel)
            if compounds:
                self.compoundExpansionSig.emit(sel.model)

        elif event.key() == QtCore.Qt.Key_U:
            model = self.model
            if model != model.root():
                self.compoundAsCurrentSig.emit(model.parentObject())

        return super(View, self).keyPressEvent(event)

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


class Scene(graphicsscene.GraphicsScene):
    """

    :param graph:
    :type graph: :class:`vortex.ui.model.graphmodel.Graph`
    :param parent:
    :type parent: :class:`:class:`vortex.ui.views.grapheditor.View``
    """

    def __init__(self, graph, *args, **kwargs):
        super(Scene, self).__init__(*args, **kwargs)
        self.graph = graph
        self.model = None
        self.nodes = {}
        self.connections = []
        self.selectionChanged.connect(self._onSelectionChanged)

    def setModel(self, objectModel):
        self.clear()
        self.nodes = {}
        self.connections = []
        self.model = objectModel
        self.createNodes(objectModel.children())
        for n in objectModel.children():
            for attr in n.attributes():
                connections = attr.connections()
                self.createConnections(connections)

        return True

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
            self.graph.application.events.uiSelectionChanged.emit(models)

    def selectedNodes(self):
        try:
            return [i["qitem"] for i in self.nodes.values() if i["qitem"].isSelected()]
        except RuntimeError:
            return []

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
            sourceItem, destinationItem = self.plugItemsForModels(*connection)
            if sourceItem is not None and destinationItem is not None:
                self.createConnectionItem(sourceItem, destinationItem)

    def updateAllConnections(self):
        for connection in self.connections:
            connection["qitem"].updatePosition()

    def connectionsForPlug(self, plug):
        for connection in self.connections:
            item = connection["qitem"]
            source = item.sourcePlug
            if source == plug or item.destinationPlug == plug:
                yield connection

    def updateConnectionsForPlug(self, plug):
        for conn in self.connectionsForPlug(plug):
            conn["qitem"].updatePosition()

    def createConnection(self, source, destination):
        src = source if source.model.isOutput() else destination
        dest = destination if destination.model.isInput() else source
        if src == dest:
            logger.debug("source and destination is the same")
            return
        if not src.model.canAcceptConnection(dest.model):
            return
        newConnection = src.model.createConnection(dest.model)
        if not newConnection:
            return
        newConnection = self.createConnectionItem(src, dest)
        return newConnection

    def createConnectionItem(self, srcItem, destinationItem):
        newConnection = graphicitems.ConnectionEdge(srcItem.outCircle,destinationItem.inCircle,
                                                    curveType=self.graph.config.defaultConnectionShape,
                                                    colour=srcItem.inCircle.colour)
        newConnection.setLineStyle(self.graph.config.defaultConnectionStyle)
        newConnection.setWidth(self.graph.config.connectionLineWidth)
        newConnection.setCurveType(self.graph.config.defaultConnectionShape)
        self.addItem(newConnection)
        self.connections.append({"srcModel": srcItem, "destModel": destinationItem, "qitem": newConnection})
        newConnection.updatePosition()
        return newConnection

    def plugItemsForModels(self, source, destination):
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
        return sourceItem, destinationItem

    def connectionsForNodes(self, objectModels):
        for connection in self.connections:
            src, dest = connection["srcModel"].objectModel, connection["destModel"].objectModel
            if src in objectModels or dest in objectModels:
                yield connection

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

    def deleteConnection(self, qItem):
        toRemove = -1
        for index, connection in enumerate(self.connections):
            item = connection["qitem"]
            if item == qItem:
                toRemove = index
                break
        if toRemove != -1:
            conn = self.connections[toRemove]
            del self.connections[toRemove]
            self.removeItem(conn["qitem"])
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
