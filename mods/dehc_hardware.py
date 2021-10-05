from multiprocessing import Process, Queue
from multiprocessing.spawn import freeze_support
import queue
import time

try:
    import mods.acr122u.dehc_nfc as NFC
except ImportError:
    pass

try: 
    import wedderburn_di_166.dehc_scales as Scales
except ImportError:
    pass

try:
    import mods.zebra_ds22_reader.dehc_barcode as Barcode
except ImportError:
    pass

try:
    import zebra_zc300_printer.dehc_printer as Printer
except ImportError:
    pass

from PIL import Image

import random

#WORKER_MESSAGE_NODATA = 'No Data'
#WORKER_MESSAGE_BROKEN_HARDWARE_CONNECTION = 'No Connection'

class Hardware:

    processes = []
    SCALES_EXIST = False
    NFCREADER_EXIST = False
    BARCODEREADER_EXIST = False
    PRINTER_EXIST = False

    lastNFCUID = ''

    inQueueBarcode = None
    outQueueBarcode = None

    inQueueNFC = None
    outQueueNFC = None

    inQueueScales = None
    outQueueScales = None

    inQueuePrinter = None
    outQueuePrinter = None

    def __init__(self, makeScales = False, makeBarcodeReader = False, makeNFCReader = False, makePrinter = False):
        
        if makeScales:
            self.inQueueScales = Queue(maxsize=1) # Only store the most recent value
            self.outQueueScales = Queue(maxsize=1) # For now, we don't need to stack up C2 messages
            self.processScales = Process(target=Scales, args=(self.outQueueScales, self.inQueueScales))
            self.processes.append(self.processScales)
        if makeNFCReader:
            self.inQueueNFC = Queue(maxsize=1) # Only store the most recent value
            self.outQueueNFC = Queue(maxsize=1) # For now, we don't need to stack up C2 messages
            self.processNFC = Process(target=NFC.NFC_Worker, args=(self.outQueueNFC, self.inQueueNFC))
            self.processes.append(self.processNFC)
        if makeBarcodeReader:
            self.inQueueBarcode = Queue(maxsize=1) # Only store the most recent value
            self.outQueueBarcode = Queue(maxsize=1) # For now, we don't need to stack up C2 messages
            self.processBarcode = Process(target=Barcode.Barcode_Worker, args=(self.outQueueBarcode, self.inQueueBarcode))
            self.processes.append(self.processBarcode)
        if makePrinter:
            self.inQueuePrinter = Queue(maxsize=1) # Only store the most recent value
            self.outQueuePrinter = Queue(maxsize=1000) # For now, we don't need to stack up C2 messages
            self.processPrinter = Process(target=Printer, args=(self.outQueuePrinter, self.inQueuePrinter))
            self.processes.append(self.processPrinter)
            
        self.startProcesses()

        self.SCALES_EXIST = makeScales
        self.NFCREADER_EXIST = makeNFCReader
        self.BARCODEREADER_EXIST = makeBarcodeReader
        self.PRINTER_EXIST = makePrinter
        
        time.sleep(1)

    def startProcesses(self):
        for process in self.processes:
            if process is None:
                continue
            process.start()

    def terminateProcesses(self):
        if self.outQueueScales is not None:
            self.outQueueScales.put({"message": "close"})
        if self.outQueueNFC is not None:
            self.outQueueNFC.put({"message": "close"})
        if self.outQueueBarcode:
            self.outQueueBarcode.put({"message": "close"})
        if self.outQueuePrinter:
            self.outQueuePrinter.put({"message": "close"})
        
        time.sleep(2) # Allow some time for process to do cleanup
        
        for process in self.processes:
            if process is None:
                continue
            if process._popen is not None:
                process.join(1)
                process.terminate()

    def getCurrentWeight(self):
        if not self.SCALES_EXIST:
            return {}
        currentWeight = {}
        try:
            currentWeight = self.inQueueScales.get(block=False)
        except queue.Empty:
            currentWeight = {"message": "error", "error": "No Data"}
        return currentWeight

    def getCurrentNFCUID(self):
        if not self.NFCREADER_EXIST:
            self.lastNFCUID = ''
        else:
            try:
                tmpData = self.inQueueNFC.get(timeout=0.01)
                if 'uid' in tmpData:
                    self.lastNFCUID = tmpData['uid']
                    #TODO: Should handle not sending duplicates??
            except queue.Empty:
                print('Queue empty')
                self.lastNFCUID = ''
        return self.lastNFCUID
    
    def getCurrentBarcode(self):
        if not self.BARCODEREADER_EXIST:
            self.lastBarcode = ''
        else:
            try:
                tmpData = self.inQueueBarcode.get(timeout=0.01)
                if 'barcode' in tmpData:
                    self.lastBarcode = tmpData['barcode']
            except queue.Empty:
                self.lastBarcode = ''
        return self.lastBarcode

    def sendNewIDCard(self, idCardImage: Image):
        self.outQueuePrinter.put({"message": "idcard", "idcard": idCardImage})

if __name__ == "__main__":

    hardware = Hardware(makeScales=False,makeBarcodeReader=False, makeNFCReader=True, makePrinter=False)

    time.sleep(2)

    # weight = hardware.getCurrentWeight()
    
    # barcode = hardware.getCurrentBarcode()
    
    nfcUID = hardware.getCurrentNFCUID()

    # for _ in range(0,1):
    #     tmpIDCard = Image.new('RGB', (400,640), (random.randint(0,255),random.randint(0,255),random.randint(0,255)))
    #     hardware.sendNewIDCard(tmpIDCard)
    
    # print(f'Weight: {weight}')
    # print(f'Barcode: {barcode}')
    print(f'NFC UID: {nfcUID}')
    
    time.sleep(1)
    
    hardware.terminateProcesses()
