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
        if event.key() ==  QtCore.Qt.Key_Escape:
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
        # self.view.deletePress.connect(self.onDelete)

    def tabPress(self, point):
        registeredItems = self.uiApplication.registerdNodes()
        if not registeredItems:
            raise ValueError("No registered nodes to display")
        self.box = PopupCompleter(point, registeredItems, parent=self)
        # self.box.itemSelected.connect(self.uiApplication.)
        self.box.itemSelected.connect(self.onCreateNode)

    def onCreateNode(self, Type):
        objectModel = self.uiApplication.onNodeCreated(Type)
        # if objectModel is not None:
        #     graphNode = graphicsnode.GraphicsNode(objectModel)
        #     self.scene.addItem(graphNode)

    def setGraph(self, graphWidget):
        self.graphWidget = graphWidget
        self.view.graphWidget = self.graphWidget
        self.graphWidget.setGeometry(0, 0, self.view.size().width(), self.view.size().height())
        self.scene.addItem(self.graphWidget)

    def showPanels(self, state):
        self.graphWidget.showPanels(state)

    def init(self):
        self.editorLayout = QtWidgets.QVBoxLayout()
        self.editorLayout.setContentsMargins(0, 0, 0, 0)
        self.editorLayout.setSpacing(0)
        # constructor view and set scene
        self.scene = graphicsscene.GraphicsScene(parent=self)

        self.view = View(self.graphWidget, self.uiApplication.config, parent=self)
        self.view.setScene(self.scene)
        # add the view to the layout
        self.editorLayout.addWidget(self.view)
        self.setLayout(self.editorLayout)


class View(graphicsview.GraphicsView):
    onTabPress = QtCore.Signal(object)

    def __init__(self, graphWidget, config, parent=None, setAntialiasing=True):
        super(View, self).__init__(config, parent, setAntialiasing)
        self.graphWidget = graphWidget
        self.newScale = None
        self.updateRequested.connect(self.rescaleGraphWidget)

    def resizeEvent(self, event):
        super(View, self).resizeEvent(event)
        size = event.size()
        self.setSceneRect(0, 0, size.width(), size.height())
        if self.graphWidget:
            pos = self.mapToScene(0, 0)
            self.graphWidget.setGeometry(pos.x(), pos.y(), size.width(), size.height())

    def rescaleGraphWidget(self):
        if self.graphWidget:
            self.graphWidget.setPos(self.mapToScene(0, 0))
            self.graphWidget.resize(self.size())


class GraphWidget(QtWidgets.QGraphicsWidget):
    def __init__(self, showPanels=True, parent=None):
        super(GraphWidget, self).__init__(parent)
        self._showPanels = showPanels
        self.rightPanel = None
        self.leftPanel = None
        layout = QtWidgets.QGraphicsLinearLayout(parent=self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setOrientation(QtCore.Qt.Horizontal)
        self.setFlag(QtWidgets.QGraphicsWidget.ItemIgnoresTransformations)
        self.setLayout(layout)
        self.showPanels(showPanels)

    def showPanels(self, state):
        if state and self.leftPanel is None and self.rightPanel is None:
            self.leftPanel = graphpanels.Panel(maximumWidth=200, parent=self)
            self.rightPanel = graphpanels.Panel(maximumWidth=200, parent=self)
            layout = self.layout()
            layout.addItem(self.leftPanel)
            layout.addStretch(1)
            layout.addItem(self.rightPanel)

        elif not state:
            if self.leftPanel is not None:
                self.layout().takeAt(self.leftPanel)
            if self.rightPanel is not None:
                self.layout().takeAt(self.leftPanel)
