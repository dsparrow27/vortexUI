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
        self.gridSize = 25
        self.panelWidth = 150
        self.drawMainGridAxis = False
        self.connectionLineWidth = 2
        self.drawPointsGrid = True
        self.graphBackgroundColor = QtGui.QColor(35, 44, 51)
        self.gridColor = QtGui.QColor(113, 124, 135)

        self.defaultConnectionStyle = connectionStyle["SolidLine"]
        self.defaultConnectionShape = connectionStyle["Cubic"]

        self.attributeMapping = {
            'quaternion': {"colour": QtGui.QColor(230,115,115)},
            'colour': {"colour": QtGui.QColor(130, 217, 159)},
            'matrix4': {"color": QtGui.QColor(230,115,115)},
            'multi': {"colour": QtGui.QColor(230, 115, 115)},
            'vector2D': {"colour": QtGui.QColor(130, 217, 159)},
            'vector3D': {"colour": QtGui.QColor(130, 217, 159)},
            "file": {"colour": QtGui.QColor(217, 190, 108)},
            "directory": {"colour": QtGui.QColor(217, 190, 108)},
            "boolean": {"colour": QtGui.QColor(230, 153, 99)},
            "dict": {"colour": QtGui.QColor(204.0, 127.5, 163.20000000000002)},
            "float": {"colour": QtGui.QColor(168, 217, 119)},
            "integer": {"colour": QtGui.QColor(98, 207, 217)},
            "list": {"colour": QtGui.QColor(56.000040000000006, 47.99992500000001, 45.00010500000001)},
            "string": {"colour": QtGui.QColor(217, 190, 108)}
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
