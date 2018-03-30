from qt import QtWidgets, QtCore, QtGui

from zoo.libs.pyqt.widgets.graphics import graphicsview
from zoo.libs.pyqt.widgets.graphics import graphicsscene
from zoo.libs.pyqt.extended import combobox
from zoo.libs.pyqt.widgets import dialog
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
        # constructor view and set scene
        self.scene = Scene(parent=self)

        self.view = View(self.uiApplication, parent=self)
        self.view.setScene(self.scene)
        self.view.contextMenuRequest.connect(self._onContextMenu)
        # add the view to the layout
        self.editorLayout.addWidget(self.view)
        self.setLayout(self.editorLayout)

    def _onContextMenu(self, menu):
        edgeStyle = menu.addMenu("ConnectionStyle")
        for i in ("SolidLine",
                  "DashLine",
                  "DotLine",
                  "DashDotLine",
                  "DashDotDotLine"):
            edgeStyle.addAction(i, self.scene.onSetConnectionStyle)


class Scene(graphicsscene.GraphicsScene):
    def __init__(self, *args, **kwargs):
        super(Scene, self).__init__(*args, **kwargs)
        self.nodes = set()
        self.backdrops = set()
        self.connections = set()

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

    def updateConnectionsForPlug(self, plug):
        for connection in self.connections:
            source = connection.sourcePlug.parentObject()
            destination = connection.destinationPlug.parentObject()
            if source == plug or destination == plug:
                connection.updatePosition()

    def deleteNode(self, node):
        if node in self.nodes:
            self.removeItem(node)
            self.nodes.remove(node)
            return True
        return False

    def onDelete(self, selection):
        for sel in selection:
            if isinstance(sel, edge.ConnectionEdge):
                deleted = sel.sourcePlug.parentObject().model.deleteConnection(sel.destinationPlug.parentObject().model)
                self.removeConnection(sel)
            elif isinstance(sel, graphicsnode.GraphicsNode):
                deleted = sel.model.delete()
                self.removeNode(sel)
            elif isinstance(sel, graphbackdrop.BackDrop):
                deleted = True
                self.removeBackDrop(sel)
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
