from multiprocessing import Process, Queue
import queue
import time

import random

from mods.dehc_worker import Hardware_Worker

import win32ui, win32con, win32print
from PIL import Image, ImageWin

#Courtesy: https://stackoverflow.com/questions/54522120/python3-print-landscape-image-file-with-specified-printer

def listPrinters():
    printers = win32print.EnumPrinters(6)
    return printers

def getDefaultPrinter():
    return win32print.GetDefaultPrinter()

class Printer_Worker(Hardware_Worker):

    barcodesToPrint = []
    count = 0
    connection = False
    selectedPrinter = None

    def __init__(self, inQueue: Queue = None, outQueue: Queue = None):
        super().__init__(inQueue=inQueue, outQueue=outQueue)

    def detectDevice(self):
        default = win32print.GetDefaultPrinter()
        if default is not None:
            self.selectedPrinter = default
                
    def openDevice(self):
        if self.selectedPrinter is not None:
            self.connection = True # Placeholder..

    def closeDevice(self):
        print('Closing Printer hardware connection')

    def printIDCard(self, idCard: Image):

        hdc = win32ui.CreateDC()
        hdc.CreatePrinterDC(self.selectedPrinter)

        horzres = hdc.GetDeviceCaps(win32con.HORZRES)
        vertres = hdc.GetDeviceCaps(win32con.VERTRES)

        landscape = horzres > vertres

        if landscape:
            if idCard.size[1] > idCard.size[0]:
                print('Landscape mode, tall image, rotate bitmap.')
                idCard = idCard.rotate(90, expand=True)
        else:
            if idCard.size[1] < idCard.size[0]:
                print('Portrait mode, wide image, rotate bitmap.')
                idCard = idCard.rotate(90, expand=True)

        img_width = idCard.size[0]
        img_height = idCard.size[1]

        if landscape:
            #we want image width to match page width
            ratio = vertres / horzres
            max_width = img_width
            max_height = (int)(img_width * ratio)
        else:
            #we want image height to match page height
            ratio = horzres / vertres
            max_height = img_height
            max_width = (int)(max_height * ratio)

        #map image size to page size
        hdc.SetMapMode(win32con.MM_ISOTROPIC)
        hdc.SetViewportExt((horzres, vertres))
        hdc.SetWindowExt((max_width, max_height))

        #offset image so it is centered horizontally
        offset_x = (int)((max_width - img_width)/2)
        offset_y = (int)((max_height - img_height)/2)
        hdc.SetWindowOrg((-offset_x, -offset_y)) 
        try:
            hdc.StartDoc('Result')
            hdc.StartPage()

            dib = ImageWin.Dib(idCard)
            dib.draw(hdc.GetHandleOutput(), (0, 0, img_width, img_height))

            hdc.EndPage()
            hdc.EndDoc()
            hdc.DeleteDC()
        except win32ui.error:
            pass

        print('Printing complete.')

    def processBarcodeQueue(self):
        if len(self.barcodesToPrint) > 0:
            self.printIDCard(self.barcodesToPrint[0])
            print(f'Calling print function')
            try:
                self.barcodesToPrint.remove(self.barcodesToPrint[0])
            except ValueError:
                pass 
    
    def processQueueMessage(self, message):
        if "idcard" in message:
            self.barcodesToPrint.append(message["idcard"])
            print(f'Added new id card to print list')
        if "printer" in message:
            self.selectedPrinter = message["printer"]
        return super().processQueueMessage(message)

    def readNewData(self, type=None):
        return super().readNewData(type=type)

    def sendNewData(self):
        self.processBarcodeQueue()
        return super().sendNewData()

if __name__ == "__main__":

    printer = Printer_Worker()

    data_updated = True

    for _ in range(0,2):
        printer.barcodesToPrint.append(Image.new('RGB', (400,640), (random.randint(0,255),random.randint(0,255),random.randint(0,255))))
        printer.processBarcodeQueue()
        time.sleep(2) 
    