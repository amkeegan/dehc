from multiprocessing import Process, Queue
import queue
import time

from PIL import Image
import random

class Printer:

    inQueue = None
    outQueue = None
    port = None
    barcodesToPrint = []
    count = 0

    def __init__(self, inQueue : Queue = None, outQueue : Queue = None):
        self.inQueue = inQueue
        self.outQueue = outQueue
        self.detectDevice()
        self.openDevice(self.port)
        if inQueue is not None and outQueue is not None:
            print('Running')
            self.run()

    def detectDevice(self):
        self.port = ''
        
    def openDevice(self, port):
        print(f'Device opened on {port}')
        self.connection = True # Placeholder..
        pass

    def closeDevice(self):
        print(f'Count: {self.count}')
        print('Closing Printer hardware connection')

    def printIDCard(self, idCard: Image):
        idCard.show()
        idCard.save('tmp.png')
        print(f'Got image: {idCard.size}, count: {self.count}, length: {len(self.barcodesToPrint)}')

    def processBarcodeQueue(self):
        if len(self.barcodesToPrint) > 0:
            self.printIDCard(self.barcodesToPrint[0])
            try:
                self.barcodesToPrint.remove(self.barcodesToPrint[0])
            except ValueError:
                pass 

    def processMsg(self, msg):
        if "message" in msg:
            if msg["message"] == "close":
                self.closeDevice()
            if msg["message"] == "idcard":
                self.barcodesToPrint.append(msg["idcard"])

    def run(self):
        self.count = 0
        while(True):
            inMsg = None
            try:
                if self.inQueue is not None:
                    while(True):
                        inMsg = self.inQueue.get(block=False)
                        if inMsg is not None:
                            self.processMsg(inMsg)
                            self.count += 1
            except queue.Empty:
                time.sleep(0.01)
            self.processBarcodeQueue() ## Print one card at time before checking message queue (for terminate messages etc)

if __name__ == "__main__":

    printer = Printer()

    data_updated = True

    for _ in range(0,2):
        printer.barcodesToPrint.append(Image.new('RGB', (400,640), (random.randint(0,255),random.randint(0,255),random.randint(0,255))))
        printer.processBarcodeQueue()
        time.sleep(2) 

