from multiprocessing import Process, Queue
import queue
import time

import serial
import serial.tools.list_ports

from mods.dehc_worker import Hardware_Worker

class Scales_Worker(Hardware_Worker):

    serialDevice = None
    port = None
    units = None

    def __init__(self, inQueue: Queue = None, outQueue: Queue = None):
        super().__init__(inQueue=inQueue, outQueue=outQueue)
    
    def detectDevice(self):
        ports = serial.tools.list_ports.comports()
        for port, desc, hwid in sorted(ports):    
            if hwid == 0x1234: #TODO Confirm HWID of FDTI / UART converter
                self.port = port
                print('Selected COM Port for scales:')
                print(f'\t{port}: {desc} [{hwid}]')
        return super().detectDevice()
    
    def openDevice(self):
        try:
            self.serialDevice = serial.Serial(self.port, 19200, timeout=1)
        except Exception as err: #TODO: Actual error checking
            print(f'Error opening {self.port}: {err}')
        print(f'Successfully opened Serial device on {self.port}')
    
    def closeDevice(self):
        if self.serialDevice is not None:
            self.serialDevice.close()
            self.serialDevice = None
            print(f'Closed Serial device on {self.port}')

    def parseWeightBytes(self, line: str):
        #TODO: Error checking, not a number
        result = float(line.decode().strip('\r\n').strip(self.units))
        return result
    
    def readCurrentWeight(self):
        self.currentWeight = None
        if self.serialDevice is not None:
            line = self.serialDevice.readline()
            if len(line) > 0:
                result = self.parseWeightBytes(line)
                self.currentWeight = result

    def sendCurrentWeight(self):    
        if self.currentWeight is not None:
            msg = {"message": "data", "weight": self.currentWeight, "units": self.units}
            if self.outQueue is not None:
                try:
                    self.outQueue.put(msg, block=False)
                except queue.Full:
                    time.sleep(0.1)
            else:
                print(msg)

    def readNewData(self, type=None):
        self.readCurrentWeight()
    
    def sendNewData(self):
        self.sendCurrentWeight()

if __name__ == "__main__":

    scales = Scales_Worker()

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
