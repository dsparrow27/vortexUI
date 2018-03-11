from qt import QtWidgets, QtCore
from vortex.ui import grapheditor
from vortex.ui.graphics import graphicsnode


class GraphNotebook(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(GraphNotebook, self).__init__(parent=parent)

        self.pages = []
        self.initLayout()

    def bindApplication(self, uiApplication):
        self.uiApplication = uiApplication
        uiApplication.onNewNodeRequested.connect(self.onRequestaddNodeToScene)
        uiApplication.initialize()

    def onRequestaddNodeToScene(self, data):
        # {model: objectModel, newTab: True}
        if data["newTab"]:
            editor = self.addPage(data["model"].text())

        else:
            editor = self.currentPage()
            graphNode = graphicsnode.GraphicsNode(data["model"])
            editor.scene.addItem(graphNode)

    def initLayout(self):
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(2, 2, 2, 2)
        self.setLayout(layout)
        self.notebook = QtWidgets.QTabWidget(parent=self)
        self.notebook.setMovable(True)
        self.notebook.setTabsClosable(True)
        self.notebook.tabCloseRequested.connect(self.deletePage)
        layout.addWidget(self.notebook)

    def addPage(self, label):
        # self.uiApplication.onBeforeNewTab.emit(self.currentPage())
        editor = grapheditor.GraphEditor(self.uiApplication, parent=self)
        editor.setGraph(grapheditor.GraphWidget())
        self.pages.append(editor)
        self.notebook.insertTab(0, editor, label)
        # self.uiApplication.onAfterNewTab.emit(self.currentPage())
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
