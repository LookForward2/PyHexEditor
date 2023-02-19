from PyQt5.QtWidgets import QUndoStack, QUndoCommand
from PyQt5.QtCore import QObject
from App.Chunks import Chunks
from enum import Enum

class CCmd(Enum):
    insert = 0 
    removeAt = 1
    overwrite = 2

# Helper class to store single byte commands
class CharCommand(QUndoCommand):
    
    def __init__(self, chunks: Chunks, cmd: CCmd, charPos: int, newChar: bytes, parent: QUndoCommand = None):
        super().__init__()
        self.chunks = chunks
        self.cmd = cmd
        self.charPos = charPos
        self.newChar = newChar
        self.oldChar = bytes()

    def mergeWith(self, command): # command: CharCommand()
        nextCommand = command
        result = False
        if self.cmd != CCmd.removeAt:
            if nextCommand.cmd == CCmd.overwrite:
                if nextCommand.charPos == self.charPos:
                    self.newChar = nextCommand.newChar
                    result = True
        return result

    def redo(self):
        if self.cmd == CCmd.insert:
            self.chunks.insert(self.charPos, self.newChar)
        if self.cmd == CCmd.overwrite:
            self.oldChar = self.chunks.at(self.charPos)
            self.wasChanged = self.chunks.dataChanged(self.charPos)
            self.chunks.overwrite(self.charPos, self.newChar)
        if self.cmd == CCmd.removeAt:
            self.oldChar = self.chunks.at(self.charPos)
            self.wasChanged = self.chunks.dataChanged(self.charPos)
            self.chunks.removeAt(self.charPos)

    def undo(self):
        if self.cmd == CCmd.insert:
            self.chunks.removeAt(self.charPos)
        if self.cmd == CCmd.overwrite:
            self.chunks.overwrite(self.charPos, self.oldChar)
            self.chunks.setDataChanged(self.charPos, self.wasChanged)
        if self.cmd == CCmd.removeAt:
            self.chunks.insert(self.charPos, self.oldChar)
            self.chunks.setDataChanged(self.charPos, self.wasChanged)

    def id(self): return 1477 # It must be an integer unique to this command's class


class UndoStack(QUndoStack):
    def __init__(self, chunks: Chunks, parent: QObject):
        super().__init__()
        self.chunks = chunks
        self.parent = parent
        self.setUndoLimit(1000)

    def removeAt(self, pos: int, length: int):
        if 0 <= pos < self.chunks.size:
            if length == 1:
                cc = CharCommand(self.chunks, CCmd.removeAt, pos, bytes(1)) # zero filled byte
                self.push(cc)
            else:
                txt = f"Delete {length} chars"
                self.beginMacro(txt)
                for i in range(length):
                    cc = CharCommand(self.chunks, CCmd.removeAt, pos, bytes(1)) # zero filled byte
                    self.push(cc)
                self.endMacro()

    def insert(self, pos: int, ba: bytes):
        if 0 <= pos <= self.chunks.size:
            if len(ba) == 1:
                cc = CharCommand(self.chunks, CCmd.insert, pos, ba)
                self.push(cc)
            elif len(ba) > 1:
                txt = f"Insert {len(ba)} chars"
                self.beginMacro(txt)
                for i in range(len(ba)):
                    cc = CharCommand(self.chunks, CCmd.insert, pos + i, ba[i:i+1])
                    self.push(cc)
                self.endMacro()                

    def overwrite(self, pos: int, ba: bytes): # no length argument - len(ba) instead
        if 0 <= pos < self.chunks.size:
            if len(ba) == 1:
                cc = CharCommand(self.chunks, CCmd.overwrite, pos, ba)
                self.push(cc)
            elif len(ba) > 1:
                txt = f"Overwrite {len(ba)} chars"
                self.beginMacro(txt)
                self.removeAt(pos, len(ba))
                self.insert(pos, ba)
                self.endMacro()
