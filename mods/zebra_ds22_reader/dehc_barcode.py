from multiprocessing import Process, Queue
import queue
import time
import sys
import os

import usb.core ## python -m pip install pyusb

from mods.dehc_worker import Hardware_Worker

class Barcode_Worker(Hardware_Worker):

    usbDevice = None

    def __init__(self, inQueue: Queue = None, outQueue: Queue = None):
        ## TODO: Add some detection logic
        ## TODO: Decide if we should hardcode, and/or allow passed in PID,VID
        self.idVendor = 0x05E0
        self.idProduct = 0x1300
        super().__init__(inQueue=inQueue, outQueue=outQueue)
    
    def detectDevice(self):
        return super().detectDevice()
    
    def openDevice(self):
        #TODO: Do exception handling
        self.usbDevice = usb.core.find(idVendor=self.idVendor, idProduct=self.idProduct)
        if self.usbDevice is None:
            print(f"USB Device could not be opened. Vendor {self.idVendor}, Product: {self.idProduct}")
            return
        self.usbDevice.set_configuration() # TODO: Work out what this does..
        self.usbEndpoint = self.usbDevice[0][(0,0)][0] # TODO: Documentation
        self.connection = True
        print(f'USB Device opened with Vendor: {self.idVendor}, Product: {self.idProduct}')

    def closeDevice(self):
        self.usbDevice = None
        self.connection = None
        print('Closing Barcode hardware connection')

    def processQueueMessage(self, message):
        return super().processQueueMessage(message)

    def parseBarcodeResponse(self, response):
        
        headerLength = 4

        i = len(response) - 1

        while(i > 0):
            if response[i] == 0:
                i -= 1
                continue
            else:
                break

        ## Assume that leading 4 bytes are some header
        ## Assume that trailing zeros are padding
        ##  -2, to include the last valid byte (before trailing zeros)
        value = bytes(response)[headerLength:i-2].decode()

        return value

    def readCurrentBarcode(self):
        self.currentBarcode = None
        if self.usbDevice is not None:
            try:
                data = None
                data = self.usbDevice.read(self.usbEndpoint.bEndpointAddress, self.usbEndpoint.wMaxPacketSize)
                recontructedData = self.parseBarcodeResponse(data)
                self.currentBarcode = recontructedData
            except usb.core.USBError as err:
                if err.args == ('Operation timed out',):
                    pass
                else:
                    self.currentBarcode = None
    
    def sendCurrentBarcode(self):
        if self.currentBarcode is not None:
            msg = {"message": "data", "barcode": self.currentBarcode}
            if self.outQueue is not None:
                try:
                    self.outQueue.put(msg, block=False)
                except queue.Full:
                    time.sleep(0.1)
            else:
                print(msg)

    def readNewData(self, type=None):
        self.readCurrentBarcode()

    def sendNewData(self):
        self.sendCurrentBarcode()

if __name__ == "__main__":

    barcode = Barcode_Worker()

    data_updated = True
    
    while(True):
        barcode.readCurrentBarcode()
        if barcode.currentBarcode is not None:
            print(f'Barcode: {barcode.currentBarcode}')
            data_updated = True
        else:
            if data_updated:
                print(f'No data')
            data_updated = False
            time.sleep(0.2)