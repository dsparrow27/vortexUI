from zoovendor.Qt import QtWidgets, QtCore
from zoo.libs.pyqt.widgets import elements


class BaseNodeWidget(QtWidgets.QWidget):
    def __init__(self, objectModel, parent=None):
        super(BaseNodeWidget, self).__init__(parent=parent)
        self.objectModel = objectModel
        layout = elements.vBoxLayout(self)
        self.mainLayout = layout

        for model in objectModel.attributes(outputs=False):
            wid = objectModel.config.attributeWidgetForType(model.type())
            if wid is not None:
                layout.addWidget(wid(model, parent=self),alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter )
