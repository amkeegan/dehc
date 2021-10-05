from multiprocessing import Process, Queue
import queue
import time

import serial

class Scales:

    inQueue = None
    outQueue = None
    currentWeight = 0.0
    port = 'COM3'
    unit = "KG" # Default measurement units

    def __init__(self, inQueue : Queue = None, outQueue : Queue = None):
        self.inQueue = inQueue
        self.outQueue = outQueue
        self.detectDevice()
        self.openDevice(self.port)
        if inQueue is not None and outQueue is not None:
            self.run()

    def detectDevice(self):
        #TODO: Add port selection logic (based on USB <-> Serial PID,VID?)
        #self.port = 'COM3'
        pass
        
    def openDevice(self, port):
        try:
            self.serial = serial.Serial(self.port, 19200, timeout=1)
        except: #TODO: Add actual error checking
            self.serial = None
            return
        print(f'Device opened on {port}')

    def closeDevice(self):
        print('Closing Scales hardware connection')
        if self.serial is not None:
            self.serial.close()
            self.serial = None
        
    def readCurrentWeight(self):
        self.currentWeight = None
        if self.serial is not None:
            line = self.serial.readline()
            if len(line) > 0:
                line = float(line.decode().strip('\r\n').strip(self.unit))
                self.currentWeight = line
    
    def sendCurrentWeight(self):
        if self.currentWeight is not None:
            msg = {"message": "data", "weight": self.currentWeight, "unit": self.unit}
            if self.outQueue is not None:
                self.outQueue.put(msg)
            else:
                print(msg)
        #else:
        #    self.outQueue.put({"message": "error", "error": "No connections"})

    def processMsg(self, msg):
        if "message" in msg:
            if msg["message"] == "close":
                self.closeDevice()

    def run(self):
        while(True):
            inMsg = None
            try:
                if self.inQueue is not None:
                    inMsg = self.inQueue.get(block=False)
            except queue.Empty:
                time.sleep(0.1)
            if inMsg is not None:
                self.processMsg(inMsg)
            self.readCurrentWeight()
            self.sendCurrentWeight()

if __name__ == "__main__":

    scales = Scales()

    data_updated = True
    
    while(True):
        scales.readCurrentWeight()
        if scales.currentWeight is not None:
            print(f'Weight: {scales.currentWeight}')
            data_updated = True
        else:
            if data_updated:
                print(f'No data')
            data_updated = False
            time.sleep(0.2)
