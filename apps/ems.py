'''The module containing the evacuation management system, used for ingest, etc.'''

import tkinter as tk
from tkinter import ttk

import mods.log as ml
import mods.widgets as mw

# ----------------------------------------------------------------------------

class EMS():
    '''A class which represents the EMS application.'''

    def __init__(self, level: str = "NOTSET"):
        '''Constructs an EMS object.
        
        level: Minimum level of logging messages to report; "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL", "NONE".
        '''
        self.logger = ml.get("EMS", level=level)
        self.logger.debug("EMS object instantiated")
        
        root = tk.Tk()
        de = mw.DataEntry(master=root, cats=["Test 1", "Test 2"], level=level, width=60, prepare=True)
        de.pack(fill=tk.BOTH, expand=True)
        root.mainloop()


    def __del__(self):
        '''Runs when EMS object is deleted.'''
        self.logger.debug("EMS object destroyed")

# ----------------------------------------------------------------------------