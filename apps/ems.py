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
    flags: The flags which can be assigned on the EMS screen.
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
        self.flags = ["FlagA", "FlagB", "FlagC", "FlagD"]

        self.root = tk.Tk()
        self.root.title("EMS Prototype")
        self.root.state('zoomed')
        self.root.bind("<Escape>", lambda *_: self.root.destroy())

        if autorun == True:
            self.prepare()
            self.pack()
            self.run()


    def prepare(self):
        '''Constructs the frames and widgets of the EMS.'''
        topbase, = self.db.items_query(cat="station", selector={"Display Name":{"$eq":"Ingest"}}, fields=["_id", "Display Name"])
        botbase, = self.db.items_query(cat="station", selector={"Display Name":{"$eq":"Clean Hold"}}, fields=["_id", "Display Name"])
        self.cm = mw.ContainerManager(master=self.root, db=self.db, topbase=topbase, botbase=botbase, cats=self.cats, level=self.level, prepare=True, select=self.item_select)
        self.de = mw.DataEntry(master=self.root, db=self.db, cats=self.cats, delete=self.delete, flags=self.flags, level=self.level, prepare=True, save=self.save)
        self.sb = mw.StatusBar(master=self.root, db=self.db, level=self.level, prepare=True)

        self.root.rowconfigure(0, weight=1000)
        self.root.rowconfigure(1, weight=1, minsize=16)
        self.root.columnconfigure(0, weight=1000)
        self.root.columnconfigure(1, weight=1000)


    def pack(self):
        '''Packs & grids children frames and widgets of the EMS.'''
        self.de.grid(column=1, row=0, sticky="nsew", padx=2, pady=2)
        self.cm.grid(column=0, row=0, sticky="nsew", padx=2, pady=2)
        self.sb.grid(column=0, row=1, columnspan=2, sticky="nsew", padx=2)


    def run(self):
        '''Enters the root's main loop, drawing the app screen.'''
        self.root.mainloop()


    def item_select(self, *args):
        '''Callback for when an item is selected on the top tree.'''
        doc, = args
        self.de.show(doc)


    def delete(self, *args):
        '''Callback for when the delete button is pressed in the data pane.'''
        id, parents, *_ = args
        if len(parents) > 0:
            parent, *_ = parents
            if id == self.cm.base()["_id"]:
                self.cm.base(newbase=self.db.item_get(id=parent, fields=["_id", "Display Name"]))
            self.cm.refresh()
            self.cm.highlight(item=parent)
            self.cm.open()
        else:
            self.cm.refresh()


    def save(self, *args):
        '''Callback for when the save button is pressed in the data pane.'''
        id, *_ = args
        if id != None:
            container, *_ = self.cm.selections()
            self.db.container_add(container=container, item=id)
        self.cm.refresh()
        if id != None:
            self.cm.highlight(item=id)


    def __del__(self):
        '''Runs when EMS object is deleted.'''
        self.logger.debug("EMS object destroyed")
    


# ----------------------------------------------------------------------------