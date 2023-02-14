from PyQt5.QtWidgets import QMainWindow, QMenu, QToolBar, QAction, QLabel, QMessageBox, QFileDialog
from PyQt5.QtGui import QCloseEvent, QDragEnterEvent, QDropEvent, QIcon, QKeySequence
from PyQt5.QtCore import QFile, QSize, QFileInfo, QSettings, QSaveFile, QTextStream
from Dialog.OptionsDialog import OptionsDialog
from App.QHexEdit import QHexEdit


class QHexWindow(QMainWindow):
    def __init__(self, name='PyHexEditor'):
        super().__init__()

        self.appName = name

        self.currentFile = str()
        self.isUntitled = False

        self.hexEdit = QHexEdit(self)

        self.file = QFile()
        self.fileMenu = QMenu()
        self.editMenu = QMenu()
        self.helpMenu = QMenu()
        self.labelSize = QLabel()
        self.fileToolBar = QToolBar()
        self.editToolBar = QToolBar()
        self.undoAction = QAction()
        self.redoAction = QAction()
        self.openAction = QAction()
        self.saveAction = QAction()
        self.exitAction = QAction()
        self.findAction = QAction()
        self.aboutAction = QAction()
        self.closeAction = QAction()
        self.saveAsAction = QAction()
        self.saveReadableAction = QAction()
        self.aboutQtAction = QAction()
        self.optionsAction = QAction()
        self.findNextAction = QAction()
        self.saveReadableSelectionAction = QAction()
        self.optionsDialog = OptionsDialog(self)

        self.setAcceptDrops(True)
        self.init()
        #self.setFixedSize(QSize(1200, 600))
        self.setMinimumSize(QSize(770, 390))
        self.show()

    def closeEvent(self, event: QCloseEvent) -> None:
        self.hexEdit.undoStack.clear()
        self.writeSettings()

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.accept()

    def dropEvent(self, event: QDropEvent) -> None:
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            filepath = urls[0].toLocalFile()
            self.loadFile(filepath)
            event.accept()

    def about(self):
        QMessageBox.about(self, self.appName, 'Hexadecimal Viewer')

    def aboutQt(self):
        QMessageBox.aboutQt(self, self.appName)

    def dataChanged(self):
        self.setWindowModified(self.hexEdit.isModified())

    def open(self):
        options = QFileDialog().Options()
        options |= QFileDialog.DontUseNativeDialog
        filename, _ = QFileDialog.getOpenFileName(self, "Select File", options=options)
        if filename:
            self.loadFile(filename)

    def optionsAccepted(self):
        self.writeSettings()
        self.readSettings()

    def findNext(self):
        pass

    def save(self):
        if self.isUntitled:
            self.saveAs()
        else:
            self.saveFile(self.currentFile)

    def saveAs(self):
        filename, _ = QFileDialog.getSaveFileName(self, 'Save As...', self.currentFile)
        if len(filename) == 0:
            return False

        return self.saveFile(filename)

    def saveSelectionReadable(self):
        filters = "Text files (*.txt);;All files (*.*)"
        defFilter = '*.txt'
        defSuffix = defFilter[1:]
        dialog = QFileDialog()
        dialog.setDefaultSuffix(defSuffix)
        filename, _ = dialog.getSaveFileName(self, 'Save As Readable...', \
            self.currentFile.rsplit('.')[0] + defSuffix, filter=filters, initialFilter=defFilter)
        return self.saveSelectionReadableFile(filename)

    def saveReadable(self):
        filters = "Text files (*.txt);;All files (*.*)"
        defFilter = '*.txt'
        defSuffix = defFilter[1:]
        dialog = QFileDialog()
        dialog.setDefaultSuffix(defSuffix)
        filename, _ = dialog.getSaveFileName(self, 'Save As Readable...', \
            self.currentFile.rsplit('.')[0] + defSuffix, filter=filters, initialFilter=defFilter)
        return self.saveReadableFile(filename)

    def setAddress(self):
        pass

    def setOverwriteMode(self):
        pass

    def setSize(self, size):
        self.labelSize.setText(str(size))

    def showOptionsDialog(self):
        pass

    def showSearchDialog(self):
        pass

    def undo(self):
        self.hexEdit.undo()

    def redo(self):
        self.hexEdit.redo()

    # noinspection PyUnresolvedReferences
    def init(self):
        self.optionsDialog.accepted.connect(self.optionsAccepted)
        self.hexEdit.dataChanged.connect(self.dataChanged)
        self.hexEdit.overwriteModeChanged.connect(self.setOverwriteMode)

        self.setUnifiedTitleAndToolBarOnMac(True)
        self.setCentralWidget(self.hexEdit)
        self.createActions()
        self.createMenus()
        self.createStatusBar()
        self.createToolBars()
        self.readSettings()

    # noinspection PyUnresolvedReferences
    def createActions(self):
        self.openAction = QAction(QIcon('Icons/MenuOpen.svg'), '&Open', self)
        self.openAction.setStatusTip('Open a existing file')
        self.openAction.setShortcut(QKeySequence.Open)
        self.openAction.triggered.connect(self.open)

        self.saveAction = QAction(QIcon('Icons/MenuSaveAll'), '&Save', self)
        self.saveAction.setStatusTip('Save the file')
        self.saveAction.setShortcut(QKeySequence.Save)
        self.saveAction.triggered.connect(self.save)

        self.saveAsAction = QAction('Save &As...', self)
        self.saveAsAction.setStatusTip('Save the file as ...')
        self.saveAsAction.setShortcut(QKeySequence.SaveAs)
        self.saveAsAction.triggered.connect(self.saveAs)

        self.saveReadableAction = QAction('Save &Readable', self)
        self.saveReadableAction.setStatusTip('Save the file as readable ...')
        self.saveReadableAction.triggered.connect(self.saveReadable)

        self.exitAction = QAction('E&xit', self)
        self.exitAction.setStatusTip('Exit the program')
        self.exitAction.setShortcut(QKeySequence.Close)
        self.exitAction.triggered.connect(self.close)

        self.undoAction = QAction(QIcon('Icons/Undo.svg'), '&Undo', self)
        self.undoAction.setStatusTip('Undo last changes')
        self.undoAction.setShortcut(QKeySequence.Undo)
        self.undoAction.triggered.connect(self.undo)

        self.redoAction = QAction(QIcon('Icons/Redo.svg'), '&Redo', self)
        self.redoAction.setStatusTip('Redo last changes')
        self.redoAction.setShortcut(QKeySequence.Redo)
        self.redoAction.triggered.connect(self.redo)
        
        self.saveReadableSelectionAction = QAction('Save Selection Readable', self)
        self.saveReadableSelectionAction.setStatusTip('Save selection as readable ...')
        self.saveReadableSelectionAction.triggered.connect(self.saveSelectionReadable)        

        self.aboutAction = QAction('&About', self)
        self.aboutAction.setStatusTip('About the program')
        self.aboutAction.triggered.connect(self.about)

        self.aboutQtAction = QAction('About &Qt', self)
        self.aboutQtAction.setStatusTip('About the program')
        self.aboutQtAction.triggered.connect(self.aboutQt)

        self.findAction = QAction(QIcon('Icons/Find.svg'), '&Find/Replace', self)
        self.findNextAction = QAction('Find &Next', self)
        self.optionsAction = QAction('&Options', self)

    def createMenus(self):
        self.fileMenu = self.menuBar().addMenu('&File')
        self.fileMenu.addAction(self.openAction)
        self.fileMenu.addAction(self.saveAction)
        self.fileMenu.addAction(self.saveAsAction)
        self.fileMenu.addAction(self.saveReadableAction)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitAction)

        self.editMenu = self.menuBar().addMenu('&Edit')
        self.editMenu.addAction(self.undoAction)
        self.editMenu.addAction(self.redoAction)

        self.editMenu.addAction(self.saveReadableSelectionAction)
        self.editMenu.addSeparator()
        # self.editMenu.addAction(self.findAction)
        # self.editMenu.addAction(self.findNextAction)
        self.editMenu.addSeparator()
        # self.editMenu.addAction(self.optionsAction)

        self.helpMenu = self.menuBar().addMenu('&Help')
        self.helpMenu.addAction(self.aboutAction)
        self.helpMenu.addAction(self.aboutQtAction)

    def createStatusBar(self):
        self.statusBar().addPermanentWidget(QLabel('Address:'))
        labelAddress = QLabel()
        labelAddress.setMinimumWidth(70)
        self.statusBar().addPermanentWidget(labelAddress)

        self.statusBar().addPermanentWidget(QLabel('Size:'))
        self.labelSize.setMinimumWidth(70)
        self.statusBar().addPermanentWidget(self.labelSize)
        self.hexEdit.currentSizeChanged.connect(self.setSize)

        self.statusBar().addPermanentWidget(QLabel('Mode:'))
        labelOverwriteMode = QLabel()
        labelOverwriteMode.setMinimumWidth(70)
        self.statusBar().addPermanentWidget(labelOverwriteMode)

        self.statusBar().showMessage('Ready', 2000)

    def createToolBars(self):
        self.fileToolBar = self.addToolBar('File')
        self.fileToolBar.setIconSize(QSize(16, 16))
        self.fileToolBar.addAction(self.openAction)
        self.fileToolBar.addAction(self.saveAction)

        self.editToolBar = self.addToolBar('Edit')
        self.editToolBar.setIconSize(QSize(16, 16))
        self.editToolBar.addAction(self.undoAction)
        self.editToolBar.addAction(self.redoAction)
        # self.editToolBar.addAction(self.findAction)

    def loadFile(self, filename: str):
        self.file.setFileName(filename)
        if not self.hexEdit.setDataDevice(self.file):
            QMessageBox.warning(self, "Hex",
                                f"Cannot read the file {filename}: {self.file.errorString()}.")
        self.setCurrentFile(filename)
        self.statusBar().showMessage('File Loaded', 2000)

    def readSettings(self):
        pass

    def saveFile(self, filename: str):
        data_to_save = self.hexEdit.chunks.data(0, -1)
        newfile = QSaveFile(filename)
        if not newfile.open(QSaveFile.WriteOnly | QSaveFile.Truncate):
            QMessageBox.warning(self, self.appName,
                                f"Cannot open file {filename} for writing: {newfile.errorString()}.")
            return False
        newfile.write(data_to_save)
        if newfile.commit():
            self.setCurrentFile(filename)
            self.statusBar().showMessage('File Saved', 2000)
            return True
        else:
            QMessageBox.warning(self, self.appName,
                                f"Cannot write file {filename}: {newfile.errorString()}.")
            return False

    def saveReadableFile(self, filename: str):
        readable_data = self.hexEdit.toReadableString()
        file = QFile(filename)
        file.open(QFile.WriteOnly | QFile.Text)
        out = QTextStream(file)
        out << readable_data
        file.close()

    def saveSelectionReadableFile(self, filename: str):
        readable_data = self.hexEdit.selectionToReadableString()
        file = QFile(filename)
        file.open(QFile.WriteOnly | QFile.Text)
        out = QTextStream(file)
        out << readable_data
        file.close()

    def setCurrentFile(self, filename: str):
        self.currentFile = QFileInfo(filename).canonicalFilePath()
        isUntitled = len(self.currentFile) == 0
        self.setWindowModified(False)
        if isUntitled:
            self.setWindowFilePath(self.appName)
        else:
            self.setWindowFilePath(self.currentFile + " - " + self.appName)

    @staticmethod
    def strippedName(fullFilename: str) -> str:
        return QFileInfo(fullFilename).fileName()

    def writeSettings(self):
        settings = QSettings()
        settings.setValue("pos", self.pos())
        settings.setValue("size", self.size())
