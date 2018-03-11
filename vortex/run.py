import logging
import sys
from zoo.libs.pyqt.widgets import mainwindow
from vortex.ui import graphnotebook
from vortex.ui import application
from zoo.libs.pyqt.widgets.graphics import graphviewconfig

from qt import QtWidgets, QtCore

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(levelname)s: %(module)s: %(lineno)s:%(message)s"))
logger.addHandler(handler)
_instance = None


def standalone():
    app = QtWidgets.QApplication(sys.argv)
    uiConfig = graphviewconfig.Config()
    uiapp = application.UIApplication(uiConfig, None)
    win = mainwindow.MainWindow()
    book = graphnotebook.GraphNotebook(uiapp, win)
    win.setCustomCentralWidget(book)
    sys.exit(app.exec_())


def embed():
    global _instance
    try:
        _instance.close()
    except:
        pass

    book = graphnotebook.GraphNotebook()
    _instance = book
    return book

# console = user level interactation
# uiSide(rightclick etc) -> objectModel
# uiApplication -> application
# tab->graphBook->
