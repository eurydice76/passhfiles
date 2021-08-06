import collections
import io
import logging
import os
import paramiko
import socket
import sys
import yaml

from PyQt5 import QtCore, QtWidgets

from bastion_browser.models.LocalFileSystemModel import LocalFileSystemModel
from bastion_browser.models.RemoteFileSystemModel import RemoteFileSystemModel
from bastion_browser.utils.Platform import sessionsDatabasePath
from bastion_browser.views.FileSystemTableView import FileSystemTableView
from bastion_browser.views.SessionTreeView import SessionTreeView
from bastion_browser.widgets.LoggerWidget import LoggerWidget

class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, parent=None):

        super(MainWindow, self).__init__(parent)

        self._init_ui()

        self.loadSessions()

    def _build_menu(self):
        """Build the menu.
        """

        menubar = self.menuBar()

        fileMenu = menubar.addMenu('&Session')

        addSessionAction = QtWidgets.QAction('&Add Session', self)
        addSessionAction.setStatusTip('Open ssh session dialog')
        addSessionAction.triggered.connect(self._sessionListView.onAddSession)
        fileMenu.addAction(addSessionAction)

        saveSessionsAction = QtWidgets.QAction('&Save Session(s)', self)
        saveSessionsAction.setStatusTip('Save current sessions')
        saveSessionsAction.triggered.connect(self.onSaveSessions)
        fileMenu.addAction(saveSessionsAction)

        clearSessionsAction = QtWidgets.QAction('&Clear Session(s)', self)
        clearSessionsAction.setStatusTip('Clear all sessions')
        clearSessionsAction.triggered.connect(self.onClearSessions)
        fileMenu.addAction(clearSessionsAction)

        restoreSessionsAction = QtWidgets.QAction('&Restore Session(s)', self)
        restoreSessionsAction.setStatusTip('Clear all sessions')
        restoreSessionsAction.triggered.connect(self.onLoadSessions)
        fileMenu.addAction(restoreSessionsAction)

        fileMenu.addSeparator()

        exitAction = QtWidgets.QAction('&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit')
        exitAction.triggered.connect(self.onQuitApplication)
        fileMenu.addAction(exitAction)

    def _init_ui(self):

        self._mainFrame = QtWidgets.QFrame(self)
        
        self._sessionListView = SessionTreeView()

        self._serversComboBox = QtWidgets.QComboBox()

        self._sourceFileSystem = FileSystemTableView()

        self._targetFileSystem = FileSystemTableView()

        self._splitter = QtWidgets.QSplitter()
        self._splitter.addWidget(self._sourceFileSystem)
        self._splitter.addWidget(self._targetFileSystem)

        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(self._sessionListView)
        hlayout.addWidget(self._splitter, stretch=2)

        logger = LoggerWidget(self)
        logger.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(logger)

        self.setCentralWidget(self._mainFrame)

        mainLayout = QtWidgets.QVBoxLayout()

        mainLayout.addLayout(hlayout, stretch=4)
        mainLayout.addWidget(logger.widget, stretch=1)

        self.setGeometry(0, 0, 1400, 800)

        self._mainFrame.setLayout(mainLayout)

        self._sessionListView.openBrowsers.connect(self.onOpenBrowsers)

        self._build_menu()

        self.show()

        logging.getLogger().setLevel(logging.INFO)

    def loadSessions(self):

        sessionsPath = sessionsDatabasePath()
        if not os.path.exists(sessionsPath):
            return

        with open(sessionsPath,'r') as fin:
            sessions = yaml.unsafe_load(fin)

        sessionsModel = self._sessionListView.model()
        sessionsModel.clear()

        for session in sessions:
            self._sessionListView.addSession(session)

        logging.info('Sessions successfully loaded')

    def onClearSessions(self):

        sessionModel = self._sessionListView.model()
        sessionModel.clear()

    def onLoadSessions(self):

        self.loadSessions()

    def onOpenBrowsers(self, sshSession, server):

        fileSystemModel = LocalFileSystemModel(sshSession, server, '.')
        self._sourceFileSystem.setModel(fileSystemModel)
        self._sourceFileSystem.horizontalHeader().setSectionResizeMode(3,QtWidgets.QHeaderView.ResizeToContents)

        remoteFileSystemModel = RemoteFileSystemModel(sshSession, server, '/')
        self._targetFileSystem.setModel(remoteFileSystemModel)
        self._targetFileSystem.horizontalHeader().setSectionResizeMode(3,QtWidgets.QHeaderView.ResizeToContents)


    def onQuitApplication(self):
        """Event called when the application is exited.
        """

        choice = QtWidgets.QMessageBox.question(
            self, 'Quit', "Do you really want to quit?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if choice == QtWidgets.QMessageBox.Yes:
            sys.exit()

    def onSaveSessions(self):

        sessionModel = self._sessionListView.model()
        currentSessions = [sessionModel.data(sessionModel.index(i,0),QtCore.Qt.UserRole) for i in range(sessionModel.rowCount())]
        
        with open(sessionsDatabasePath(),'w') as fout:
            yaml.dump(currentSessions,fout)

        logging.info('Sessions saved to {}'.format(sessionsDatabasePath()))

    @property
    def sessionListView(self):
        return self._sessionListView
