import os
import weakref

from Qt import QtWidgets, QtCore
from zoo.libs.pyqt import uiconstants
from zoo.libs.pyqt.widgets import elements


class StringWidget(elements.StringEdit):

    def __init__(self, model, parent=None):
        super(StringWidget, self).__init__(model.text(), model.value(), enableMenu=False, parent=parent)
        self.model = weakref.ref(model)
        self.textModified.connect(model.setValue)


class PathWidget(QtWidgets.QFrame):
    def __init__(self, model, parent=None):
        super(PathWidget, self).__init__(parent=parent)
        self.directory = False
        self.model = weakref.ref(model)
        self.layout = elements.hBoxLayout(parent=self)
        self.edit = elements.LineEdit(parent=self)
        self.layout.addWidget(self.edit)
        self.browserBtn = elements.styledButton("",
                                                "browse",
                                                toolTip="Browse",
                                                parent=self,
                                                minWidth=uiconstants.BTN_W_ICN_MED)
        self.layout.addWidget(self.browserBtn)
        self.browserBtn.clicked.connect(self.onBrowserClicked)
        self.edit.editingFinished.connect(self.onEditChanged)

    def onBrowserClicked(self):
        currentPath = self.edit.text()
        if not os.path.isfile(currentPath):
            currentPath = os.path.dirname(currentPath)
        if not self.directory:
            fileName, _ = QtWidgets.QFileDialog.getOpenFileName(parent=self, dir=currentPath)
        else:
            fileName = QtWidgets.QFileDialog.getExistingDirectory(parent=self, dir=currentPath)
        if fileName:
            self.edit.setText(fileName)
            self.model.setValue(fileName)

    def onEditChanged(self):
        self.model.setValue(str(self.edit.text()))


class DirectoryWidget(PathWidget):
    def __init__(self, model, parent=None):
        super(DirectoryWidget, self).__init__(model, parent=parent)
        self.directory = True


class NumericAttributeWidget(QtWidgets.QFrame):
    valueChanged = QtCore.Signal(object)

    def __init__(self, model, parent=None):
        super(NumericAttributeWidget, self).__init__(parent=parent)
        self.model = weakref.ref(model)
        layout = elements.hBoxLayout()
        self.setLayout(layout)

        self.slider = elements.FloatSlider(
            label=model.text(),
            defaultValue=model.default(),
            parent=self,
            toolTip=model.description(),
            sliderMin=model.min(),
            sliderMax=model.max(), sliderAccuracy=200, enableMenu=False, editBox=True, labelRatio=1,
            editBoxRatio=1, sliderRatio=1, labelBtnRatio=1, decimalPlaces=3, orientation=QtCore.Qt.Horizontal,
            dynamicMin=False, dynamicMax=False)
        self.slider.numSliderMajorChange.connect(self.setValue)
        layout.addWidget(self.slider)
        self.slider.setValue(model.value())

    def setValue(self):
        value = self.slider.value()
        ref = self.model()
        if ref is not None and ref.value() != value:
            ref.setValue(value)
