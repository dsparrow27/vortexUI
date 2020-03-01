from vortex.ui.views import graphnotebook
from Qt import QtWidgets
from zoo.libs.pyqt.widgets import mainwindow
from zoo.preferences.core import preference


class ApplicationWindow(mainwindow.MainWindow):
    def __init__(self, vortexGraph, title="Vortex", width=800, height=600, parent=None):
        super(ApplicationWindow, self).__init__(title=title, width=width, height=height, parent=parent)

        self.setStyleSheet(preference.interface("core_interface").stylesheet().data)
        self.noteBook = graphnotebook.GraphNotebook(vortexGraph, parent=self)
        self.setCustomCentralWidget(self.noteBook)
        self.setupMenuBar()
        self.loadAction = QtWidgets.QAction("Load", parent=self)
        self.saveAction = QtWidgets.QAction("Save", parent=self)
        self.recentFilesMenu = QtWidgets.QMenu("Recent Files", parent=self)

        self.fileMenu.insertAction(self.exitAction, self.saveAction)
        self.fileMenu.insertAction(self.exitAction, self.loadAction)
        self.fileMenu.insertMenu(self.exitAction, self.recentFilesMenu)
        self.saveAction.triggered.connect(self.onSave)
        self.loadAction.triggered.connect(self.onLoad)
        vortexGraph.loadPlugins()

    def onSave(self):
        fname, _ = QtWidgets.QFileDialog.getSaveFileName(parent=self, caption="Select Graph")
        if fname:
            self.noteBook.graph.saveGraph(fname)

    def onLoad(self):
        fname, _ = QtWidgets.QFileDialog.getOpenFileName(parent=self, caption="Select Graph")
        if fname:
            self.noteBook.graph.loadGraph(fname)
