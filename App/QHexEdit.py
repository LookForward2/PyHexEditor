from PyQt5.QtWidgets import QWidget, QAbstractScrollArea, QApplication
from PyQt5.QtGui import QColor, QFont, QResizeEvent, QPaintEvent, QMouseEvent, QKeyEvent, QPainter, QPalette, QPen, \
    QBrush, QKeySequence
from PyQt5.QtCore import QByteArray, QIODevice, QPoint, QRect, Qt, QTimer
from PyQt5.QtCore import pyqtSignal as QSignal
from App.Chunks import Chunks
from App.UndoStack import UndoStack


class QHexEdit(QAbstractScrollArea):
    """
    QHexEdit is a binary editor widget for Qt.

    :brief: It is a simple editor for binary data, just like QPlainTextEdit is
    for text data.

    QHexEdit takes the data of a QByteArray (setData()) and shows it. You can use
    the mouse or the keyboard to navigate inside the widget. If you hit the keys
    (0..9, a..f) you will change the data. Changed data is highlighted and can be
    accessed via data().

    Normally QHexEdit works in the overwrite mode. You can set overwrite mode(false)
    and insert data. In this case the size of data() increases. It is also possible
    to delete bytes (del or backspace), here the size of data decreases.

    You can select data with keyboard hits or mouse movements. The copy-key will
    copy the selected data into the clipboard. The cut-key copies also but deletes
    it afterwards. In overwrite mode, the paste function overwrites the content of
    the (does not change the length) data. In insert mode, clipboard data will be
    inserted. The clipboard content is expected in ASCII Hex notation. Unknown
    characters will be ignored.

    QHexEdit comes with undo/redo functionality. All changes can be undone, by
    pressing the undo-key (usually ctr-z). They can also be redone afterwards.
    The undo/redo framework is cleared, when setData() sets up a new
    content for the editor. You can search data inside the content with indexOf()
    and lastIndexOf(). The replace() function is to change located subdata. This
    'replaced' data can also be undone by the undo/redo framework.

    QHexEdit is based on QIODevice, that's why QHexEdit can handle big amounts of
    data. The size of edited data can be more then two gigabytes without any
    restrictions.
    """

    dataChanged = QSignal()
    currentSizeChanged = QSignal(int)
    overwriteModeChanged = QSignal(bool)
    currentAddressChanged = QSignal(int)

    # noinspection PyUnresolvedReferences
    def __init__(self, parent: QWidget = None):
        """
        Creates an instance of QHexEdit.
        :param parent: Parent widget of QHexEdit.
        """
        super().__init__(parent)

        self.addressArea = True
        """
        Property address area switch the address area on or off. Set addressArea true
        (show it), false (hide it).
        """

        self.addressWidth = 4
        """
        Set and get the minimum width of the address area, width in characters.
        """

        self.addressOffset = 0
        """
        Property addressOffset is added to the Numbers of the Address Area.
        A offset in the address area (left side) is sometimes useful, whe you show
        only a segment of a complete memory picture. With setAddressOffset() you set
        this property - with addressOffset() you get the current value.
        """

        self.asciiArea = True
        """
        Switch the ascii area on (true, show it) or off (false, hide it).
        """

        self.overwriteMode = True
        """
        Property overwrite mode sets (setOverwriteMode()) or gets (overwriteMode()) the mode
        in which the editor works. In overwrite mode the user will overwrite existing data. The
        size of data will be constant. In insert mode the size will grow, when inserting
        new data.
        """

        self.highlighting = True
        """
        Switch the highlighting feature on or of: true (show it), false (hide it).
        """

        self.readOnly = False
        """
        Property readOnly sets (setReadOnly()) or gets (isReadOnly) the mode
        in which the editor works. In readonly mode the the user can only navigate
        through the data and select data; modifying is not possible. This
        property's default is false.
        """

        self.cursorPosition = 0
        """
        Property cursorPosition sets or gets the position of the editor cursor
        in QHexEdit. Every byte in data has two cursor positions: the lower and upper
        Nibble. Maximum cursor position is factor two of data.size().
        """

        #self.absoluteCursorPosition = 0
        """
        Absolute position of cursor, 1 Byte == 2 tics.
        """

        self.lastEventSize = 0
        self.hexCharInLine = 47
        self.bytesPerLine = 16
        """
        Set and get bytes number per line.
        """

        self.editAreaIsAscii = False
        """
        Flag about the ascii mode edited.
        """

        self.hexCaps = False
        """
        That property defines if the hex values looks as a-f if the value is false(default)
        or A-F if value is true.
        """

        self.dynamicBytesPerLine = False
        """
        Property defines the dynamic calculation of bytesPerLine parameter 
        depends of width of widget. set this property true to avoid horizontal
        scrollbars and show the maximal possible data. defalut value is false.
        """

        self.blink = True
        """
        Help get cursor blinking.
        """

        self.modified = True
        self.addressDigit = 0
        """
        Real no of addressdigits, may be > addressWidth.
        """

        self.rowsShown = 0

        # Name Convention: pixel position start with px
        self.pxCharWidth = 0
        self.pxCharHeight = 0
        self.pxPosHexX = 0
        self.pxPosAdrX = 0
        self.pxPosAsciiX = 0
        self.pxGapAdr = 0
        self.pxGapAdrHex = 0
        self.pxGapHexAscii = 0
        self.pxCursorWidth = 0
        self.pxSelectionSub = 0
        self.pxCursorX = 0
        self.pxCursorY = 0

        # Name Convention: absolute byte position in chunks start with b
        self.bSelectionBegin = 0
        self.bSelectionEnd = 0
        self.bSelectionInit = 0
        self.bPosFirst = 0
        self.bPosLast = 0
        self.bPosCurrent = 0

        self.chunks = Chunks(self)
        """
        IODevice based access to data.
        """

        self.__font = QFont()
        """
        Set the font of the widget. Please use fixed width fonts like Mono or Courier.
        """

        self.data = bytearray()
        """
        Property data holds the content of QHexEdit. Call setData() to set the
        content of QHexEdit, data() returns the actual content. When calling setData()
        with a QByteArray as argument, QHexEdit creates a internal copy of the data
        If you want to edit big files please use setData(), based on QIODevice.
        """

        self.cursorRect = QRect()
        self.penSelection = QPen()
        self.cursorTimer = QTimer()
        """
        For blinking cursor.
        """

        self.penHighlighted = QPen()
        self.undoStack = UndoStack(self.chunks, self)
        self.dataShown = bytearray()
        self.brushSelection = QBrush()
        self.hexDataShow = str()
        self.markedShown = bytearray()
        self.brushHighlighted = QBrush()

        self.highlightingColor = QColor(0xff, 0xff, 0x99, 0xff)
        self.brushHighlighted.setColor(self.highlightingColor)
        self.selectionColor = QColor(0x99, 0xff, 0x99, 0xff)
        #self.brushSelection.setColor(Qt.green)
        self.brushSelection.setColor(self.selectionColor)

        """
        Property highlighting color sets (setHighlightingColor()) the background
        color of highlighted text areas. You can also read the color
        (highlightingColor()).
        """

        self.selectionColor = self.palette().highlight().color()
        """
        Property selection color sets (setSelectionColor()) the background
        color of selected text areas. You can also read the color
        (selectionColor()).
        """

        self.addressAreaColor = self.palette().alternateBase().color()
        """
        Property address area color sets (setAddressAreaColor()) the background
        color of address areas. You can also read the color (addressAreaColor()).
        """

        self.cursorTimer.timeout.connect(self.updateCursor)
        self.cursorTimer.setInterval(500)
        self.cursorTimer.start()

        self.verticalScrollBar().valueChanged.connect(self.adjust)
        self.horizontalScrollBar().valueChanged.connect(self.adjust)

        self.undoStack.indexChanged.connect(self.dataChangedPrivate)

        self.setFont(QFont("Monospace", 12))

    def setAddressArea(self, addressArea: bool) -> None:
        self.addressArea = addressArea
        self.adjust()
        self.setCursorPosition(self.cursorPosition)
        self.viewport().update()

    def setAddressAreaColor(self, color: QColor) -> None:
        self.addressAreaColor = color
        self.viewport().update()

    def setAddressOffset(self, addressOffset: int) -> None:
        self.addressOffset = addressOffset
        self.adjust()
        self.setCursorPosition(self.cursorPosition)
        self.viewport().update()

    def setAddressWidth(self, width: int) -> None:
        self.adjust()
        self.setCursorPosition(self.cursorPosition)
        self.viewport().update()

    def setAsciiArea(self, asciiArea: bool) -> None:
        if not self.asciiArea:
            self.editAreaIsAscii = False
        self.asciiArea = asciiArea
        self.adjust()
        self.setCursorPosition(self.cursorPosition)
        self.viewport().update()

    def setBytesPerLine(self, count: int) -> None:
        self.bytesPerLine = count
        self.hexCharInLine = count * 3 - 1
        self.adjust()
        self.setCursorPosition(self.cursorPosition)
        self.viewport().update()

    def setCursorPosition(self, position: int) -> None:
        # 1. delete old cursor
        self.blink = False
        self.viewport().update()

        # 2. Check, if cursor in range?
        #print(f'{position = }, {self.chunks.size = }')
        if position > (self.chunks.size * 2 - 1):
            position = self.chunks.size * 2 - (1 if self.overwriteMode else 0)
        
        if position < 0:
            position = 0

        # 3. Calc new position of cursor
        self.bPosCurrent = position // 2
        self.pxCursorY = ((position // 2 - self.bPosFirst) // self.bytesPerLine + 1) * self.pxCharHeight
        x = position % (2 * self.bytesPerLine)
        if self.editAreaIsAscii:
            self.pxCursorX = x // 2 * self.pxCharWidth + self.pxPosAsciiX
            self.cursorPosition = (position >> 1) << 1 # & 0xFFFFFFFFFFFFFFFE
        else:
            self.pxCursorX = (((x // 2) * 3) + (x % 2)) * self.pxCharWidth + self.pxPosHexX
            self.cursorPosition = position

        if self.overwriteMode:
            self.cursorRect = QRect(self.pxCursorX - self.horizontalScrollBar().value(), self.pxCursorY + self.pxCursorWidth, self.pxCharWidth, self.pxCursorWidth)
        else:
            self.cursorRect = QRect(self.pxCursorX - self.horizontalScrollBar().value(), self.pxCursorY - self.pxCharHeight + 4, self.pxCursorWidth, self.pxCharHeight)

        # 4. Immediately draw new cursor
        self.blink = True
        self.viewport().update(self.cursorRect)
        self.currentAddressChanged.emit(self.bPosCurrent)

    def getCursorPosition(self, position: QPoint) -> int:
        # Calc cursor position depending on a graphical position
        posX = position.x() + self.horizontalScrollBar().value()
        posY = position.y() - 3
        if self.pxPosHexX <= posX < (self.pxPosHexX + (1 + self.hexCharInLine) * self.pxCharWidth):
            self.editAreaIsAscii = False
            x = (posX - self.pxPosHexX) // self.pxCharWidth
            x = (x // 3) * 2 + x % 3
            y = (posY // self.pxCharHeight) * 2 * self.bytesPerLine
            return self.bPosFirst * 2 + x + y
        elif self.asciiArea and self.pxPosAsciiX <= posX < (
                self.pxPosAsciiX + (1 + self.bytesPerLine) * self.pxCharWidth):
            self.editAreaIsAscii = True
            x = 2 * (posX - self.pxPosAsciiX) // self.pxCharWidth
            y = (posY // self.pxCharHeight) * 2 * self.bytesPerLine
            return self.bPosFirst * 2 + x + y
        else:
            return -1

    def setDataArray(self, array: QByteArray) -> None:
        pass

    def setDataDevice(self, device: QIODevice) -> bool:
        status = self.chunks.setIODevice(device)
        self.dataChangedPrivate()
        self.viewport().update()
        return status

    def dataAt(self, position: int, count: int) -> bytearray:
        return self.chunks.data(position, count)

    def write(self, device: QIODevice, position: int, count: int) -> bool:
        return self.chunks.write(device, position, count)

    def insert(self, index: int, array: bytes) -> None:
        self.undoStack.insert(index, array)

    def removeChar(self, index: int, length: int) -> None:
        self.undoStack.removeAt(index, length)

    def replaceChar(self, index: int, char: bytes) -> None:
        self.undoStack.overwrite(index, char[0:1]) # assert only 1 byte
        self.refresh()

    def replace(self, index: int, array: bytes) -> None: # united both replaceChar and replaceAtArray
        self.undoStack.overwrite(index, array)
        self.refresh()

    def replaceAtArray(self, position: int, length: int, array: bytes) -> None:
        self.undoStack.overwrite(position, array)
        self.refresh()

    def ensureVisible(self) -> None:
        if self.cursorPosition <= self.bPosFirst * 2:
            self.verticalScrollBar().setValue(int(self.cursorPosition / 2 / self.bytesPerLine))
        if self.cursorPosition > self.bPosFirst + (self.rowsShown - 1) * self.bytesPerLine * 2:
            self.verticalScrollBar().setValue(int(self.cursorPosition / 2 / self.bytesPerLine) - self.rowsShown + 1)
        if self.pxCursorX <= self.horizontalScrollBar().value():
            self.horizontalScrollBar().setValue(self.pxCursorX)
        if self.pxCursorX + self.pxCharWidth > self.horizontalScrollBar().value() + self.viewport().width():
            self.horizontalScrollBar().setValue(self.pxCursorX + self.pxCharWidth - self.viewport().width())
        self.viewport().update()

    def indexOf(self, array: bytes, _from: int) -> int:
        pass

    def isModified(self) -> bool:
        return self.modified

    def lastIndexOf(self, array: bytes, _from: int) -> int:
        pass

    def redo(self) -> None:
        self.undoStack.redo()
        self.setCursorPosition(self.chunks.getPos() * 1 if self.editAreaIsAscii else 2)
        self.refresh()

    def selectionToReadableString(self) -> str:
        ba = self.chunks.data(self.getSelectionBegin(), self.getSelectionEnd() - self.getSelectionBegin())
        return self.toReadable(ba)

    def selectedData(self) -> str:
        pass

    def setFont(self, font: QFont) -> None:
        newFont = QFont(font)
        newFont.setStyleHint(QFont.Monospace)
        super(QHexEdit, self).setFont(newFont)
        metrics = self.fontMetrics()
        self.pxCharWidth = metrics.width('2')
        self.pxCharHeight = metrics.height()
        self.pxGapAdr = self.pxCharWidth // 2
        self.pxGapAdrHex = self.pxCharWidth
        self.pxGapHexAscii = 2 * self.pxCharWidth
        self.pxCursorWidth = self.pxCharHeight // 7
        self.pxSelectionSub = self.pxCharHeight // 5
        self.viewport().update()

    def toReadableString(self) -> str:
        ba = self.chunks.data(0, -1)
        return self.toReadable(ba)

    def undo(self) -> None:
        self.undoStack.undo()
        self.setCursorPosition(self.chunks.getPos() * 1 if self.editAreaIsAscii else 2)
        self.refresh()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        # Use match/case statment since Python 3.10
        # Cursor movements
        if event.matches(QKeySequence.MoveToNextChar):
            pos = self.cursorPosition + (2 if self.editAreaIsAscii else 1)
            self.setCursorPosition(pos)
            self.resetSelection(pos)
        if event.matches(QKeySequence.MoveToPreviousChar):
            pos = self.cursorPosition - (2 if self.editAreaIsAscii else 1)
            self.setCursorPosition(pos)
            self.resetSelection(pos)
        if event.matches(QKeySequence.MoveToEndOfLine):
            pos = self.cursorPosition - (self.cursorPosition % (2 * self.bytesPerLine)) + (2 * self.bytesPerLine) - 1
            self.setCursorPosition(pos)
            self.resetSelection(self.cursorPosition)
        if event.matches(QKeySequence.MoveToStartOfLine):
            pos = self.cursorPosition - (self.cursorPosition % (2 * self.bytesPerLine))
            self.setCursorPosition(pos)
            self.resetSelection(self.cursorPosition)  
        if event.matches(QKeySequence.MoveToNextLine):
            pos = self.cursorPosition + (2 * self.bytesPerLine)
            self.setCursorPosition(pos)
            self.resetSelection(self.cursorPosition)    
        if event.matches(QKeySequence.MoveToPreviousLine):
            pos = self.cursorPosition - (2 * self.bytesPerLine)
            self.setCursorPosition(pos)
            self.resetSelection(self.cursorPosition)  
        if event.matches(QKeySequence.MoveToNextPage):
            pos = self.cursorPosition + (((self.rowsShown - 1) * 2 * self.bytesPerLine))
            self.setCursorPosition(pos)
            self.resetSelection(self.cursorPosition)  
        if event.matches(QKeySequence.MoveToPreviousPage):
            pos = self.cursorPosition - (((self.rowsShown - 1) * 2 * self.bytesPerLine))
            self.setCursorPosition(pos)
            self.resetSelection(self.cursorPosition)
        if event.matches(QKeySequence.MoveToEndOfDocument):
            pos = self.chunks.size * 2
            self.setCursorPosition(pos)
            self.resetSelection(self.cursorPosition)    
        if event.matches(QKeySequence.MoveToStartOfDocument):
            pos = 0
            self.setCursorPosition(pos)
            self.resetSelection(self.cursorPosition)

        # Select commands  
        if event.matches(QKeySequence.SelectAll):
            self.resetSelection(0)
            self.setSelection(2 * self.chunks.size + 1)
        if event.matches(QKeySequence.SelectNextChar):
            pos = self.cursorPosition + (2 if self.editAreaIsAscii else 1)
            self.setCursorPosition(pos)
            self.setSelection(pos)
        if event.matches(QKeySequence.SelectPreviousChar):
            pos = self.cursorPosition - (2 if self.editAreaIsAscii else 1)
            self.setCursorPosition(pos)
            self.setSelection(pos)
        
        if event.matches(QKeySequence.SelectEndOfLine):
            pos = self.cursorPosition - (self.cursorPosition % (2 * self.bytesPerLine)) + (2 * self.bytesPerLine) - 1
            self.setCursorPosition(pos)
            self.setSelection(pos)
        if event.matches(QKeySequence.SelectStartOfLine):
            pos = self.cursorPosition - (self.cursorPosition % (2 * self.bytesPerLine))
            self.setCursorPosition(pos)
            self.setSelection(pos) 
        if event.matches(QKeySequence.SelectNextLine):
            pos = self.cursorPosition + (2 * self.bytesPerLine)
            self.setCursorPosition(pos)
            self.setSelection(pos)  
        if event.matches(QKeySequence.SelectPreviousLine):
            pos = self.cursorPosition - (2 * self.bytesPerLine)
            self.setCursorPosition(pos)
            self.setSelection(pos) 
        if event.matches(QKeySequence.SelectNextPage):
            # pos = self.cursorPosition + (((self.rowsShown - 1) * 2 * self.bytesPerLine))
            pos = self.cursorPosition + (self.viewport().height() // self.pxCharHeight - 1) * 2 * self.bytesPerLine
            self.setCursorPosition(pos)
            self.setSelection(pos)
        if event.matches(QKeySequence.SelectPreviousPage):
            # pos = self.cursorPosition - (((self.rowsShown - 1) * 2 * self.bytesPerLine))
            pos = self.cursorPosition - (self.viewport().height() // self.pxCharHeight - 1) * 2 * self.bytesPerLine
            self.setCursorPosition(pos)
            self.setSelection(pos)
        if event.matches(QKeySequence.SelectEndOfDocument):
            pos = self.chunks.size * 2
            self.setCursorPosition(pos)
            self.setSelection(pos)
        if event.matches(QKeySequence.SelectStartOfDocument):
            pos = 0
            self.setCursorPosition(pos)
            self.setSelection(pos)

        # Copy
        if event.matches(QKeySequence.Copy):
            # ba = bytearray
            ba = self.chunks.data(self.getSelectionBegin(), self.getSelectionEnd() - self.getSelectionBegin())
            buf = str()
            for i in range(0, len(ba), 32): # 32 bytes in a row
                buf += ba[i:i+32].hex() + '\n'
            clipboard = QApplication.clipboard()
            print('copy\n', buf)
            clipboard.setText(buf)

        # Switch between insert/overwrite mode
        if event.key() == Qt.Key_Insert and event.modifiers() == Qt.NoModifier:
            self.overwriteMode = not self.overwriteMode
            self.overwriteModeChanged.emit(self.overwriteMode)
            self.setCursorPosition(self.cursorPosition)
        
        # Switch from hex to ascii edit
        if event.key() == Qt.Key_Tab and not self.editAreaIsAscii:
            self.editAreaIsAscii = True
            self.setCursorPosition(self.cursorPosition)

        # Switch from ascii to hex edit
        if event.key() == Qt.Key_Backtab and self.editAreaIsAscii:
            self.editAreaIsAscii = False
            self.setCursorPosition(self.cursorPosition)

        # Edit commands will be parced only if NOT ReadOnly

        if not self.readOnly:
            # self.refresh()
            # QAbstractScrollArea.keyPressEvent(self, event)
            # return
        
            # Cut
            if event.matches(QKeySequence.Cut):
                ba = self.chunks.data(self.getSelectionBegin(), self.getSelectionEnd() - self.getSelectionBegin())
                buf = str()
                for i in range(0, len(ba), 32):
                    buf += ba[i:i+32].hex() + '\n'
                clipboard = QApplication.clipboard()
                print('cut\n', buf)
                clipboard.setText(buf)
                if self.overwriteMode:
                    self.replaceAtArray(self.getSelectionBegin(), \
                        self.getSelectionEnd() - self.getSelectionBegin(), \
                        bytes(self.getSelectionEnd() - self.getSelectionBegin())) # zero filled bytes
                else:
                    self.removeChar(self.getSelectionBegin(), self.getSelectionEnd() - self.getSelectionBegin())
                self.setCursorPosition(2 * self.getSelectionBegin())
                self.resetSelection(2 * self.getSelectionBegin())
            
            # Paste
            if event.matches(QKeySequence.Paste):
                print('Paste Key Event')
                clipboard = QApplication.clipboard()
                ba = bytes.fromhex(clipboard.text()) # ?
                print(ba)
                if self.overwriteMode:
                    ba = ba[0:min(len(ba), self.chunks.size - self.bPosCurrent)]
                    self.replaceAtArray(self.bPosCurrent, len(ba), ba)
                else:
                    self.insert(self.bPosCurrent, ba)
                self.setCursorPosition(self.cursorPosition + 2 * len(ba))
                self.resetSelection(self.getSelectionBegin())

                # Delete char
            elif event.matches(QKeySequence.Delete):
                if self.getSelectionBegin() != self.getSelectionEnd():
                    self.bPosCurrent = self.getSelectionBegin()
                    if self.overwriteMode:
                        ba = bytes(self.getSelectionEnd() - self.getSelectionBegin()) # zero filled bytes
                        self.replaceAtArray(self.bPosCurrent, len(ba), ba)
                    else:
                        self.removeChar(self.bPosCurrent, self.getSelectionEnd() - self.getSelectionBegin())
                else:
                    if self.overwriteMode:
                        self.replaceChar(self.bPosCurrent, bytes(1)) # zero filled byte
                    else:
                        self.removeChar(self.bPosCurrent, 1)
            # Backspace
            elif event.key() == Qt.Key_Backspace and event.modifiers() == Qt.NoModifier:
                if self.getSelectionBegin() != self.getSelectionEnd():
                    self.bPosCurrent = self.getSelectionBegin()
                    self.setCursorPosition(2 * self.bPosCurrent)
                    if self.overwriteMode:
                        ba = bytes(self.getSelectionEnd() - self.getSelectionBegin()) # zero filled byte
                        self.replaceAtArray(self.bPosCurrent, len(ba), ba)
                    else:
                        self.remove(self.bPosCurrent, self.getSelectionEnd() - self.getSelectionBegin())
                    self.resetSelection(2 * self.bPosCurrent)
                else:
                    behindLastByte = False
                    if self.cursorPosition // 2 == self.chunks.size:
                        behindLastByte = True
                    
                    self.bPosCurrent -= 1
                    if self.overwriteMode:
                        self.replaceChar(self.bPosCurrent, bytes(1)) # zero filled byte
                    else:
                        self.removeChar(self.bPosCurrent, 1)
                    
                    if behindLastByte: self.bPosCurrent -= 1

                    self.setCursorPosition(2 * self.bPosCurrent)
                    self.resetSelection(2 * self.bPosCurrent)

            # undo
            elif event.matches(QKeySequence.Undo):
                self.undo()

            # redo
            elif event.matches(QKeySequence.Redo):
                self.redo()

            elif (QApplication.keyboardModifiers() == Qt.NoModifier) or \
                    (QApplication.keyboardModifiers() == Qt.KeypadModifier) or \
                    (QApplication.keyboardModifiers() == Qt.ShiftModifier) or \
                    (QApplication.keyboardModifiers() == (Qt.AltModifier | Qt.ControlModifier)) or \
                    (QApplication.keyboardModifiers() == Qt.GroupSwitchModifier):
                # hex and ascii input
                if self.editAreaIsAscii:
                    #key = event.text()[0].toLatin1() #?
                    #key = event.text()[0]
                    key = event.text()
                else:
                    #key = event.text()[0].toLower().toLatin1() #?
                    #key = event.text()[0].lower()
                    key = event.text().lower()
                print(f'{key = }')
                print(f'{self.overwriteMode = }')
                if (('0' <= key <= '9' or 'a' <= key <= 'f') and not self.editAreaIsAscii) or \
                        (key >= ' ' and self.editAreaIsAscii):
                    if self.getSelectionBegin() != self.getSelectionEnd():
                        if self.overwriteMode:
                            length = self.getSelectionEnd() - self.getSelectionBegin()
                            self.replaceAtArray(self.getSelectionBegin(), length, bytes(length)) # zero filled bytes
                        else:
                            self.removeChar(self.getSelectionBegin(), self.getSelectionEnd - self.getSelectionBegin())
                            self.bPosCurrent = self.getSelectionBegin()
                        self.setCursorPosition(2 * self.bPosCurrent)
                        self.resetSelection(2 * self.bPosCurrent)

                    # If insert mode, then insert a byte
                    if not self.overwriteMode:
                        if self.cursorPosition % 2 == 0:
                            self.insert(self.bPosCurrent, bytes(1)) # zero filled byte
                    
                    # Change content
                    if self.chunks.size > 0:
                        print(f'{self.chunks.size = }')
                        print('self.chunks.chunks ', self.chunks.chunks)
                        ch = bytes(key, encoding='ascii')
                        if not self.editAreaIsAscii:
                            print('keyevent self.chunks.chunks = ', self.chunks.chunks)
                            hexVal = self.chunks.data(self.bPosCurrent, 1).hex() # hexVal: str, length = 2
                            if self.cursorPosition % 2 == 0:
                                print(f'{hexVal = }')
                                print(f'{key = }')
                                # 'QByteArray' object does not support item assignment
                                # hexVal[0] = ord(key)
                                hexVal = key + hexVal[1] # replace [7:4] bits of byte - even position 
                                print(f'{hexVal = }')
                            else:
                                hexVal = hexVal[0] + key # replace [3:0] bits of byte - odd position
                                print(f'{hexVal = }')
                            ch = bytes.fromhex(hexVal)
                        print(f'char {ch}')
                        self.replaceChar(self.bPosCurrent, ch)
                        if self.editAreaIsAscii:
                            self.setCursorPosition(self.cursorPosition + 2)
                        else:
                            self.setCursorPosition(self.cursorPosition + 1)
                        self.resetSelection(self.cursorPosition)
            #end edit section if not readonly

        self.refresh()
        QAbstractScrollArea.keyPressEvent(self, event)
        #end of keyPressEvent
        #pass

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        self.blink = False
        self.viewport().update()
        actPos = self.getCursorPosition(event.pos())
        if actPos >= 0:
            self.setCursorPosition(actPos)
            self.setSelection(actPos)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        self.blink = False
        self.viewport().update()
        cPos = self.getCursorPosition(event.pos())
        #ePos = event.pos().x(), event.pos().y()
        #print(f'{ePos = } , {cPos = }')
        if cPos >= 0:
            if event.button() != Qt.RightButton:
                self.resetSelection(cPos)
            self.setCursorPosition(cPos)

    def paintEvent(self, event: QPaintEvent) -> None:
        #print('paintEvent start')
        painter = QPainter(self.viewport())
        pxOffsetX = self.horizontalScrollBar().value()
        if event.rect() != self.cursorRect:
            pxPosStartY = self.pxCharHeight
            # Draw some patterns if needed
            painter.fillRect(event.rect(), self.viewport().palette().color(QPalette.Base))
            if self.addressArea:
                painter.fillRect(
                    QRect(-pxOffsetX, event.rect().top(), self.pxPosHexX - self.pxGapAdrHex // 2, self.height()),self.addressAreaColor)
                painter.setPen(Qt.gray)
                addrLinePos = self.pxPosHexX - self.pxGapAdrHex // 2
                painter.drawLine(addrLinePos, event.rect().top(), addrLinePos, event.rect().bottom())

            if self.asciiArea:
                linePos = self.pxPosAsciiX - (self.pxGapHexAscii // 2)
                painter.setPen(Qt.gray)
                painter.drawLine(linePos - pxOffsetX, event.rect().top(), linePos - pxOffsetX, self.height())
            painter.setPen(self.viewport().palette().color(QPalette.WindowText))
            if self.addressArea:
                pxPosY = pxPosStartY
                for row in range(len(self.dataShown) // self.bytesPerLine):
                    addrTemplate = self.getAddrTemplate(self.chunks.size)
                    address = addrTemplate.format(self.bPosFirst + row * self.bytesPerLine + self.addressOffset)
                    painter.drawText(self.pxPosAdrX - pxOffsetX, pxPosY, address)
                    pxPosY += self.pxCharHeight
            colStandard = QPen(self.viewport().palette().color(QPalette.WindowText))
            painter.setBackgroundMode(Qt.TransparentMode)
            pxPosY = pxPosStartY
            for row in range(self.rowsShown):
                pxPosX = self.pxPosHexX - pxOffsetX
                pxPosAsciiX = self.pxPosAsciiX - pxOffsetX
                bPosLine = row * self.bytesPerLine
                colIdx = 0
                while (bPosLine + colIdx) < len(self.dataShown) and colIdx < self.bytesPerLine:
                    c = self.viewport().palette().color(QPalette.Base)
                    painter.setPen(colStandard)
                    posBa = self.bPosFirst + bPosLine + colIdx
                    if self.getSelectionBegin() <= posBa < self.getSelectionEnd():
                        c = self.brushSelection.color()
                        painter.setPen(self.penSelection)
                    elif self.highlighting:
                        if self.markedShown[posBa - self.bPosFirst]:
                            c = self.brushHighlighted.color()
                            painter.setPen(self.penHighlighted)
                    r = QRect()
                    if colIdx == 0:
                        r.setRect(pxPosX, pxPosY - self.pxCharHeight + self.pxSelectionSub, 2 * self.pxCharWidth,
                                  self.pxCharHeight)
                    else:
                        r.setRect(pxPosX - self.pxCharWidth, pxPosY - self.pxCharHeight + self.pxSelectionSub,
                                  3 * self.pxCharWidth, self.pxCharHeight)
                    painter.fillRect(r, c) # uncomment!
                    hex = self.hexDataShow[(bPosLine + colIdx) * 2:(bPosLine + colIdx) * 2 + 2]
                    painter.drawText(pxPosX, pxPosY, hex.upper() if self.hexCaps else hex)
                    pxPosX += 3 * self.pxCharWidth
                    if self.asciiArea:
                        ch = self.bytesToStr(self.dataShown[bPosLine+colIdx:bPosLine+colIdx+1])
                        r.setRect(pxPosAsciiX, pxPosY - self.pxCharHeight + self.pxSelectionSub, self.pxCharWidth,
                                  self.pxCharHeight)
                        painter.fillRect(r, c) # uncomment!
                        painter.drawText(pxPosAsciiX, pxPosY, ch)
                        pxPosAsciiX += self.pxCharWidth
                    colIdx += 1
                pxPosY += self.pxCharHeight
            painter.setBackgroundMode(Qt.TransparentMode)
            painter.setPen(self.viewport().palette().color(QPalette.WindowText))

        # _cursorPosition counts in 2, _bPosFirst counts in 1
        hexPositionInShowData = self.cursorPosition - 2 * self.bPosFirst
        #print(f'{hexPositionInShowData = }')

        if 0 <= hexPositionInShowData < len(self.hexDataShow):
            if self.readOnly:
                color = self.viewport().palette().dark().color()
                painter.fillRect(
                    QRect(self.pxCursorX - pxOffsetX, self.pxCursorY - self.pxCharHeight + self.pxSelectionSub,
                          self.pxCharWidth, self.pxCharHeight), color)
            elif self.blink and self.hasFocus():
                painter.fillRect(self.cursorRect, self.palette().color(QPalette.WindowText))

            if self.editAreaIsAscii:
                asciiPositionInShowData = hexPositionInShowData // 2
                ch = self.bytesToStr(self.dataShown[asciiPositionInShowData:asciiPositionInShowData+1])
                painter.drawText(self.pxCursorX - pxOffsetX, self.pxCursorY, ch)
            else:
                string = self.hexDataShow[hexPositionInShowData:hexPositionInShowData+1].upper() \
                    if self.hexCaps else self.hexDataShow[hexPositionInShowData:hexPositionInShowData+1]
                #print('paintEvent hex', f'{ string = }')
                painter.drawText(self.pxCursorX - pxOffsetX, self.pxCursorY, string)
        # emit event, if size has changed
        if self.lastEventSize != self.chunks.size:
            self.lastEventSize = self.chunks.size
            # noinspection PyUnresolvedReferences
            self.currentSizeChanged.emit(self.lastEventSize)

    def resizeEvent(self, event: QResizeEvent) -> None:
        if self.dynamicBytesPerLine:
            pxFixGaps = 0
            if self.addressArea:
                pxFixGaps = self.addressWidth * self.pxCharWidth + self.pxGapAdr
            pxFixGaps += self.pxGapAdrHex
            if self.asciiArea:
                pxFixGaps += self.pxGapHexAscii
            # +1 because the last hex value do not have space. so it is effective one char more
            charWidth = (self.viewport().width() - pxFixGaps) // self.pxCharWidth + 1
            # 2 hex alfa-digits 1 space 1 ascii per byte = 4; if ascii is disabled then 3
            # to prevent division by zero use the min value 1
            self.setBytesPerLine(max(charWidth // (4 if self.asciiArea else 3), 1))
        self.adjust()

    def focusNextPrevChild(self, nextChild: bool) -> bool:
        if self.addressArea:
            if (nextChild and self.editAreaIsAscii) or (not nextChild and not self.editAreaIsAscii):
                super(QHexEdit, self).focusNextPrevChild(nextChild)
            else:
                return False
        else:
            super(QHexEdit, self).focusNextPrevChild(nextChild)

    def initSelection(self):
        self.bSelectionBegin = self.bSelectionInit
        self.bSelectionEnd = self.bSelectionInit

    def resetSelection(self, pos: int) -> None:
        pos = pos // 2
        if pos < 0: pos = 0
        if pos > self.chunks.size: pos = self.chunks.size
        self.bSelectionInit = pos
        self.bSelectionBegin = pos
        self.bSelectionEnd = pos

    def setSelection(self, pos: int) -> None:
        pos = pos // 2
        if pos < 0: pos = 0
        if pos > self.chunks.size: pos = self.chunks.size
        if pos >= self.bSelectionInit:
            self.bSelectionBegin, self.bSelectionEnd = self.bSelectionInit, pos
        else:
            self.bSelectionBegin, self.bSelectionEnd = pos, self.bSelectionInit

    def getSelectionBegin(self) -> int:
        return self.bSelectionBegin

    def getSelectionEnd(self) -> int:
        return self.bSelectionEnd

    def adjust(self) -> None:
        if self.addressArea:
            # The addressDigit is the total of digits that is used for represent the directions of memory
            # Old called to method: getAddressDigit()
            self.addressDigit = 8
            self.pxPosHexX = self.pxGapAdr + self.addressDigit * self.pxCharWidth + self.pxGapAdrHex
        else:
            self.pxPosHexX = self.pxGapAdrHex
        self.pxPosAdrX = self.pxGapAdr
        self.pxPosAsciiX = self.pxPosHexX + self.hexCharInLine * self.pxCharWidth + self.pxGapHexAscii

        # Set horizontalScrollBar()
        pxWidth = self.pxPosAsciiX
        if self.asciiArea:
            pxWidth += self.bytesPerLine * self.pxCharWidth
        self.horizontalScrollBar().setRange(0, pxWidth - self.viewport().width())
        self.horizontalScrollBar().setPageStep(self.viewport().width())

        # Set verticalScrollbar()
        self.rowsShown = (self.viewport().height() - 4) // self.pxCharHeight
        lineCount = (self.chunks.size // self.bytesPerLine) + 1
        self.verticalScrollBar().setRange(0, lineCount - self.rowsShown)
        self.verticalScrollBar().setPageStep(self.rowsShown)

        value = self.verticalScrollBar().value()
        self.bPosFirst = value * self.bytesPerLine
        self.bPosLast = self.bPosFirst + (self.rowsShown * self.bytesPerLine) - 1
        if self.bPosLast >= self.chunks.getSize():
            self.bPosLast = self.chunks.getSize() - 1
        self.readBuffers()
        self.setCursorPosition(self.cursorPosition)

    # noinspection PyUnresolvedReferences
    def dataChangedPrivate(self) -> None:
        self.modified = self.undoStack.index() != 0
        self.adjust()
        self.dataChanged.emit()

    def refresh(self) -> None:
        self.ensureVisible()
        self.readBuffers()

    def readBuffers(self) -> None:
        self.dataShown = self.chunks.data(self.bPosFirst, self.bPosLast - self.bPosFirst + self.bytesPerLine + 1,
                                          self.markedShown)
        self.hexDataShow = self.dataShown.hex()

    def toReadable(self, array: bytearray) -> str:
        result = str()
        addrTemplate = self.getAddrTemplate(len(array))
        for i in range(0, len(array), 16):
            addString = addrTemplate.format(self.addressOffset + i)
            ascString = str()
            hexline = array[i:i+16].hex()
            hexString = ' '.join([hexline[i:i+2] for i in range(0, len(hexline), 2)] + ['  ']*(16 - len(hexline) // 2))
            ascString = self.bytesToStr(array[i:i+16])
            result += addString + '  ' + hexString + '  ' + ascString + '\n'
        return result

    def updateCursor(self):
        if self.blink:
            self.blink = False
        else:
            self.blink = True
        self.viewport().update(self.cursorRect)

    def byteToStr(self, b: bytes) -> str:
        ch = b.decode(encoding='ascii', errors='ignore')
        return '.' if ch < ' ' or ch > '~' else ch

    def bytesToStr(self, b: bytes) -> str:
        res = ''
        for i in range(len(b)):
            ch = b[i:i+1].decode(encoding='ascii', errors='ignore')
            res += '.' if ch < ' ' or ch > '~' else ch
        return res

    def getAddrTemplate(self, size: int, base: int = 10) -> str:
        if base == 10:
            return "{0:0>4}" if size < 10000 else "{0:0>8}"
        elif base == 8:
            return "{0:0>4o}" if size < 0o10000 else "{0:0>8o}"
        else:
            return "{0:0>4x}" if size < 0x10000 else "{0:0>8x}"
