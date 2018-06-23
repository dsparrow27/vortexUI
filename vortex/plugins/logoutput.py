import logging

from zoo.libs.pyqt.widgets import logoutput
from vortex.ui import plugin
from qt import QtCore


class Logger(plugin.UIPlugin):
    autoLoad = True
    id = "Logger"
    creator = "David Sparrow"

    def initializeWidget(self):
        window = self.application.mainWindow()
        self.logout = logoutput.OutputLogDialog("Log output", parent=self.application.mainWindow())
        handler = logoutput.QWidgetHandler()
        handler.addWidget(self.logout)
        for logger in logging.Logger.manager.loggerDict.values():
            try:
                logger.addHandler(handler)
            except AttributeError:
                continue
        window.createDock(self.logout, QtCore.Qt.RightDockWidgetArea, tabify=False)
