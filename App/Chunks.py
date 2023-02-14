import sys

from PyQt5.QtCore import QObject, QIODevice, QBuffer

NORMAL = b'\x00'
HIGHLIGHTED = b'\x01'
CHUNK_SIZE = 0x1000
BUFFER_SIZE = 0x10000


class Chunk:
    def __init__(self):
        self.data = bytearray
        self.dataChanged = bytearray
        self.absPos: int = 0


class Chunks(QObject):
    def __init__(self, parent: QObject = None, device: QIODevice = None):
        super().__init__(parent)
        self.device = QBuffer(self) if device is None else device
        self.chunks: list[Chunk] = []
        self.position = 0
        self.size = 0

        self.setIODevice(self.device)

    def setIODevice(self, device: QIODevice) -> bool:
        self.device = device
        status = self.device.open(QIODevice.ReadOnly)
        if status:
            self.size = self.device.size()
            self.device.close()
        else:
            # Fallback is an empty buffer
            self.size = 0
            self.device = QBuffer(self)
        self.chunks.clear()
        self.position = 0
        return status

    def data(self, position: int, maxSize: int = -1, highlighted: bytearray = None) -> bytearray:
        delta = 0
        chunkIdx = 0
        chunk = Chunk()
        buffer = bytearray()
        if highlighted is not None:
            highlighted.clear()
        if position >= self.size:
            return buffer
        if maxSize < 0:
            maxSize = self.size
        elif (position + maxSize) > self.size:
            maxSize = self.size - position

        self.device.open(QIODevice.ReadOnly)
        while maxSize > 0:
            chunk.absPos = sys.maxsize
            chunksLoopOngoing = True
            while chunkIdx < len(self.chunks) and chunksLoopOngoing:
                # In this section, we track changes before our required data and
                # we take the editdet data, if availible. ioDelta is a difference
                # counter to justify the read pointer to the original data, if
                # data in between was deleted or inserted.
                chunk = self.chunks[chunkIdx]
                if chunk.absPos > position:
                    chunksLoopOngoing = False
                else:
                    count = 0
                    chunkIdx += 1
                    chunkOfs = position - chunk.absPos
                    if maxSize > len(chunk.data) - chunkOfs:
                        count = len(chunk.data) - chunkOfs
                        delta += CHUNK_SIZE - len(chunk.data)
                    else:
                        count = maxSize

                    if count > 0:
                        buffer += chunk.data[chunkOfs:chunkOfs+count]
                        maxSize -= count
                        position += count
                        if highlighted is not None:
                            highlighted += chunk.dataChanged[chunkOfs:chunkOfs+count]
            if maxSize > 0 and position < chunk.absPos:
                byteCount = 0
                if (chunk.absPos - position) > maxSize:
                    byteCount = maxSize
                else:
                    byteCount = chunk.absPos - position
                maxSize -= byteCount
                self.device.seek(position + delta)
                readBuffer = self.device.read(byteCount)
                buffer += readBuffer
                if highlighted is not None:
                    highlighted += bytearray(NORMAL*len(readBuffer)) # b'\x00' filled bytearray
                position += len(readBuffer)
        self.device.close()
        return buffer

    def write(self, device: QIODevice, position: int = 0, count: int = -1) -> bool:
        if count == -1:
            count = self.size
        status = device.open(QIODevice.WriteOnly)
        if status:
            for idx in range(position, count, BUFFER_SIZE):
                array = self.data(idx, BUFFER_SIZE)
                device.write(array)
            device.close()
        return status

    def setDataChanged(self, position: int, dataChanged: bool) -> None:
        if 0 <= self.position < self.size:
            chunkIdx = self.getChunkIndex(position)
            posInBa = position - self.chunks[chunkIdx].absPos
            self.chunks[chunkIdx].dataChanged[posInBa] = dataChanged

    def dataChanged(self, position: int) -> bool:
        highlighted = bytearray()
        self.data(position, 1, highlighted)
        return bool(highlighted[0])

    def indexOf(self, array: bytearray, _from: int) -> int:
        res = -1
        for pos in range(_from, self.size, BUFFER_SIZE):
            buffer = self.data(pos, BUFFER_SIZE + len(array) - 1)
            findPos = buffer.find(array)
            if findPos >= 0:
                res = pos + findPos
                break
        return res

    def lastIndexOf(self, array: bytearray, _from: int) -> int:
        res = -1
        for pos in range(_from, 0, -BUFFER_SIZE):
            sPos = pos - BUFFER_SIZE - len(array) + 1
            if sPos < 0: sPos = 0
            buffer = self.data(sPos, pos - sPos)
            findPos = buffer.rfind(array)
            if findPos >= 0:
                res = sPos + findPos
                break
        return res

    def insert(self, position: int, character: bytes) -> bool:
        if 0 <= position <= self.size:
            if position == self.size and self.size == 0:
                chunkIdx = self.getChunkIndex(position) # to insert before the last byte ??? position-1
            elif position == self.size:
                chunkIdx = self.getChunkIndex(position-1)
            else:
                chunkIdx = self.getChunkIndex(position)
            posInBa = position - self.chunks[chunkIdx].absPos
            self.chunks[chunkIdx].data[posInBa:posInBa] = character[0:1]
            self.chunks[chunkIdx].dataChanged[posInBa:posInBa] = bytes(HIGHLIGHTED) # to highlight the change
            for i in range(chunkIdx+1, len(self.chunks)):
                self.chunks[i].absPos += 1
            self.size += 1
            self.position = position
            return True
        else:
            return False

    def overwrite(self, position: int, character: bytes) -> bool:
        if 0 <= position < self.size:
            chunkIdx = self.getChunkIndex(position)
            posInBa = position - self.chunks[chunkIdx].absPos
            self.chunks[chunkIdx].data[posInBa:posInBa + 1] = character[0:1]
            self.chunks[chunkIdx].dataChanged[posInBa:posInBa + 1] = bytes(HIGHLIGHTED) # to highlight the change
            self.position = position
            return True
        else:
            return False

    def removeAt(self, position: int) -> bool:
        if 0 <= position < self.size:
            chunkIdx = self.getChunkIndex(position)
            posInBa = position - self.chunks[chunkIdx].absPos
            del self.chunks[chunkIdx].data[posInBa]
            del self.chunks[chunkIdx].dataChanged[posInBa]
            for i in range(chunkIdx + 1, len(self.chunks)):
                self.chunks[i].absPos -= 1
            self.size -= 1
            self.position = position
            return True
        else:
            return False        

    def at(self, pos) -> bytes:
        return bytes(self.data(pos, 1))

    def getPos(self) -> int:
        return self.position

    def getSize(self) -> int:
        return self.size

    def __getitem__(self, item):
        pass

    def getChunkIndex(self, absPos: int):
        foundIdx = -1
        insertIdx = 0
        ioDelta = 0

        for i in range(len(self.chunks)):
            chunk = self.chunks[i]
            # when "undo" and then "redo" the only byte the loop makes a new chunk every "undo-redo"
            if len(chunk.data) == 0 and len(self.chunks) == 1 and absPos == 0: return 0
            if chunk.absPos <= absPos < chunk.absPos + len(chunk.data):
                foundIdx = i
                break
            if absPos < chunk.absPos:
                insertIdx = i
                break
            ioDelta += len(chunk.data) - CHUNK_SIZE
            insertIdx = i + 1
        
        if foundIdx == -1:
            newChunk = Chunk() 
            readAbsPos = absPos - ioDelta
            readPos = (readAbsPos >> 12) << 12 # & READ_CHUNK_MASK Q_INT64_C(0xfffffffffffff000)
            self.device.open(QIODevice.ReadOnly)
            self.device.seek(readPos)
            newChunk.data = bytearray(self.device.read(CHUNK_SIZE))
            self.device.close()
            newChunk.absPos = absPos - (readAbsPos - readPos)
            newChunk.dataChanged = bytearray(len(newChunk.data)) #zero filled bytearray
            self.chunks.insert(insertIdx, newChunk)
            foundIdx = insertIdx
        
        return foundIdx