from qt import QtWidgets, QtCore
from zoo.libs.pyqt.widgets import mainwindow
from vortex.ui import graphnotebook, attributeeditor


class ApplicationWindow(mainwindow.MainWindow):
    def __init__(self, applicationModel, title="", width=600, height=800, icon="", parent=None, showOnInitialize=True):
        super(ApplicationWindow, self).__init__(title, width, height, icon, parent, showOnInitialize)
        self.noteBook = graphnotebook.GraphNotebook(parent=self)
        self.setCustomCentralWidget(self.noteBook)
        self.attributeEditor = attributeeditor.AttributeEditor(applicationModel, parent=self)
        self.createDock(self.attributeEditor, QtCore.Qt.RightDockWidgetArea)

        self.noteBook.bindApplication(applicationModel)