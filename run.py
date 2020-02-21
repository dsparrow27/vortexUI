import logging
import os
import sys

logger = logging.getLogger("VortexUI")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

_instance = None


def standalone():
    global _instance

    sys.path.append(os.path.join(os.environ["ZOOTOOLS_ROOT"], "install", "core", "python"))
    from zoo.core import api
    cfg = api.zooFromPath(os.environ["ZOOTOOLS_ROOT"])
    cfg.resolver.resolveFromPath(cfg.resolver.environmentPath())
    from Qt import QtWidgets, QtCore
    app = QtWidgets.QApplication(sys.argv)
    app.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    _instance = embed()
    # print(_instance)
    _instance.show()
    sys.exit(app.exec_())


def embed():
    global _instance
    try:
        _instance.close()
    except:
        pass
    os.path.join(os.environ["ZOOTOOLS_ROOT"], "install", "core", "python")
    from zoo.core import api
    cfg = api.zooFromPath(os.environ["ZOOTOOLS_ROOT"])
    cfg.resolver.resolveFromPath(cfg.resolver.environmentPath())
    from zoo.preferences.core import preference
    logger.debug("Starting boot process")
    from vortex.ui import config
    from vortex.ui import mainwindow, application
    from vortex.ui import grapheditor
    from vortex.vortexmodel import slithermodel  # temp just for proto
    stylesheet = preference.interface("core_interface").stylesheet().data
    from Qt import QtCore

    uiConfig = config.VortexConfig()
    app = slithermodel.Application(uiConfig)
    app.loadPlugins()
    ui = mainwindow.ApplicationWindow(app)

    nodes = [
        {"data": {"label": "float1", "category": "math", "secondaryLabel": "bob", "script": "", "commands": [],
                  "description": ""}},
        {"data": {"label": "float2", "category": "math", "secondaryLabel": "bob", "script": "", "commands": [],
                  "description": ""}},
        {"data": {"label": "sum", "category": "math", "secondaryLabel": "bob", "script": "", "commands": [],
                  "description": ""},
         },
        {"data": {"label":"searchAndReplace", "category": "strings",
                  "secondaryLabel": "bob", "script": "", "commands": [],
                  "description": ""},
         "attributes": [{"label": "search", "isInput": True, "type": "string", "isOutput": True},
                        {"label": "toReplace", "isInput": True, "type": "string", "isOutput": True},
                        {"label": "replace", "isInput": True, "type": "string", "isOutput": True},
                        {"label": "result", "isInput": False, "type": "string", "isOutput": True}]},

    ]
    root = slithermodel.SlitherUIObject(uiConfig, None)
    # add a tab te the notebook
    editor = ui.noteBook.addPage(root)
    ui.setStyleSheet(stylesheet)
    # add a bunch of nodes to the root
    for n in nodes:
        editor.scene.createNode(slithermodel.SlitherUIObject(uiConfig, parent=root, **n), QtCore.QPoint(10, 0))

    logger.debug("Completed boot process")

    _instance = ui
    return ui


if __name__ == "__main__":
    standalone()
