"""Main Graph editor widget which is attached to a page of the graphnote book,
Each editor houses a graphicsview and graphicsScene.
"""

import os, logging
from functools import partial

from qt import QtWidgets, QtCore, QtGui

from zoo.libs.pyqt.widgets.graphics import graphicsview
from zoo.libs.pyqt.widgets.graphics import graphicsscene
from vortex.ui import utils
from vortex.ui.graphics import graphpanels, edge, graphicsnode
from zoo.libs.pyqt.widgets.graphics import graphbackdrop

logger = logging.getLogger(__name__)


class GraphEditor(QtWidgets.QWidget):
    requestCompoundExpansion = QtCore.Signal(object)

    def __init__(self, model, application, parent=None):
        super(GraphEditor, self).__init__(parent=parent)
        self.model = model
        self.application = application
        self.init()
        self.view.tabPress.connect(self.showNodeLibrary)
        self.view.deletePress.connect(self.scene.onDelete)
        self.nodeLibraryWidget = application.nodeLibraryWidget(parent=self)
        self.nodeLibraryWidget.hide()

    def showNodeLibrary(self, point):
        registeredItems = self.application.registeredNodes()
        if not registeredItems:
            raise ValueError("No registered nodes to display")
        self.nodeLibraryWidget.reload(registeredItems)
        self.nodeLibraryWidget.show()
        self.nodeLibraryWidget.move(self.mapFromGlobal(point))

    def showPanels(self, state):
        self.view.showPanels(state)

    def init(self):
        self.editorLayout = QtWidgets.QVBoxLayout()
        self.editorLayout.setContentsMargins(0, 0, 0, 0)
        self.editorLayout.setSpacing(0)
        self.toolbar = QtWidgets.QToolBar(parent=self)
        self.createAlignmentActions(self.toolbar)
        self.toolbar.addSeparator()
        self.application.customToolbarActions(self.toolbar)
        self.editorLayout.addWidget(self.toolbar)
        # constructor view and set scene
        self.scene = Scene(self.application, parent=self)

        self.view = View(self.application, self.model, parent=self)
        self.view.setScene(self.scene)
        self.view.contextMenuRequest.connect(self._onViewContextMenu)
        self.view.requestCompoundExpansion.connect(self.requestCompoundExpansion.emit)
        # add the view to the layout
        self.editorLayout.addWidget(self.view)
        self.setLayout(self.editorLayout)

    def createAlignmentActions(self, parent):
        icons = os.environ["VORTEX_ICONS"]
        iconsData = {
            "horizontalAlignCenter.png": ("Aligns the selected nodes to the horizontal center", utils.CENTER | utils.X),
            "horizontalAlignLeft.png": ("Aligns the selected nodes to the Left", utils.LEFT),
            "horizontalAlignRight.png": ("Aligns the selected nodes to the Right", utils.RIGHT),
            "verticalAlignBottom.png": ("Aligns the selected nodes to the bottom", utils.BOTTOM),
            "verticalAlignCenter.png": ("Aligns the selected nodes to the vertical center", utils.CENTER | utils.Y),
            "verticalAlignTop.png": ("Aligns the selected nodes to the Top", utils.TOP)}
        for name, tip in iconsData.items():
            act = QtWidgets.QAction(QtGui.QIcon(os.path.join(icons, name)), "", self)
            act.setStatusTip(tip[0])
            act.setToolTip(tip[0])
            act.triggered.connect(partial(self.alignSelectedNodes, tip[1]))
            parent.addAction(act)

    def _onViewContextMenu(self, menu, item):
        if item:
            if isinstance(item, (graphicsnode.GraphicsNode, graphpanels.Panel)) and item.model.supportsContextMenu():
                item.model.contextMenu(menu)
            return
        edgeStyle = menu.addMenu("ConnectionStyle")
        for i in self.application.config.connectionStyles.keys():
            edgeStyle.addAction(i, self.scene.onSetConnectionStyle)
        alignment = menu.addMenu("Alignment")
        self.createAlignmentActions(alignment)

    def alignSelectedNodes(self, direction):
        nodes = self.scene.selectedNodes()
        if len(nodes) < 2:
            return
        if direction == utils.CENTER | utils.X:
            utils.nodesAlignX(nodes, utils.CENTER)
        elif direction == utils.CENTER | utils.Y:
            utils.nodesAlignY(nodes, utils.CENTER)
        elif direction == utils.RIGHT:
            utils.nodesAlignX(nodes, utils.RIGHT)
        elif direction == utils.LEFT:
            utils.nodesAlignX(nodes, utils.LEFT)
        elif direction == utils.TOP:
            utils.nodesAlignY(nodes, utils.TOP)
        else:
            utils.nodesAlignY(nodes, utils.BOTTOM)
        # :todo: only update the selected nodes
        self.scene.updateAllConnections()


class Scene(graphicsscene.GraphicsScene):
    def __init__(self, application, *args, **kwargs):
        super(Scene, self).__init__(*args, **kwargs)
        self.selectionChanged.connect(self._onSelectionChanged)
        self.uiApplication = application
        self.nodes = {}
        self.panelWidget = None
        self.backdrops = set()
        self.connections = set()
        self.uiApplication.onNodeDeleteRequested.connect(self.deleteNode)

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

    def createNode(self, model, position):
        graphNode = graphicsnode.GraphicsNode(model, position=position)
        self.addItem(graphNode)
        graphNode.init()
        model.addConnectionSig.connect(self.createConnection)
        self.nodes[hash(model)] = {"qitem": graphNode,
                                   "model": model}

    def createBackDrop(self):
        drop = graphbackdrop.BackDrop()
        self.backdrops.add(drop)
        self.addItem(drop)
        return drop

    def createConnection(self, sourceModel, destinationModel):
        """Called from the model. the create an Edge between two attributes.

        :param sourceModel: The source attribute objectModel
        :type sourceModel: ::class:`ObjectModel`
        :param destinationModel: The destination attribute objectModel
        :type destinationModel: ::class:`ObjectModel`
        """
        sourceModelObj = sourceModel.objectModel
        sourceNode = self.nodes.get(hash(sourceModelObj), {}).get("qitem")
        destination, source = None, None
        # ok if the sourceNode can't be found in the nodes cache
        # then it may means it's part of the side panels. Inputs are on the left panel
        # while the outputs are on the rightPanel
        if sourceNode is None:
            # compare hash of the objectModels
            if hash(self.panelWidget.model) == hash(sourceModelObj):
                source = self.panelWidget.leftPanel.attributeItem(sourceModel)
        else:
            source = sourceNode.attributeItem(sourceModel)  # source Plug item which will be connected
        destinationModelObj = destinationModel.objectModel
        destinationNode = self.nodes.get(hash(destinationModelObj), {}).get("qitem")
        if destinationNode is None:
            # compare hash of the objectModels
            if hash(self.panelWidget.model) == hash(destinationModelObj):
                destination = self.panelWidget.rightPanel.attributeItem(destinationModel)
        else:
            destination = destinationNode.attributeItem(destinationModel)  # destination Plug Item which will be
        if destination is None or source is None:
            msg = "Can't find source: {} or destination: {}, attributes on source: {}, destination: {}".format(
                sourceModel.text(), destinationModel.text(), sourceNode.text(), destinationNode.text())
            logger.error(msg)
            return

        connection = destination.addConnection(source)
        logger.debug("Created Connection Edge, input: {}, output: {}".format(sourceModel.text(),
                                                                             destinationModel.text()))
        self.connections.add(connection)
        self.addItem(connection)

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

    def deleteNode(self, node):
        key = hash(node)
        if key in self.nodes:
            item = self.nodes[key]["qitem"]
            self.removeItem(item)
            del self.nodes[key]
            return True
        return False

    def deleteBackDrop(self, backDrop):
        if backDrop in self.backdrops:
            self.removeItem(backDrop)
            self.backdrops.remove(backDrop)
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
            if isinstance(sel, edge.ConnectionEdge):
                if sel.sourcePlug.parentObject().model.deleteConnection(sel.destinationPlug.parentObject().model):
                    self.deleteConnection(sel)
                continue
            elif isinstance(sel, graphicsnode.GraphicsNode):
                deleted = sel.model.delete()
            elif isinstance(sel, graphbackdrop.BackDrop):
                deleted = True
                self.deleteBackDrop(sel)
            else:
                continue
            if deleted:
                self.removeItem(sel)

    def onSetConnectionStyle(self):
        style = self.sender().text()
        style = self.uiApplication.config.connectionStyles.get(style)
        self.uiApplication.config.defaultConnectionStyle = style
        if style == "Linear":
            for conn in self.connections:
                conn.setAsLinearPath()
            self.update()
            return
        elif style == "Cubic":
            for conn in self.connections:
                conn.setAsCubicPath()
            self.update()
            return
        for conn in self.connections:
            conn.setLineStyle(style)
        self.update()


class View(graphicsview.GraphicsView):
    requestCopy = QtCore.Signal()
    requestPaste = QtCore.Signal(object)
    requestCompoundExpansion = QtCore.Signal(object)

    def __init__(self, application, model, parent=None, setAntialiasing=True):
        super(View, self).__init__(application.config, parent, setAntialiasing)
        self.application = application
        self.model = model
        self.newScale = None
        self.updateRequested.connect(self.rescaleGraphWidget)
        self.panelWidget = None

    def showPanels(self, state):
        if state:
            self.panelWidget = graphpanels.PanelWidget(self.model, acceptsContextMenu=True)
            self.scene().panelWidget = self.panelWidget
            self.scene().addItem(self.panelWidget)
            size = self.size()
            self.setSceneRect(0, 0, size.width(), size.height())

    def keyPressEvent(self, event):
        ctrl = event.modifiers() == QtCore.Qt.ControlModifier
        key = event.key()
        if key in (QtCore.Qt.Key_C, QtCore.Qt.Key_V, QtCore.Qt.Key_G) and ctrl:
            self.application.keyPressEvent(event)
        super(View, self).keyPressEvent(event)

    def resizeEvent(self, event):
        super(View, self).resizeEvent(event)
        self.rescaleGraphWidget()

    def mouseDoubleClickEvent(self, event):
        item = self.itemAt(event.pos())
        if isinstance(item, graphicsnode.GraphicsNode) and item.model.isCompound():
            self.requestCompoundExpansion.emit(item)
        super(View, self).mouseDoubleClickEvent(event)

    def mouseMoveEvent(self, event):
        super(View, self).mouseMoveEvent(event)
        if self.pan_active:
            self.rescaleGraphWidget()

    def mousePressEvent(self, event):
        if self.parent().nodeLibraryWidget.isVisible():
            self.parent().nodeLibraryWidget.hide()

        super(View, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):

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
        self.panelWidget.setGeometry(leftCorner.x(),
                                     leftCorner.y(),
                                     rect.width(),
                                     rect.height())
        # force the heights
        self.panelWidget.rightPanel.setMinimumHeight(rect.height())
        self.panelWidget.leftPanel.setMinimumHeight(rect.height())
