from zoo.libs.plugin import plugin


class UIPlugin(plugin.Plugin):
    def __init__(self, application, manager):
        super(UIPlugin, self).__init__(manager=manager)
        self.application = application

    def initializeWidget(self):
        return
