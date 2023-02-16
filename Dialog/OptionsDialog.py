#!/usr/bin/env python

import sys
from PyQt5.QtGui import QColor, QFont, QPalette, QPen, QBrush
from PyQt5.QtWidgets import QDialog, QMessageBox, QColorDialog, QFontDialog
from PyQt5.QtCore import QSettings
from PyQt5.QtCore import pyqtSignal as QSignal

from Dialog.ui_optionsdialog import Ui_OptionsDialog


class OptionsDialog(QDialog):
    accepted = QSignal()

    def __init__(self, fileName=None):
        super(OptionsDialog, self).__init__()
        self.ui = Ui_OptionsDialog()
        self.ui.setupUi(self)
        
        self.readSettings()
        self.writeSettings()

    def show(self):
        self.readSettings()
        super(OptionsDialog, self).show()
        
    def accept(self):
        self.writeSettings()
        self.accepted.emit()
        super(OptionsDialog, self).hide()
        
    def readSettings(self):
        settings = QSettings()
        
        self.setColor(self.ui.lbHighlightingColor, QColor(settings.value("HighlightingColor", QColor(0xff, 0xff, 0x99, 0xff))))
        self.setColor(self.ui.lbAddressAreaColor, QColor(settings.value("AddressAreaColor", QColor(0xd4, 0xd4, 0xd4, 0xff))))
        self.setColor(self.ui.lbSelectionColor, QColor(settings.value("SelectionColor", QColor(0x99, 0xff, 0x99, 0xff))))
        self.ui.leWidgetFont.setFont(QFont(settings.value("WidgetFont", QFont("Monospace", 12))))

        if sys.version_info >= (3, 0): # determine Python version
            self.ui.sbAddressAreaWidth.setValue(int(settings.value("AddressAreaWidth", 4)))
            self.ui.sbBytesPerLine.setValue(int(settings.value("BytesPerLine", 16)))
            self.ui.cbAddressArea.setChecked(settings.value("AddressArea", 'true')=='true')
            self.ui.cbAsciiArea.setChecked(settings.value("AsciiArea", 'true')=='true')
            self.ui.cbHighlighting.setChecked(settings.value("Highlighting", 'true')=='true')
            self.ui.cbOverwriteMode.setChecked(settings.value("OverwriteMode", 'true')=='true')
            self.ui.cbReadOnly.setChecked(settings.value("ReadOnly", 'false')=='true')

        else:
            self.ui.sbAddressAreaWidth.setValue(settings.value("AddressAreaWidth", 4).toInt()[0])
            self.ui.cbAddressArea.setChecked(settings.value("AddressArea", True).toBool())
            self.ui.cbAsciiArea.setChecked(settings.value("AsciiArea", True).toBool())
            self.ui.cbHighlighting.setChecked(settings.value("Highlighting", True).toBool())
            self.ui.cbOverwriteMode.setChecked(settings.value("OverwriteMode", True).toBool())
            self.ui.cbReadOnly.setChecked(settings.value("ReadOnly", False).toBool())


    def writeSettings(self):
        settings = QSettings()
        if sys.version_info >= (3, 0):
            def b(b):
                if b: return 'true'
                else: return 'false'
            settings.setValue("AddressArea", b(self.ui.cbAddressArea.isChecked()))
            settings.setValue("AsciiArea", b(self.ui.cbAsciiArea.isChecked()))
            settings.setValue("Highlighting", b(self.ui.cbHighlighting.isChecked()))
            settings.setValue("OverwriteMode", b(self.ui.cbOverwriteMode.isChecked()))
            settings.setValue("ReadOnly", b(self.ui.cbReadOnly.isChecked()))
        else:
            settings.setValue("AddressArea", self.ui.cbAddressArea.isChecked())
            settings.setValue("AsciiArea", self.ui.cbAsciiArea.isChecked())
            settings.setValue("Highlighting", self.ui.cbHighlighting.isChecked())
            settings.setValue("OverwriteMode", self.ui.cbOverwriteMode.isChecked())
            settings.setValue("ReadOnly", self.ui.cbReadOnly.isChecked())
        
        settings.setValue("HighlightingColor", self.ui.lbHighlightingColor.palette().color(QPalette.Background))
        settings.setValue("AddressAreaColor", self.ui.lbAddressAreaColor.palette().color(QPalette.Background))
        settings.setValue("SelectionColor", self.ui.lbSelectionColor.palette().color(QPalette.Background))
        settings.setValue("WidgetFont", self.ui.leWidgetFont.font())
        
        settings.setValue("AddressAreaWidth", self.ui.sbAddressAreaWidth.value())
        settings.setValue("BytesPerLine", self.ui.sbBytesPerLine.value())
        
    def reject(self):
        super(OptionsDialog, self).hide()
        
    def setColor(self, label, color):
        palette = label.palette()
        palette.setColor(QPalette.Background, color)
        label.setPalette(palette)
        label.setAutoFillBackground(True)

    def on_pbHighlightingColor_pressed(self):
        color = QColorDialog.getColor(self.ui.lbHighlightingColor.palette().color(QPalette.Highlight), self)
        if color.isValid():
            self.setColor(self.ui.lbHighlightingColor, color)
        
    def on_pbAddressAreaColor_pressed(self):
        color = QColorDialog.getColor(self.ui.lbAddressAreaColor.palette().color(QPalette.Background), self)
        if color.isValid():
            self.setColor(self.ui.lbAddressAreaColor, color)
        
    def on_pbSelectionColor_pressed(self):
        color = QColorDialog.getColor(self.ui.lbSelectionColor.palette().color(QPalette.Background), self)
        if color.isValid():
            self.setColor(self.ui.lbSelectionColor, color)
        
    def on_pbWidgetFont_pressed(self):
        font, ok = QFontDialog().getFont(self.ui.leWidgetFont.font(), self)
        if ok:
            self.ui.leWidgetFont.setFont(font)
