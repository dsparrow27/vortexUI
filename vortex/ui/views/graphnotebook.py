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
    def __init__(self,application, parent=None):
        super(GraphNotebook, self).__init__(parent=parent)
        self.application = application
        application.graphNoteBook = self
        self.pages = []
        self.notebook = None
        self.initLayout()

    def initLayout(self):
        layout = elements.vBoxLayout(parent=self)
        self.notebook = tabwidget.TabWidget("NoteBook", parent=self)
        layout.addWidget(self.notebook)
    #
    # def onRequestExpandCompoundAsTab(self, compound):
    #     self.addPage(compound.text())
    #     self.graph.models[compound.text()] = compound

    def addPage(self, graph, objectModel):
        editor = grapheditor.GraphEditor(self.application,  graph, objectModel, parent=self)
        editor.showPanels(True)
        graph.nodeCreated.connect(editor.createNode)
        graph.graphLoaded.connect(self._onGraphLoad)

        self.pages.append(editor)
        self.notebook.insertTab(0, editor, objectModel.text())
        for child in objectModel.children():
            editor.createNode(child)
        return editor

    def setCurrentPageLabel(self, label):
        page = self.notebook.currentIndex()
        self.notebook.setTabText(page, label)

    def deletePage(self, index):
        if index in range(self.notebook.count()):
            # show popup
            self.pages[index].close()
            self.notebook.removeTab(index)
            # self.graph.onBeforeRemoveTab.emit(self.pages[index])
            # self.graph.onAfterRemoveTab.emit(self.pages[index])

    def clear(self):
        for i in range(len(self.pages)):
            self.deletePage(i)
        self.notebook.clear()

    def currentPage(self):
        if self.notebook.currentIndex() in range(len(self.pages)):
            return self.pages[self.notebook.currentIndex()]

    def _onGraphLoad(self, objectModel, clear=False):
        if clear:
            self.clear()

        # self.addPage(editor.graph, objectModel)
