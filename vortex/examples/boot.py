import logging
import os
import sys
import pprint
from vortex import startup

startup.initialize()

from Qt import QtGui, QtWidgets, QtCore
from vortex import api as vortexApi
from vortex.examples import datamodel

if __name__ == "__main__":
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    app = QtWidgets.QApplication(sys.argv)
    from zoo.libs.pyqt import stylesheet
    stylesheet.loadDefaultFonts()

    uiConfig = datamodel.Config()
    vortexApp = vortexApi.UIApplication(uiConfig)
    ui = vortexApi.ApplicationWindow(vortexApp)
    vortexApp.registerGraphType(datamodel.Graph)
    vortexApp.createGraphFromPath(os.path.join(os.environ["VORTEX"], "vortex/examples/example.vgrh"))

    # logger.debug("Completed boot process")

    sys.exit(app.exec_())
