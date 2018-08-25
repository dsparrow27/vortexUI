import os

from zoo.libs.pyqt.widgets import mainwindow
from vortex.ui import graphnotebook
from qt import QtWidgets

from zoo.libs.pyqt import stylesheet

styleKeys = {
    "$BTN_BACKGROUND_COLOR": "5D5D5D",
    "$DISABLED_COLOR": "454545",
    "$HOVER_BACKGROUND_COLOR": "5D5D5D",
    "$MAIN_BACKGROUND_COLOR": "111111",
    "$MAIN_FOREGROUND_COLOR": "C6C6C6",
    "$SECONDARY_BACKGROUND_COLOR": "353535",
    "$STACKITEM_BACKGROUND_COLOR": "5D5D5D",
    "$VIEW_BACKGROUND_COLOR": "1C1C1C",
}

style = stylesheet.StyleSheet.fromPath(os.path.join(os.path.dirname(__file__), "style.qss"), **styleKeys)


class ApplicationWindow(mainwindow.MainWindow):
    def __init__(self, applicationModel, title="Vortex", width=1920, height=1080, icon="", parent=None,
                 showOnInitialize=True):
        super(ApplicationWindow, self).__init__(title, width, height, icon, parent, showOnInitialize)
        self.setObjectName("VortexMainWindow")
        self.setStyleSheet(style.data)
        self.noteBook = graphnotebook.GraphNotebook(parent=self)
        self.setCustomCentralWidget(self.noteBook)
        self.noteBook.bindApplication(applicationModel)
        self.setupMenuBar()
        self.loadAction = QtWidgets.QAction("Load", parent=self)
        self.saveAction = QtWidgets.QAction("Save", parent=self)
        self.recentFilesMenu = QtWidgets.QMenu("Recent Files", parent=self)

        self.fileMenu.insertAction(self.exitAction, self.saveAction)
        self.fileMenu.insertAction(self.exitAction, self.loadAction)
        self.fileMenu.insertMenu(self.exitAction, self.recentFilesMenu)
        self.saveAction.triggered.connect(self.onSave)
        self.loadAction.triggered.connect(self.onLoad)

    def onSave(self):
        fname, _ = QtWidgets.QFileDialog.getSaveFileName(parent=self, caption="Select Graph")
        if fname:
            self.noteBook.uiApplication.save(fname)

    def onLoad(self):
        fname, _ = QtWidgets.QFileDialog.getOpenFileName(parent=self, caption="Select Graph")
        if fname:
            self.noteBook.uiApplication.load(fname)
