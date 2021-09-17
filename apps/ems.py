'''The module containing the evacuation management system, used for ingest, etc.'''

import tkinter as tk
from tkinter import ttk

import mods.log as ml
import mods.database as md
import mods.widgets as mw

# ----------------------------------------------------------------------------

class EMS():
    '''A class which represents the EMS application.
    
    cats: The categories which can be searched and created on the EMS screen.
    db: The database object which the app uses for database transactions.
    logger: The logger object used for logging.
    root: The root of the application, a tk.Tk object.
    '''

    def __init__(self, db: md.DEHCDatabase, *, level: str = "NOTSET", autorun: bool = False):
        '''Constructs an EMS object.
        
        db: The database object which the app uses for database transactions.
        level: Minimum level of logging messages to report; "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL", "NONE".
        prepare: If true, automatically prepares widgets for packing.
        '''
        self.level = level
        self.logger = ml.get("EMS", level=self.level)
        self.logger.debug("EMS object instantiated")

        self.db = db
        self.cats = self.db.schema_cats()

        self.root = tk.Tk()
        self.root.title("EMS Prototype")
        self.root.resizable(width=False, height=False)
        self.root.bind("<Escape>", lambda *_: self.root.destroy())

        if autorun == True:
            self.prepare()
            self.pack()
            self.run()


    def prepare(self):
        '''Constructs the frames and widgets of the EMS.'''
        self.f_left = ttk.Frame(master=self.root)
        self.f_right = ttk.Frame(master=self.root)
        self.f_base = ttk.Frame(master=self.root)
        topbase, = self.db.items_query(cat="station", selector={"Display Name":{"$eq":"Ingest"}}, fields=["_id", "Display Name"])
        botbase, = self.db.items_query(cat="station", selector={"Display Name":{"$eq":"Clean Hold"}}, fields=["_id", "Display Name"])
        self.cm = mw.ContainerManager(master=self.f_left, db=self.db, topbase=topbase, botbase=botbase, cats=self.cats, level=self.level, prepare=True, select=self.item_select, width=100)
        self.de = mw.DataEntry(master=self.f_right, db=self.db, cats=self.cats, level=self.level, prepare=True, height=266, width=100)
        self.sb = mw.StatusBar(master=self.f_base, db=self.db, level=self.level, prepare=True, width=200)


    def pack(self):
        '''Packs & grids children frames and widgets of the EMS.'''
        self.f_left.grid(column=0, row=0, sticky="nsew")
        self.f_right.grid(column=1, row=0, sticky="nsew")
        self.f_base.grid(column=0, row=1, columnspan=2)
        self.de.pack(fill=tk.BOTH, expand=True)
        self.cm.pack(fill=tk.BOTH, expand=True)
        self.sb.pack(fill=tk.BOTH, expand=True)


    def run(self):
        '''Enters the root's main loop, drawing the app screen.'''
        self.root.mainloop()


    def __del__(self):
        '''Runs when EMS object is deleted.'''
        self.logger.debug("EMS object destroyed")
    

    def item_select(self, *args):
        '''Callback for when an item is selected on the top tree.'''
        doc, = args
        self.de.show(doc)


# ----------------------------------------------------------------------------