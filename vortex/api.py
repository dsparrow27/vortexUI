from .ui.model.graphmodel import GraphModel
from .ui.model.objectmodel import ObjectModel
from .ui.model.attributemodel import AttributeModel
from .ui.config import VortexConfig
from .ui.plugin import UIPlugin
from .ui.mainwindow import ApplicationWindow
from .ui.uiapplication import UIApplication
from Qt import QtWidgets, QtCore
from zoo.libs.pyqt import stylesheet
import sys


def createWindow(graphType, config, parent=None):
    vortexApp = UIApplication(config())
    ui = ApplicationWindow(vortexApp, parent=parent)
    vortexApp.registerGraphType(graphType)
    return ui, vortexApp


def standalone(graphType, config, filePath=None):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    app = QtWidgets.QApplication(sys.argv)
    stylesheet.loadDefaultFonts()
    win, vortexApplication = createWindow(graphType, config, parent=None)
    if filePath:
        vortexApplication.createGraphFromPath(filePath)
    sys.exit(app.exec_())


def maya(graphType, config, parent=None):
    from zoo.libs.maya.qt import mayaui
    ui, _ = createWindow(graphType, config, parent=parent or mayaui.getMayaWindow())
    return ui
