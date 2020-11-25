"""Main Graph editor widget which is attached to a page of the graphnote book,
Each editor houses a graphicsview and graphicsScene.
"""
import os, logging
from functools import partial

from Qt import QtWidgets, QtCore, QtGui
from zoo.libs.pyqt.widgets import elements
from vortex.ui import utils
from vortex.ui.graphics import graphnodes, graph
from vortex.ui.views import nodepropertiesdialog

logger = logging.getLogger(__name__)


class GraphEditor(QtWidgets.QWidget):
    """Graph UI manager
    """

    def __init__(self, application, graphModel, objectModel, parent=None):
        super(GraphEditor, self).__init__(parent=parent)
        self.application = application
        self.graph = graphModel
        self.editorLayout = None  # type: elements.vBoxLayout
        self.toolbar = None  # type: QtWidgets.QToolBar
        self.scene = None  # type: graph.Scene
        self.view = None  # type: graph.View
        self.init(objectModel)
        self.connections()
        self.nodeLibraryWidget = application.loadUIPlugin("NodeLibrary", dock=False)

        self.nodeLibraryWidget.widget.finished.connect(self.nodeLibraryWidget.hide)
        self.nodeLibraryWidget.hide()

    @property
    def model(self):
        return self.scene.model

    def close(self):
        self.graph.delete()
        super(GraphEditor, self).close()

    def connections(self):
        self.view.deletePress.connect(self.scene.onDelete)
        self.view.tabPress.connect(self.showNodeLibrary)
        self.application.events.modelNodesCreated.connect(self.scene.createNodes)

    def showNodeLibrary(self, point):
        self.nodeLibraryWidget.initUI(dock=False)
        self.nodeLibraryWidget.widget.move(self.mapFromGlobal(point))

    def init(self, objectModel):
        self.editorLayout = elements.vBoxLayout(parent=self)
        self.toolbar = QtWidgets.QToolBar(parent=self)
        self.createAlignmentActions(self.toolbar)
        self.toolbar.addSeparator()
        self.graph.customToolbarActions(self.toolbar)
        self.editorLayout.addWidget(self.toolbar)
        # constructor view and set scene
        self.scene = graph.Scene(self.graph, parent=self)
        self.view = graph.View(self.graph, parent=self)
        self.view.setScene(self.scene)
        self.view.contextMenuRequest.connect(self._onViewContextMenu)
        self.view.requestNodeProperties.connect(self.displayNodeProperties)
        self.view.nodeDoubleClicked.connect(self._requestCompoundAsCurrent)
        self.view.compoundAsCurrentSig.connect(self._requestCompoundAsCurrent)
        self.breadCrumbWidget = QtWidgets.QLabel("", parent=self)
        self.editorLayout.insertWidget(0, self.breadCrumbWidget)
        # add the view to the layout
        self.editorLayout.addWidget(self.view)
        self.scene.setModel(objectModel)
        self.view.showPanels(True)

    def displayNodeProperties(self, objectModel):
        a = nodepropertiesdialog.NodePropertiesDialog(self.graph, objectModel, parent=self)
        a.exec_()

    def _onViewContextMenu(self, menu, item, pos):
        items = self.view.itemsFromPos(pos)
        if items:
            item = items[0]
            if isinstance(item, (graphnodes.QBaseNode,)) and item.model.supportsContextMenu():
                item.model.contextMenu(menu)
            elif isinstance(item.parentObject(), (graphnodes.QBaseNode,)):
                model = item.parentObject().model
                if model.supportsContextMenu():
                    model.contextMenu(menu)
                return
        edgeStyle = menu.addMenu("ConnectionStyle")
        for i in self.graph.config.connectionStyles.keys():
            edgeStyle.addAction(i, self.scene.onSetConnectionStyle)
        alignment = menu.addMenu("Alignment")
        self.createAlignmentActions(alignment)

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

    def _requestCompoundAsCurrent(self, model):
        self.breadCrumbWidget.setText("->".join(model.fullPathName().split("/")))
        self.scene.setModel(model)
        self.view.showPanels(True)
        self.view.viewport().update()

