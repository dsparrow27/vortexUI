from vortex.ui.views import graphnotebook
from Qt import QtWidgets, QtCore
from zoo.libs.pyqt.widgets import mainwindow
from zoo.libs.pyqt.widgets import elements
from zoo.libs import iconlib


class ApplicationWindow(elements.FramelessWindow):

    def __init__(self, application, title="", parent=None, width=800, height=600, framelessChecked=True,
                 titleBarClass=None,
                 titleShrinksFirst=True, alwaysShowAllTitle=False):
        super(ApplicationWindow, self).__init__(title, parent, width, height, framelessChecked, titleBarClass,
                                                titleShrinksFirst,
                                                alwaysShowAllTitle)
        layout = elements.vBoxLayout()
        self.setMainLayout(layout)
        layout.addWidget(VortexApplicationWindow(application))

        fileMenu = elements.IconMenuButton(iconlib.icon("magic", size=32))

        self.titlebarContentsLayout().addWidget(fileMenu)
        self.loadAction = fileMenu.addAction("Load", connect=self.onLoad)
        self.saveAction = fileMenu.addAction("Save", connect=self.onSave)
        self.exitAction = fileMenu.addAction("Close", icon=iconlib.icon("close"))
        self.exitAction.setShortcut("ctrl+Q")
        self.exitAction.setToolTip("Closes application")
        # self.recentFilesMenu = QtWidgets.QMenu("Recent Files", parent=self)

    def onSave(self):
        fname, _ = QtWidgets.QFileDialog.getSaveFileName(parent=self, caption="Select Graph")
        if fname:
            graphEditor = self.noteBook.currentPage()
            if graphEditor is not None:
                graphEditor.graph.saveGraph(fname)

    def onLoad(self):
        fname, _ = QtWidgets.QFileDialog.getOpenFileName(parent=self, caption="Select Graph")
        if fname:
            self.uiApplication.createGraphFromPath(fname)


class VortexApplicationWindow(mainwindow.MainWindow):
    def __init__(self, application, title="Vortex", width=800, height=600, parent=None):
        super(VortexApplicationWindow, self).__init__(title=title, width=width, height=height, parent=parent)
        self.uiApplication = application
        self.noteBook = graphnotebook.GraphNotebook(self.uiApplication, parent=self)
        self.setCustomCentralWidget(self.noteBook)
        self.uiApplication.loadPlugins()
