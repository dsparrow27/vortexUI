"""GraphNoteBook is container  management for a tabwidget of all graphs.
Each Tab contains it's own graphicsView and qscene but references the same datamodel backend when needed
however they can also be completed isolated.

"""
from vortex.ui.views import grapheditor
from zoo.libs.pyqt.extended import tabwidget
import logging

logger = logging.getLogger(__name__)


class GraphNotebook(tabwidget.TabWidget):
    def __init__(self, application, parent=None):
        super(GraphNotebook, self).__init__("NoteBook", parent=parent)
        self.application = application
        application.graphNoteBook = self
        self.editors = []

    def addGraph(self, graph, objectModel):
        editor = grapheditor.GraphEditor(self.application, graph, objectModel, parent=self)
        self.application.events.modelGraphLoaded.connect(self._onGraphLoad)

        self.editors.append(editor)
        self.onAddTab(editor, objectModel.text())

        return editor

    def _onRequestCompound(self, objectModel):
        self.addGraph(self.currentEditor().graph, objectModel)

    def setCurrentGraphLabel(self, label):
        page = self.currentIndex()
        self.setTabText(page, label)

    def deleteGraph(self, index):
        if index in range(self.count()):
            # show popup
            self.editors[index].close()
            self.removeTab(index)

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
