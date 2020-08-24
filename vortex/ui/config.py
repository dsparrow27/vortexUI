from Qt import QtCore, QtGui
from zoo.libs.pyqt.widgets.graphics import graphviewconfig

# from vortex.vortexmodel import attributewidgets

connectionStyle = {"SolidLine": QtCore.Qt.SolidLine,
                   "DashLine": QtCore.Qt.DashLine,
                   "DotLine": QtCore.Qt.DotLine,
                   "DashDotLine": QtCore.Qt.DashDotLine,
                   "DashDotDotLine": QtCore.Qt.DashDotDotLine,
                   "Linear": "Linear",
                   "Cubic": "Cubic"}


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
        self.defaultConnectionShape = connectionStyle["Cubic"]

        self.attributeMapping = {
            'quaternion': {"colour": QtGui.QColor(126.999945, 24.999944999999997, 24.999944999999997)},
            'colour': {"colour": QtGui.QColor(22.999980000000015, 255, 255)},
            'matrix4': {"color": QtGui.QColor(174.99987000000002, 130.00001999999998, 114.99990000000001)},
            'multi': {"colour": QtGui.QColor(25, 25, 25)},
            'vector2D': {"colour": QtGui.QColor(147.000105, 102.0, 156.000075)},
            'vector3D': {"colour": QtGui.QColor(184.99994999999998, 126.999945, 184.99994999999998)},
            "file": {"colour": QtGui.QColor(184.99994999999998, 126.999945, 184.99994999999998)},
            "directory": {"colour": QtGui.QColor(184.99994999999998, 126.999945, 184.99994999999998)},
            "boolean": {"colour": QtGui.QColor(38.00010000000001, 73.99998000000001, 114.000045)},
            "dict": {"colour": QtGui.QColor(204.0, 127.5, 163.20000000000002)},
            "float": {"colour": QtGui.QColor(133.000095, 102.0, 147.99996000000002)},
            "integer": {"colour": QtGui.QColor(133.000095, 102.0, 147.99996000000002)},
            "list": {"colour": QtGui.QColor(56.000040000000006, 47.99992500000001, 45.00010500000001)},
            "string": {"colour": QtGui.QColor(244.9999965, 214.999935, 59.99997)}
        }

    def registerAttributeWidget(self, attributeType, widget):
        self.attributeMapping.setdefault(attributeType, {})["widget"] = widget

    def registerAttributeColor(self, attributeType, colour):
        self.attributeMapping.setdefault(attributeType, {})["colour"] = QtGui.QColor(colour)

    def registeredNodes(self):
        return {}

    def attributeWidgetForType(self, attributeType):
        widget = self.attributeMapping.get(attributeType, {}).get("widget")
        if widget is None:
            raise TypeError("Missing attributeType: {}".format(attributeType))
        return widget
