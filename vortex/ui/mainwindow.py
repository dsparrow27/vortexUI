from functools import partial

from vortex.ui.views import graphnotebook

from zoovendor.Qt import QtWidgets, QtCore
from zoo.libs.pyqt.widgets import mainwindow
from zoo.libs.pyqt.widgets import elements
from zoo.libs import iconlib
from zoo.libs.pyqt.widgets import flowtoolbar


class ApplicationWindow(elements.ZooWindow):

    def __init__(self, application, title="Vortex v0.0.1", parent=None, width=800, height=600):
        super(ApplicationWindow, self).__init__(title=title, parent=parent, width=width, height=height,
                                                minButton=True, maxButton=True, show=False)
        layout = elements.vBoxLayout()
        self.setMainLayout(layout)
        self.win = VortexApplicationWindow(application, parent=self)
        layout.addWidget(self.win)
        titleBtn = self.titleBar.logoButton
        self.newAction = titleBtn.addAction("New", connect=self.onNew)
        self.loadAction = titleBtn.addAction("Load", connect=self.onLoad)
        self.saveAction = titleBtn.addAction("Save", connect=self.onSave)
        self.exitAction = titleBtn.addAction("Close", icon=iconlib.icon("close"), connect=self.close)
        self.exitAction.setShortcut("Ctrl+Q")
        self.exitAction.setToolTip("Closes application")

        self._menuBar = Toolbar(parent=self)
        self.titleBar.contentsLayout.addWidget(self._menuBar)
        actions = []
        for plugin in application.pluginManager.plugins.values():
            actions.append((plugin.id, partial(self._onLoadView, plugin.id)))

        self._menuBar.addToolMenu("displayOptions", "Views",
                                  actions=actions,
                                  iconColor=(192, 192, 192))
        self.show()

    def _onLoadView(self, pluginId):
        self.win.uiApplication.loadUIPlugin(pluginId)

    def onNew(self):
        self.win.uiApplication.createNewGraph()

    def onSave(self):
        fname, _ = QtWidgets.QFileDialog.getSaveFileName(parent=self, caption="Select Graph")
        if fname:
            graphEditor = self.win.noteBook.currentEditor()
            if graphEditor is not None:
                graphEditor.graph.saveGraph(fname)

    def onLoad(self):
        fname, _ = QtWidgets.QFileDialog.getOpenFileName(parent=self, caption="Select Graph")
        if fname:
            self.win.uiApplication.createGraphFromPath(fname)


class VortexApplicationWindow(mainwindow.MainWindow):
    def __init__(self, application, title="Vortex", width=800, height=600, parent=None):
        super(VortexApplicationWindow, self).__init__(title=title, width=width, height=height,
                                                      parent=parent,
                                                      showOnInitialize=False)
        self.uiApplication = application
        self.noteBook = graphnotebook.GraphNotebook(self.uiApplication, parent=self)
        self.setCustomCentralWidget(self.noteBook)
        self.uiApplication.loadPlugins()


class Toolbar(flowtoolbar.FlowToolBar):
    def __init__(self, parent=None, menuIndicatorIcon="arrowmenu", iconSize=20, iconPadding=2):
        super(Toolbar, self).__init__(parent, menuIndicatorIcon, iconSize, iconPadding)
