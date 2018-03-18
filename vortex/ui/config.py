from zoo.libs.pyqt.widgets.graphics import graphviewconfig


class VortexConfig(graphviewconfig.Config):
    def __init__(self):
        super(VortexConfig, self).__init__()
        self.panelWidthPercentage = 0.05
        self.drawMainGridAxis = False
