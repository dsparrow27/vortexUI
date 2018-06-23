from zoo.libs.pyqt.widgets import mainwindow
from vortex.ui import graphnotebook


class ApplicationWindow(mainwindow.MainWindow):
    def __init__(self, applicationModel, title="Vortex", width=1920, height=1080, icon="", parent=None,
                 showOnInitialize=True):
        super(ApplicationWindow, self).__init__(title, width, height, icon, parent, showOnInitialize)
        self.setObjectName("VortexMainWindow")
        self.setupMenuBar()
        self.noteBook = graphnotebook.GraphNotebook(parent=self)
        self.setCustomCentralWidget(self.noteBook)
        self.noteBook.bindApplication(applicationModel)