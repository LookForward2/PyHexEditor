from PyQt5 import QtCore
from PyQt5.QtWidgets import QDialog, QMessageBox

from Dialog.ui_searchdialog import Ui_SearchDialog


class SearchDialog(QDialog):
    def __init__(self, parent, hexEdit):
        super(SearchDialog, self).__init__()
        self.ui = Ui_SearchDialog()
        self.ui.setupUi(self)
        self._hexEdit = hexEdit
        
    def findNext(self):
        startIdx = self._hexEdit.cursorPosition // 2
        findBa = self.getContent(self.ui.cbFindFormat.currentIndex(), self.ui.cbFind.currentText())
        idx = -1
        
        if len(findBa) > 0:
            if self.ui.cbBackwards.isChecked():
                idx = self._hexEdit.lastIndexOf(findBa, startIdx)
            else:
                idx = self._hexEdit.indexOf(findBa, startIdx)
        
        return idx
        
    @QtCore.pyqtSlot()
    def on_pbFind_clicked(self):
        self.findNext()
        
    @QtCore.pyqtSlot()
    def on_pbReplace_clicked(self):
        idx = self.findNext()
        if idx >= 0:
            replaceBa = self.getContent(self.ui.cbReplaceFormat.currentIndex(), self.ui.cbReplace.currentText())
            self.replaceOccurrence(idx, replaceBa)
            
    @QtCore.pyqtSlot()
    def on_pbReplaceAll_clicked(self):
        replaceCounter = 0
        idx = 0
        goOn = QMessageBox.Yes
        
        while (idx >= 0) and (goOn == QMessageBox.Yes):
            idx = self.findNext()
            if idx >= 0:
                replaceBa = self.getContent(self.ui.cbReplaceFormat.currentIndex(), self.ui.cbReplace.currentText())
                result = self.replaceOccurrence(idx, replaceBa)
                
                if result == QMessageBox.Yes:
                    replaceCounter += 1
                    
                if result == QMessageBox.Cancel:
                    goOn = QMessageBox.Cancel
                    
        if replaceCounter > 0:
            QMessageBox.information(self, "QHexEdit", "%s occurrences replaced" % replaceCounter)
            
    def getContent(self, comboIndex, inputStr) -> bytes:
        if comboIndex == 0:     # hex
            findBa = bytes.fromhex(inputStr)
        elif comboIndex == 1:   # text
            findBa = bytes(inputStr, encoding = "utf-8")
        else:
            findBa = bytes()
        return findBa   
    
    def replaceOccurrence(self, idx, replaceBa):
        result = QMessageBox.Yes
        
        if len(replaceBa) >= 0:
            if self.ui.cbPrompt.isChecked():
                result = QMessageBox.question(self, "QHexEdit", "Replace occurrence?", 
                             QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
                
                if result == QMessageBox.Yes:
                    self._hexEdit.replace(idx, replaceBa)
                    self._hexEdit.update()
                    
            else:
                self._hexEdit.replace(idx, replaceBa)
                    
        return result

        