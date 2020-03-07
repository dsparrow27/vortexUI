from Qt import QtCore, QtGui
from zoo.libs.pyqt.widgets.graphics import graphviewconfig

# from vortex.vortexmodel import attributewidgets

connectionStyle = {"SolidLine": QtCore.Qt.SolidLine,
                   "DashLine": QtCore.Qt.DashLine,
                   "DotLine": QtCore.Qt.DotLine,
                   "DashDotLine": QtCore.Qt.DashDotLine,
                   "DashDotDotLine": QtCore.Qt.DashDotDotLine,
                   "linear": 1,
                   "cubic": 0}


class VortexConfig(graphviewconfig.Config):
    def __init__(self):
        super(VortexConfig, self).__init__()
        self.connectionStyles = connectionStyle
        self.panelWidth = 150
        self.drawMainGridAxis = False
        self.connectionLineWidth = 2
        self.graphBackgroundColor = QtGui.QColor(45, 45, 45)
        self.gridColor = QtGui.QColor(0.0, 0.0, 0.0)
        self.defaultConnectionStyle = connectionStyle["SolidLine"]
        self.defaultConnectionShape = connectionStyle["cubic"]

        self.attributeMapping = {
            'quaternion': {"color": QtGui.QColor(126.999945, 24.999944999999997, 24.999944999999997),
                           "widget": None},
            'color': {"color": QtGui.QColor(22.999980000000015, 255, 255)},
            'matrix4': {
                "color": QtGui.QColor(174.99987000000002, 130.00001999999998, 114.99990000000001)},
            'multi': {"color": QtGui.QColor(25, 25, 25)},
            'vector2D': {"color": QtGui.QColor(147.000105, 102.0, 156.000075)},
            'vector3D': {"color": QtGui.QColor(184.99994999999998, 126.999945, 184.99994999999998)},
            "file": {"color": QtGui.QColor(184.99994999999998, 126.999945, 184.99994999999998),
                     "widget": None},
            "directory": {"color": QtGui.QColor(184.99994999999998, 126.999945, 184.99994999999998),
                          "widget": None},
            "boolean": {"color": QtGui.QColor(38.00010000000001, 73.99998000000001, 114.000045)},
            "dict": {"color": QtGui.QColor(204.0, 127.5, 163.20000000000002)},
            "float": {"color": QtGui.QColor(133.000095, 102.0, 147.99996000000002),
                      "widget": None},
            "integer": {"color": QtGui.QColor(133.000095, 102.0, 147.99996000000002),
                        "widget": None},
            "list": {"color": QtGui.QColor(56.000040000000006, 47.99992500000001, 45.00010500000001)},
            "string": {"color": QtGui.QColor(244.9999965, 214.999935, 59.99997),
                       "widget": None}
        }

    def registeredNodes(self):
        return {}
