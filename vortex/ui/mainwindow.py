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
        self.win = VortexApplicationWindow(application, parent=self)
        layout.addWidget(self.win)
        titleBtn = self.titleBar.logoButton
        self.loadAction = titleBtn.addAction("Load", connect=self.onLoad)
        self.saveAction = titleBtn.addAction("Save", connect=self.onSave)
        self.exitAction = titleBtn.addAction("Close", icon=iconlib.icon("close"))
        self.exitAction.setShortcut("Ctrl+Q")
        self.exitAction.setToolTip("Closes application")
        self.toggleMaximized()
        # self.recentFilesMenu = QtWidgets.QMenu("Recent Files", parent=self)

    def onSave(self):
        fname, _ = QtWidgets.QFileDialog.getSaveFileName(parent=self, caption="Select Graph")
        if fname:
            graphEditor = self.win.noteBook.currentPage()
            if graphEditor is not None:
                graphEditor.graph.saveGraph(fname)

    def onLoad(self):
        fname, _ = QtWidgets.QFileDialog.getOpenFileName(parent=self, caption="Select Graph")
        if fname:
            self.win.uiApplication.createGraphFromPath(fname)


class VortexApplicationWindow(mainwindow.MainWindow):
    def __init__(self, application, title="Vortex", width=800, height=600, parent=None):
        super(VortexApplicationWindow, self).__init__(title=title, width=width, height=height, parent=parent, showOnInitialize=False)
        self.uiApplication = application
        self.noteBook = graphnotebook.GraphNotebook(self.uiApplication, parent=self)
        self.setCustomCentralWidget(self.noteBook)
        self.uiApplication.loadPlugins()
