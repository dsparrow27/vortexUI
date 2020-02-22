import os


def initialize():
    from zoo.core import api
    cfg = api.zooFromPath(os.environ["ZOOTOOLS_ROOT"])
    cfg.resolver.resolveFromPath(cfg.resolver.environmentPath())