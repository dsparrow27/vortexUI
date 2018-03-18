import logging
import sys

from vortex import slithermodel
from vortex.ui import graphnotebook
from vortex.ui import config

from qt import QtWidgets, QtCore

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(levelname)s: %(module)s: %(lineno)s:%(message)s"))
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

    uiConfig = config.VortexConfig()

    app = slithermodel.Application(uiConfig)
    ui = graphnotebook.GraphNotebook()
    ui.bindApplication(app)
    ui.resize(2000, 2500)
    ui.show()

    _instance = ui
    return ui


if __name__ == "__main__":
    standalone()
