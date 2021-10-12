'''The module containing pbjects that create and manage photos.'''

import cv2
from PIL import Image

import mods.log as ml

# ----------------------------------------------------------------------------

class PhotoManager:
    '''A class which handles taking photos from a webcam.'''

    def __init__(self, level: str = "NOTSET"):
        '''Constructs a PhotoManager object.
        
        level: Minimum level of logging messages to report; "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL", "NONE".
        '''
        self.logger = ml.get(name="PhotoManager", level=level)
        self.logger.debug(f"PhotoManager object instantiated")

        self.camera = cv2.VideoCapture(0)


    def destroy(self):
        '''Deletes the VideoCapture object, freeing it as a resource.'''
        del(self.camera)


    def take_photo(self):
        '''Takes a photo and returns it as a PIL object.'''
        result, img = self.camera.read()
        if result == True:
            self.logger.debug(f"Photo captured")
            img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
            img.thumbnail(size=(300, 300))
        else:
            self.logger.warning(f"Photo capture failed")
        return img

