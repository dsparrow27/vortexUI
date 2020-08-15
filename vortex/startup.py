import os


def initialize():
    from zoo.core import api
    if api.currentConfig() is None:
        cfg = api.zooFromPath(os.environ["ZOOTOOLS_ROOT"])
        cfg.resolver.resolveFromPath(cfg.resolver.environmentPath())
