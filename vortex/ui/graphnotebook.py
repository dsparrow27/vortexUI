from qt import QtWidgets, QtCore, QtGui
from vortex.ui import grapheditor
import logging

logger = logging.getLogger(__name__)


class GraphNotebook(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(GraphNotebook, self).__init__(parent=parent)
        self.pages = []
        self.initLayout()

    def bindApplication(self, uiApplication):
        logger.debug("Binding UIApplication to notebook")
        self.uiApplication = uiApplication
        uiApplication.onNewNodeRequested.connect(self.onRequestaddNodeToScene)
        uiApplication.initialize()

    def onRequestaddNodeToScene(self, data):
        # {model: objectModel, newTab: True}
        if data["newTab"]:
            editor = self.addPage(data["model"].text())
        else:
            editor = self.currentPage()
            editor.scene.createNode(model=data["model"], position=editor.view.centerPosition())

    def showTabContextMenu(self, pos):
        tabWidget = self.notebook.tabBar().tabAt(pos)
        if not tabWidget:
            return
        menu = QtWidgets.QMenu(parent=self)
        menu.addAction("Delete")
        menu.exec_(tabWidget.mapToGlobal(pos))

    def initLayout(self):
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(2, 2, 2, 2)
        self.setLayout(layout)
        self.notebook = QtWidgets.QTabWidget(parent=self)
        bar = self.notebook.tabBar()
        bar.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        bar.customContextMenuRequested.connect(self.showTabContextMenu)
        self.notebook.setMovable(True)
        self.notebook.setTabsClosable(True)
        self.notebook.tabCloseRequested.connect(self.deletePage)

        layout.addWidget(self.notebook)

    def onRequestExpandCompoundAsTab(self, compound):
        self.addPage(compound.text())
        self.uiApplication.models[compound.text()] = compound

    def addPage(self, label):
        editor = grapheditor.GraphEditor(self.uiApplication, parent=self)
        editor.requestCompoundExpansion.connect(self.onRequestExpandCompoundAsTab)
        editor.showPanels(True)
        self.pages.append(editor)
        self.notebook.insertTab(0, editor, label)
        return editor

    def setCurrentPageLabel(self, label):
        page = self.notebook.currentIndex()
        self.notebook.setTabText(page, label)

    def deletePage(self, index):
        if index in range(self.notebook.count()):
            # show popup
            # self.uiApplication.onBeforeRemoveTab.emit(self.pages[index])
            self.pages[index].close()
            self.notebook.removeTab(index)
            # self.uiApplication.onAfterRemoveTab.emit(self.pages[index])

    def clear(self):
        self.notebook.clear()

    def currentPage(self):
        if self.notebook.currentIndex() in range(len(self.pages)):
            return self.pages[self.notebook.currentIndex()]
