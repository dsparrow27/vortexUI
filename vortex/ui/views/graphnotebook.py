"""GraphNoteBook is container  management for a tabwidget of all graphs.
Each Tab contains it's own graphicsView and qscene but references the same datamodel backend when needed
however they can also be completed isolated.

"""
from vortex.ui.views import grapheditor
from zoo.libs.pyqt.extended import tabwidget
from zoo.libs.pyqt.widgets import frame
from zoo.libs.pyqt.widgets import elements
from zoovendor.Qt import QtCore
import logging

logger = logging.getLogger(__name__)


class GraphNotebook(tabwidget.TabWidget):
    def __init__(self, application, parent=None):
        super(GraphNotebook, self).__init__("NoteBook", showNewTab=True, parent=parent)
        self.newTabRequested.connect(self._onNewGraph)
        self.tabCloseRequested.connect(self._onTabClose)
        self.application = application
        application.graphNoteBook = self
        self.editors = []
        self.hasWelcome = True
        self.addWelcomeTab()
        application.sigGraphCreated.connect(self._onGraphModelCreated)

    def _onGraphModelCreated(self, graphModel):
        self.addGraph(graphModel, graphModel.rootNode)

    def _onNewGraph(self, wid, text):
        self.application.createNewGraph(text)

    def _onTabClose(self, index):
        if self.onTabCloseRequested():
            self.deleteGraph(index)

    def addWelcomeTab(self):
        wel = WelcomeWidget(self.application, parent=self)
        wel.createSig.connect(self.application.createNewGraph)
        self.onAddTab(wel, "Welcome")
        self.hasWelcome = True

    def addGraph(self, graph, objectModel):
        editor = grapheditor.GraphEditor(self.application, graph, objectModel, parent=self)
        self.editors.append(editor)
        if self.hasWelcome:
            logger.debug("Removing welcome tab")
            self.removeTab(0)
            self.hasWelcome = False
        self.onAddTab(editor, objectModel.text())
        self.application.events.uiGraphCreated.emit(graph)
        return editor

    def setCurrentGraphLabel(self, label):
        page = self.currentIndex()
        self.setTabText(page, label)

    def deleteGraph(self, index):
        if index in range(self.count()):
            # show popup
            graph = self.editors[index].graph
            self.application.events.uiGraphDeleted.emit(graph)
            self.editors[index].close()
            self.removeTab(index)
            if self.count() < 1:
                self.addWelcomeTab()

    def clear(self):
        for i in range(self.count):
            self.deleteGraph(i)
        self.clear()

    def currentEditor(self):
        if self.currentIndex() in range(self.count()):
            return self.editors[self.currentIndex()]

    def _onGraphLoad(self, graph, clear=False):
        if clear:
            self.clear()
        self.addGraph(graph, graph.rootNode())


class WelcomeWidget(frame.QFrame):
    createSig = QtCore.Signal()

    def __init__(self, application, parent=None):
        super(WelcomeWidget, self).__init__(parent)
        self.application = application
        self.btn = elements.regularButton(text="Create Graph", parent=self)
        self.btn.clicked.connect(self.createSig.emit)
        layout = elements.hBoxLayout(parent=self)
        layout.addWidget(self.btn)
