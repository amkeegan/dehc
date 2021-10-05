from multiprocessing import Process, Queue
import queue
import time

class Hardware_Worker:
    
    inQueue = None
    outQueue = None
    currentData = None
    connection = None

    def __init__(self, inQueue : Queue = None, outQueue : Queue = None):
        self.inQueue = inQueue
        self.outQueue = outQueue
        self.detectDevice()
        self.openDevice()
        if inQueue is not None and outQueue is not None:
            self.run()

    def detectDevice(self):
        pass

    def openDevice(self):
        pass

    def closeDevice(self):
        pass

    def readNewData(self, type = None):
        pass

    def sendNewData(self):
        if self.currentData is not None:
            msg = {"message": "data", "data": self.currentData}
            if self.outQueue is not None:
                self.outQueue.put(msg)
            else:
                print(msg)

    def processQueueMessage(self, message):
        if "message" in message:
            if message["message"] == "close":
                self.closeDevice()
                self.connection = False

    def run(self):
        while(self.connection):
            inMessage = None
            try:
                if self.inQueue is not None:
                    inMessage = self.inQueue.get(block=False)
            except queue.Empty:
                time.sleep(0.1)
            if inMessage is not None:
                self.processQueueMessage(inMessage)
            self.readNewData()
            self.sendNewData()
