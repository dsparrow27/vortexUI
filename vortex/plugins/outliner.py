from vortex.ui import plugin
from qt import QtCore, QtWidgets


class AttributeEditorPlugin(plugin.UIPlugin):
    id = "Outliner"
    type = "Widget"
    autoLoad = True
    creator = "David Sparrow"

    def initializeWidget(self):
        window = self.application.mainWindow()
        self.outliner = QtWidgets.QFrame(parent=window)
        window.createDock(self.outliner, QtCore.Qt.LeftDockWidgetArea)
        return self.outliner