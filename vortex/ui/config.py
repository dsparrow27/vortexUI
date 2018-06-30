from qt import QtCore, QtGui
from zoo.libs.pyqt.widgets.graphics import graphviewconfig

connectionStyle = {"SolidLine": QtCore.Qt.SolidLine,
                   "DashLine": QtCore.Qt.DashLine,
                   "DotLine": QtCore.Qt.DotLine,
                   "DashDotLine": QtCore.Qt.DashDotLine,
                   "DashDotDotLine": QtCore.Qt.DashDotDotLine,
                   "linear": 5,
                   "cubic": 6}


class VortexConfig(graphviewconfig.Config):
    def __init__(self):
        super(VortexConfig, self).__init__()
        self.connectionStyles = connectionStyle
        self.panelWidth = 150
        self.drawMainGridAxis = False
        self.connectionLineWidth = 2
        self.defaultConnectionStyle = connectionStyle["SolidLine"]
        self.defaultConnectionShape = connectionStyle["cubic"]
