from Qt import QtWidgets, QtCore, QtGui
from vortex.ui import grapheditor
from zoo.libs.pyqt.extended import tabwidget
import logging

logger = logging.getLogger(__name__)


class GraphNotebook(QtWidgets.QWidget):
    def __init__(self, uiApplication, parent=None):
        super(GraphNotebook, self).__init__(parent=parent)
        self.pages = []
        self.notebook = None
        self.initLayout()
        self.uiApplication = uiApplication

    def initLayout(self):
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(2, 2, 2, 2)
        self.setLayout(layout)

        self.notebook = tabwidget.TabWidget("NoteBook", parent=self)

        layout.addWidget(self.notebook)

    def onRequestExpandCompoundAsTab(self, compound):
        self.addPage(compound.text())
        self.uiApplication.models[compound.text()] = compound

    def addPage(self, model):
        editor = grapheditor.GraphEditor(model, self.uiApplication, parent=self)
        # model.addConnectionSig.connect(editor.scene.createConnection)
        editor.requestCompoundExpansion.connect(self.onRequestExpandCompoundAsTab)
        editor.showPanels(True)
        self.pages.append(editor)
        self.notebook.insertTab(0, editor, model.text())
        return editor

    def setCurrentPageLabel(self, label):
        page = self.notebook.currentIndex()
        self.notebook.setTabText(page, label)

    def deletePage(self, index):
        if index in range(self.notebook.count()):
            # show popup
            self.uiApplication.onBeforeRemoveTab.emit(self.pages[index])
            self.pages[index].close()
            self.notebook.removeTab(index)
            self.uiApplication.onAfterRemoveTab.emit(self.pages[index])

    def clear(self):
        self.notebook.clear()

    def currentPage(self):
        if self.notebook.currentIndex() in range(len(self.pages)):
            return self.pages[self.notebook.currentIndex()]
