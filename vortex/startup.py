import os


def initialize():
    from zoo.core import api
    if api.currentConfig() is None:
        cfg = api.zooFromPath(os.environ["ZOOTOOLS_ROOT"])
        cfg.resolver.resolveFromPath(cfg.resolver.environmentPath())
        from zoo.core.util import zlogging
        zlogging.setGlobalDebug(True)
    from zoo.libs.utils import env
    vortexRoot = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    os.environ["VORTEX"] = vortexRoot
    env.addToEnv("ZOO_ICON_PATHS", [os.path.join(vortexRoot, "icons")])
    env.addToEnv("VORTEX_UI_PLUGINS", [os.path.join(vortexRoot, "vortex", "plugins", "ui")])
