"""GraphNoteBook is a contains the management for a tabwidget of all graphs.
Each Tab contains it's own graphicsView and qscene but references the same datamodel backend.

"""
from functools import partial

from Qt import QtWidgets, QtCore, QtGui
from vortex.ui.views import grapheditor
from zoo.libs.pyqt.extended import tabwidget
from zoo.libs.pyqt.widgets import elements
import logging

logger = logging.getLogger(__name__)


class GraphNotebook(QtWidgets.QWidget):
    def __init__(self, application, parent=None):
        super(GraphNotebook, self).__init__(parent=parent)
        self.application = application
        application.graphNoteBook = self
        self.pages = []
        self.notebook = tabwidget.TabWidget("NoteBook", parent=self)
        self.initLayout()

    def initLayout(self):
        layout = elements.vBoxLayout(parent=self)
        layout.addWidget(self.notebook)
        self.notebook.tabCloseRequested.connect(self.deletePage)

    def addPage(self, graph, objectModel):
        editor = grapheditor.GraphEditor(self.application, graph, objectModel, parent=self)
        self.application.events.modelGraphLoaded.connect(self._onGraphLoad)
        editor.requestCompoundExpansion.connect(self._onRequestCompound)

        self.pages.append(editor)
        self.notebook.onAddTab(editor, objectModel.text())
        editor.scene.createNodes(objectModel.children())
        for n in objectModel.children():
            for attr in n.attributes():
                connections = attr.connections()
                editor.scene.createConnections(connections)

        return editor

    def _onRequestCompound(self, objectModel):
        self.addPage(self.currentPage().graph, objectModel)

    def setCurrentPageLabel(self, label):
        page = self.notebook.currentIndex()
        self.notebook.setTabText(page, label)

    def deletePage(self, index):
        if index in range(self.notebook.count()):
            # show popup
            self.pages[index].close()
            self.notebook.removeTab(index)

    def clear(self):
        for i in range(len(self.pages)):
            self.deletePage(i)
        self.notebook.clear()

    def currentPage(self):
        if self.notebook.currentIndex() in range(len(self.pages)):
            return self.pages[self.notebook.currentIndex()]

    def _onGraphLoad(self, graph, clear=False):
        if clear:
            self.clear()
        self.addPage(graph, graph.rootNode())
