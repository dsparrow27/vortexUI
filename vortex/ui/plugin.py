"""Base Module to handle UI Plugins

Class: UIPlugin()
"""

from zoo.libs.plugin import plugin


class UIPlugin(plugin.Plugin):
    """Base Plugin for UI, a UI Plugin allows the client to implement their own UI widgets and attach it
    to the MainWindow. To Initialize a widget you should overload initializeWidget()
    """
    def __init__(self, application, manager=None):
        """SubClasses that implement this method need to call super().

        :param application: The Vortex Application handler
        :type application: ::class:`Vortex.application.UIApplication`
        :param manager: The manager object for plugins
        :type manager: ::class:`zoo.libs.plugin.pluginmanager.PluginManager`
        """
        super(UIPlugin, self).__init__(manager=manager)
        self.application = application

    def initializeWidget(self):
        """
        :return:
        :rtype: ::class`qt.QtWidget` or None
        """
        return
