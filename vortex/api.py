import sys
from vortex import startup
startup.initialize()
del startup

from .ui.model.graphmodel import GraphModel
from .ui.model.objectmodel import ObjectModel
from .ui.model.attributemodel import AttributeModel
from .ui.config import VortexConfig
from .ui.plugin import UIPlugin
from .ui.mainwindow import ApplicationWindow
from .ui.uiapplication import UIApplication
from zoo.libs.pyqt import stylesheet
from Qt import QtWidgets, QtCore


def createWindow(application, graphType, config, parent=None):
    if application is None:
        vortexApp = UIApplication(config())
    else:
        vortexApp = application(config())
    ui = ApplicationWindow(vortexApp, parent=parent)
    vortexApp.registerGraphType(graphType)
    return ui, vortexApp


def standalone(application, graphType, config, filePath=None):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    app = QtWidgets.QApplication(sys.argv)
    stylesheet.loadDefaultFonts()
    win, vortexApplication = createWindow(application, graphType, config, parent=None)
    if filePath:
        vortexApplication.createGraphFromPath(filePath)
    sys.exit(app.exec_())


def maya(application, graphType, config, parent=None):
    from zoo.libs.maya.qt import mayaui
    ui, _ = createWindow(application, graphType, config, parent=parent or mayaui.getMayaWindow())
    return ui
