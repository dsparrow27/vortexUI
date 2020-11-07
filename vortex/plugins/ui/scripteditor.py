import logging
import os
import sys

from zoo.libs.pyqt.extended import pythoneditor
from zoo.libs.pyqt.widgets import logoutput
from zoo.libs.pyqt.widgets import elements
from zoo.libs.pyqt.syntaxhighlighter import highlighter
from vortex import api
from Qt import QtCore, QtWidgets


class XStream(QtCore.QObject):
    """https://stackoverflow.com/questions/24469662/how-to-redirect-logger-output-into-pyQt-text-widget
    """
    _stdout = None
    _stderr = None
    messageWritten = QtCore.Signal(str)

    def flush(self):
        pass

    def fileno(self):
        return -1

    def write(self, msg):
        if not self.signalsBlocked():
            self.messageWritten.emit(str(msg.strip()))

    @staticmethod
    def stdout():
        if not XStream._stdout:
            XStream._stdout = XStream()
            sys.stdout = XStream._stdout
        return XStream._stdout

    @staticmethod
    def stderr():
        if not XStream._stderr:
            XStream._stderr = XStream()
            sys.stderr = XStream._stderr
        return XStream._stderr


class ScriptEditor(api.UIPlugin):
    autoLoad = False
    id = "ScriptEditor"
    creator = "David Sparrow"
    dockArea = QtCore.Qt.BottomDockWidgetArea

    def show(self, parent):
        self.editorParent = QtWidgets.QWidget(parent=parent)
        self.editorParent.setObjectName("ScriptEditor")
        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        self.layout = elements.vBoxLayout(parent=self.editorParent)
        self.layout.addWidget(self.splitter)
        self.editor = pythoneditor.TabbedEditor(parent=parent)
        self.editor.setObjectName("Script Editor")
        self.editor.addNewEditor("New Tab", variables={"app": self.application})
        self.logout = logoutput.OutputLogDialog("History", parent=parent)

        self.pythonHighlighter = highlighter.highlighterFromJson(os.path.join(os.path.dirname(highlighter.__file__),
                                                                              "highlightdata.json"),
                                                                 self.logout.document())
        handler = logoutput.QWidgetHandler()
        handler.addWidget(self.logout)
        for logger in logging.Logger.manager.loggerDict.values():
            try:
                logger.addHandler(handler)
            except AttributeError:
                continue
        self.splitter.addWidget(self.logout)
        self.splitter.addWidget(self.editor)
        self.editor.outputText.connect(self.outputText)
        XStream.stdout().messageWritten.connect(self.logout.insertPlainText)
        XStream.stderr().messageWritten.connect(self.logout.logError)

        return self.editorParent

    def outputText(self, text):
        logger = self.logout
        if logger is not None:
            logger.write(text)

    def uiInstance(self):
        try:
            return self.editorParent
        except AttributeError:
            return
