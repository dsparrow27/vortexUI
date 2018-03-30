import os
from functools import partial

from qt import QtWidgets, QtCore, QtGui

from zoo.libs.pyqt.widgets.graphics import graphicsview
from zoo.libs.pyqt.widgets.graphics import graphicsscene
from zoo.libs.pyqt.extended import combobox
from vortex.ui import utils
from vortex.ui.graphics import graphpanels, edge, graphicsnode
from zoo.libs.pyqt.widgets.graphics import graphbackdrop


class PopupCompleter(combobox.ExtendedComboBox):

    def __init__(self, position, items, parent):
        super(PopupCompleter, self).__init__(items, parent)
        self.move(position)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Popup)
        self.setSizeAdjustPolicy(self.AdjustToContents)
        self.show()


class GraphEditor(QtWidgets.QWidget):
    def __init__(self, uiApplication, parent=None):
        super(GraphEditor, self).__init__(parent=parent)
        self.uiApplication = uiApplication
        self.init()
        self.view.tabPress.connect(self.tabPress)
        self.view.deletePress.connect(self.scene.onDelete)

    def tabPress(self, point):
        registeredItems = self.uiApplication.registeredNodes()
        if not registeredItems:
            raise ValueError("No registered nodes to display")
        registeredItems.append("Group")
        self.box = PopupCompleter(point, registeredItems, parent=self)
        self.box.itemSelected.connect(self.onLibraryRequestNode)

    def onLibraryRequestNode(self, Type):
        if Type == "Group":
            drop = self.scene.createBackDrop()
            drop.setPos(self.view.centerPosition())
        else:
            self.uiApplication.onNodeCreated(Type)
        self.view.setFocus()

    def showPanels(self, state):
        self.view.showPanels(state)

    def init(self):

        self.editorLayout = QtWidgets.QVBoxLayout()
        self.editorLayout.setContentsMargins(0, 0, 0, 0)
        self.editorLayout.setSpacing(0)
        self.toolbar = QtWidgets.QToolBar(parent=self)
        self.createAlignmentActions(self.toolbar)
        self.toolbar.addSeparator()
        self.uiApplication.customToolbarActions(self.toolbar)
        self.editorLayout.addWidget(self.toolbar)
        # constructor view and set scene
        self.scene = Scene(parent=self)

        self.view = View(self.uiApplication, parent=self)
        self.view.setScene(self.scene)
        self.view.contextMenuRequest.connect(self._onViewContextMenu)
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
        for i in ("SolidLine",
                  "DashLine",
                  "DotLine",
                  "DashDotLine",
                  "DashDotDotLine",
                  "Linear",
                  "Cubic"):
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
    def __init__(self, *args, **kwargs):
        super(Scene, self).__init__(*args, **kwargs)
        self.nodes = set()
        self.backdrops = set()
        self.connections = set()

    def selectedNodes(self):
        return [i for i in self.nodes if i.isSelected()]

    def selectionConnections(self):
        return [i for i in self.connections if i.isSelected()]

    def createNode(self, model, position):
        graphNode = graphicsnode.GraphicsNode(model, position=position)
        self.nodes.add(graphNode)
        self.addItem(graphNode)

    def createBackDrop(self):
        drop = graphbackdrop.BackDrop()
        self.backdrops.add(drop)
        self.addItem(drop)
        return drop

    def createConnection(self, source, destination):
        sourceModel = source.model
        destinationModel = destination.model
        if not sourceModel.canAcceptConnection(destinationModel):
            return
        if destinationModel.isConnected() and not destinationModel.acceptsMultipleConnections():
            connection = self.connectionForPlug(destination)
            self.deleteConnection(connection)
            destinationModel.deleteConnection(sourceModel)
        result = sourceModel.createConnection(destinationModel)
        if not result:
            return
        if sourceModel.isInput():
            connection = edge.ConnectionEdge(destination.outCircle, source.inCircle)
        else:
            connection = edge.ConnectionEdge(source.outCircle, destination.inCircle)
        connection.updatePosition()
        self.connections.add(connection)
        self.addItem(connection)

    def updateAllConnections(self):
        for connection in self.connections:
            connection.updatePosition()

    def connectionForPlug(self, plug):
        for connection in iter(self.connections):
            source = connection.sourcePlug.parentObject()
            if source == plug or connection.destinationPlug.parentObject() == plug:
                return connection

    def updateConnectionsForPlug(self, plug):
        connection = self.connectionForPlug(plug)
        if connection:
            connection.updatePosition()

    def deleteNode(self, node):
        if node in self.nodes:
            self.removeItem(node)
            self.nodes.remove(node)
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
                sel.sourcePlug.parentObject().model.deleteConnection(sel.destinationPlug.parentObject().model)
                self.deleteConnection(sel)
                continue
            elif isinstance(sel, graphicsnode.GraphicsNode):
                deleted = sel.model.delete()
                self.removeNode(sel)
            elif isinstance(sel, graphbackdrop.BackDrop):
                deleted = True
                self.removeBackDrop(sel)
            else:
                continue
            if deleted:
                self.removeItem(sel)

    def onSetConnectionStyle(self):
        style = self.sender().text()
        if style == "SolidLine":
            style = QtCore.Qt.SolidLine
        elif style == "DashLine":
            style = QtCore.Qt.DashLine
        elif style == "DotLine":
            style = QtCore.Qt.DotLine
        elif style == "DashDotLine":
            style = QtCore.Qt.DashDotLine
        elif style == "DashDotDotLine":
            style = QtCore.Qt.DashDotDotLine
        elif style == "Linear":
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
    onTabPress = QtCore.Signal(object)
    requestCopy = QtCore.Signal()
    requestPaste = QtCore.Signal(object)

    def __init__(self, application, parent=None, setAntialiasing=True):
        super(View, self).__init__(application.config, parent, setAntialiasing)
        self.application = application
        self.newScale = None
        self.updateRequested.connect(self.rescaleGraphWidget)
        self.leftPanel = None
        self.rightPanel = None

    def showPanels(self, state):
        if state and self.leftPanel is None and self.rightPanel is None:
            self.leftPanel = graphpanels.Panel()
            self.rightPanel = graphpanels.Panel()
            self.scene().addItem(self.leftPanel)
            self.scene().addItem(self.rightPanel)
            size = self.size()
            self.setSceneRect(0, 0, size.width(), size.height())
            self.rescaleGraphWidget()
        elif not state:
            if self.leftPanel is not None:
                self.layout().takeAt(self.leftPanel)
            if self.rightPanel is not None:
                self.layout().takeAt(self.leftPanel)

    def keyPressEvent(self, event):
        ctrl = event.modifiers() == QtCore.Qt.ControlModifier
        key = event.key()
        if key == QtCore.Qt.Key_C and ctrl:
            self.requestCopy.emit()
        elif key == QtCore.Qt.Key_V and ctrl:
            self.requestPaste.emit(QtGui.QCursor.pos())
        super(View, self).keyPressEvent(event)

    def resizeEvent(self, event):
        super(View, self).resizeEvent(event)
        self.rescaleGraphWidget()

    def mouseMoveEvent(self, event):
        super(View, self).mouseMoveEvent(event)
        if self.pan_active:
            self.rescaleGraphWidget()

    def wheelEvent(self, event):
        super(View, self).wheelEvent(event)
        self.rescaleGraphWidget()

    def rescaleGraphWidget(self):
        rect = self.mapToScene(self.rect()).boundingRect()
        pos = self.mapToScene(0, 0)
        multiple = self.config.panelWidthPercentage
        panelWidth = rect.width() * multiple
        height = rect.height()
        self.leftPanel.setGeometry(pos.x(), pos.y(), panelWidth, height)
        self.rightPanel.setGeometry(rect.topRight().x() - panelWidth,
                                    rect.topRight().y(),
                                    panelWidth,
                                    height)
