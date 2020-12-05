"""Base Module to handle UI Plugins

Class: UIPlugin()
"""

from zoo.libs.plugin import plugin
from Qt import QtCore


class UIPlugin(plugin.Plugin):
    """Base Plugin for UI, a UI Plugin allows the client to implement their own UI widgets and attach it
    to the MainWindow. To Initialize a widget you should overload initializeWidget()
    """
    dockArea = QtCore.Qt.LeftDockWidgetArea
    autoLoad = False
    tabify = True

    def __init__(self, application, manager=None):
        """SubClasses that implement this method need to call super().

        :param application: The Vortex Application handler
        :type application: ::class:`Vortex.graph.ModehModel`
        :param manager: The manager object for plugins
        :type manager: ::class:`zoo.libs.plugin.pluginmanager.PluginManager`
        """
        super(UIPlugin, self).__init__(manager=manager)
        self.application = application
        self._widget = None

    @property
    def widget(self):
        return self._widget

    def hide(self):
        try:
            self._widget.hide()
        except Exception:
            pass

    def initUI(self, dock=True):
        """Internal use only
        :return:
        :rtype:
        """
        if self._widget:
            print("advsdvsdvdfbdb")
            # self._widget.show()
            # return
        window = self.application.mainWindow()
        print(">>>>>>>>>>>>>>>>>>>>>>", window)
        widget = self.show(window)
        if dock and window:
            window.createDock(widget, self.dockArea, tabify=self.tabify)
        self._widget = widget

    def show(self, parent):
        """
        :return:
        :rtype: ::class`Qt.QtWidget` or None
        """
        raise NotImplementedError
