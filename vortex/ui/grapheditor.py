from qt import QtWidgets, QtCore

from zoo.libs.pyqt.widgets.graphics import graphicsview
from zoo.libs.pyqt.widgets.graphics import graphicsscene
from zoo.libs.pyqt.extended import combobox
from vortex.ui.graphics import graphpanels
from vortex.ui.graphics import graphicsnode


class PopupCompleter(combobox.ExtendedComboBox):
    itemSelected = QtCore.Signal(str)

    def __init__(self, position, items, parent):
        super(PopupCompleter, self).__init__(items, parent)
        self.move(position)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Popup);
        self.setSizeAdjustPolicy(self.AdjustToContents)
        self.show()

    def keyPressEvent(self, event):
        super(PopupCompleter, self).keyPressEvent(event)
        if event.key() == QtCore.Qt.Key_Escape:
            self.close()
            self.parent().setFocus()
        elif event.key() in (QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return):
            self.itemSelected.emit(self.currentText())
            self.close()
            self.parent().setFocus()


class GraphEditor(QtWidgets.QWidget):
    def __init__(self, uiApplication, parent=None):
        super(GraphEditor, self).__init__(parent=parent)
        self.graphWidget = None
        self.uiApplication = uiApplication
        self.init()
        self.view.tabPress.connect(self.tabPress)
        self.view.deletePress.connect(self.onDelete)

    def tabPress(self, point):
        registeredItems = self.uiApplication.registeredNodes()
        if not registeredItems:
            raise ValueError("No registered nodes to display")
        registeredItems.append("Group")
        self.box = PopupCompleter(point, registeredItems, parent=self)

        self.box.itemSelected.connect(self.onLibraryRequestNode)

    def onLibraryRequestNode(self, Type):

        if Type == "Group":
            from zoo.libs.pyqt.widgets.graphics import graphbackdrop
            drop = graphbackdrop.BackDrop("test backdrop")
            self.scene.addItem(drop)
        else:
            self.uiApplication.onNodeCreated(Type)

    def showPanels(self, state):
        self.view.showPanels(state)

    def onDelete(self):
        print "deleting"

    def init(self):
        self.editorLayout = QtWidgets.QVBoxLayout()
        self.editorLayout.setContentsMargins(0, 0, 0, 0)
        self.editorLayout.setSpacing(0)
        # constructor view and set scene
        self.scene = graphicsscene.GraphicsScene(parent=self)

        self.view = View(self.uiApplication.config, parent=self)
        self.view.setScene(self.scene)
        # add the view to the layout
        self.editorLayout.addWidget(self.view)
        self.setLayout(self.editorLayout)


class View(graphicsview.GraphicsView):
    onTabPress = QtCore.Signal(object)

    def __init__(self, config, parent=None, setAntialiasing=True):
        super(View, self).__init__(config, parent, setAntialiasing)
        self.newScale = None
        self.updateRequested.connect(self.rescaleGraphWidget)
        self.leftPanel = None
        self.rightPanel = None

    def showPanels(self, state):
        if state and self.leftPanel is None and self.rightPanel is None:
            self.leftPanel = graphpanels.Panel(maximumWidth=200)
            self.rightPanel = graphpanels.Panel(maximumWidth=200)
            self.scene().addItem(self.leftPanel)
            self.scene().addItem(self.rightPanel)

        elif not state:
            if self.leftPanel is not None:
                self.layout().takeAt(self.leftPanel)
            if self.rightPanel is not None:
                self.layout().takeAt(self.leftPanel)

    def resizeEvent(self, event):
        """Override to rescale the side panels"""
        super(View, self).resizeEvent(event)
        size = event.size()
        self.setSceneRect(0, 0, size.width(), size.height())
        if self.leftPanel:
            pos = self.mapToScene(0, 0)
            self.leftPanel.setGeometry(pos.x(), pos.y(), 200, size.height())
        if self.rightPanel:
            pos = self.mapToScene(size.width(), 0)
            self.rightPanel.setGeometry(size.width() - 200, pos.y(), 200, size.height())

    def mouseMoveEvent(self, event):
        """ Overriden to rescale the side panels
        """
        super(View, self).mouseMoveEvent(event)
        self.rescaleGraphWidget()

    def rescaleGraphWidget(self):
        size = self.size()
        width = size.width()
        if self.rightPanel:
            scenePosition = self.mapToScene(width - 200, 0)
            self.rightPanel.setPos(scenePosition)
        if self.leftPanel:
            scenePosition = self.mapToScene(0, 0)
            self.leftPanel.setPos(scenePosition)
