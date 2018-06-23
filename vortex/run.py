import logging
import sys

import os

from vortex.ui import config

from qt import QtWidgets, QtCore

logger = logging.getLogger("VortexUI")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

_instance = None


def standalone():
    app = QtWidgets.QApplication(sys.argv)
    win = embed()
    win.show()
    sys.exit(app.exec_())


def embed():
    global _instance
    try:
        _instance.close()
    except:
        pass
    os.environ["VORTEX_UI_PLUGINS"] = r"E:\code\python\personal\vortexUI\vortex\plugins"
    logger.debug("Starting boot process")
    print os.environ["VORTEX_UI_PLUGINS"]
    from vortex.ui import mainwindow
    from slither.vortexmodel import slithermodel  # temp just for proto
    uiConfig = config.VortexConfig()
    app = slithermodel.Application(uiConfig)
    ui = mainwindow.ApplicationWindow(app)
    app.loadPlugins()
    logger.debug("Completed boot process")

    _instance = ui
    return ui


if __name__ == "__main__":
    standalone()
