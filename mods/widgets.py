'''The module containing objects that create and manage groups of tkinter widgets.'''

import tkinter as tk
from tkinter import ttk

import mods.log as ml


# ----------------------------------------------------------------------------

class SuperWidget:
    '''A class which represents a self-contained collection of tkinter widgets.
    
    Not to be instantiated directly; use the various sub-classes instead.
    When subclassing, overwrite _pack_children() with code to pack the various child widgets beneath self.w_fr.

    master: The widget that the SuperWidget's component widgets will be instantiated under.
    logger: The logger object used for logging.
    w_fr: The frame widget that contains the SuperWidget's component widgets.
    '''

    def __init__(self, master: tk.Misc, *, level: str = "NOTSET"):
        '''Constructs a SuperWidget object.
        
        master: The widget that the SuperWidget's component widgets will be instantiated under.
        level: Minimum level of logging messages to report; "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL", "NONE".
        '''
        logger_name = str(type(self).__name__)
        self.logger = ml.get(logger_name, level=level)
        self.logger.debug(f"{logger_name} object instantiated")

        self.master = master
        self.w_fr = ttk.Frame(master=self.master)


    def pack(self, *args, **kwargs):
        '''Packs the frames and widgets of the SuperWidget.
        
        Arguments are the same as tkinter's .pack() methods.
        '''
        self.w_fr.pack(*args, **kwargs)
        self._pack_children()

    
    def grid(self, *args, **kwargs):
        '''Grids the frames and widgets of the SuperWidget.
        
        Arguments are the same as tkinter's .grid() methods.
        '''
        self.w_fr.grid(*args, **kwargs)
        self._pack_children()
    

    def _pack_children(self):
        '''Packs & grids children frames and widgets of the SuperWidget.
        
        Should be overwritten for each new SuperWidget.
        '''
        raise NotImplementedError


class DataEntry(SuperWidget):
    '''A SuperWidget representing a data entry pane.
    
    cats: The categories for which new items can be created using this DataEntry.
    logger: The logger object used for logging.
    master: The widget that the DataEntry's component widgets will be instantiated under.
    '''

    def __init__(self, master: tk.Misc, *, cats: list = [], level: str = "NOTSET", prepare: bool = True, width: int = 45):
        '''Constructs a DataEntry object.
        
        master: The widget that the DataEntry's component widgets will be instantiated under.
        cats: The categories of items that can be created using the New button.
        level: Minimum level of logging messages to report; "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL", "NONE".
        prepare: If true, automatically prepares widgets for packing.
        width: The width of the widget in characters.
        '''
        super().__init__(master=master, level=level)

        self.cats = cats
        self.width = width

        if prepare == True:
            self.prepare()
    

    def prepare(self):
        '''Constructs the frames and widgets of the DataEntry.'''
        # Frames
        self.w_fr_head = ttk.Frame(master=self.w_fr)
        self.w_fr_body = ttk.Frame(master=self.w_fr, height=128)
        self.w_fr_foot = ttk.Frame(master=self.w_fr)

        # Widgets
        self.w_var_cat = tk.StringVar()
        self.w_la_head = ttk.Label(master=self.w_fr_head, text="Title Here", width=self.width)
        self.w_bu_edit = ttk.Button(master=self.w_fr_foot, text="Edit", command=self.edit, width=self.width//6)
        self.w_bu_cancel = ttk.Button(master=self.w_fr_foot, text="Cancel", command=self.cancel, width=self.width//6)
        self.w_co_cat = ttk.Combobox(master=self.w_fr_foot, values=self.cats, textvariable=self.w_var_cat, state="readonly", width=self.width//6)
        self.w_bu_new = ttk.Button(master=self.w_fr_foot, text="New", command=self.new, width=self.width//6)
        self.w_bu_save = ttk.Button(master=self.w_fr_foot, text="Save", command=self.save, width=self.width//6)
        self.w_bu_delete = ttk.Button(master=self.w_fr_foot, text="Delete", command=self.delete, width=self.width//6)
        self.w_co_cat.current(0)


    def _pack_children(self):
        '''Packs & grids children frames and widgets of the DataEntry.'''
        # Frames
        self.w_fr_head.grid(column=0, row=0, sticky="nsew")
        self.w_fr_body.grid(column=0, row=1, sticky="nsew")
        self.w_fr_foot.grid(column=0, row=2, sticky="nsew")

        # Widgets
        self.w_la_head.pack(fill=tk.BOTH, expand=True)
        self.w_bu_edit.grid(column=0, row=0, sticky="nsew")
        self.w_bu_cancel.grid(column=1, row=0, sticky="nsew")
        self.w_co_cat.grid(column=2, row=0, sticky="nsew")
        self.w_bu_new.grid(column=3, row=0, sticky="nsew")
        self.w_bu_save.grid(column=4, row=0, sticky="nsew")
        self.w_bu_delete.grid(column=5, row=0, sticky="nsew")


    def add(self, *args):
        '''Callback for when the flag add button is pressed'''
        self.logger.info("Pressed ADD FLAG")

    def cancel(self, *args):
        '''Callback for when the cancel button is pressed.'''
        self.logger.info("Pressed CANCEL")

    def delete(self, *args):
        '''Callback for when the delete button is pressed'''
        self.logger.info("Pressed DELETE")

    def edit(self, *args):
        '''Callback for when the edit button is pressed'''
        self.logger.info("Pressed EDIT")

    def new(self, *args):
        '''Callback for when the new button is pressed.'''
        self.logger.info("Pressed NEW")

    def photo(self, *args):
        '''Callback for when the photo is pressed'''
        self.logger.info("Pressed PHOTO")

    def remove(self, *args):
        '''Callback for when the flag remove button is pressed'''
        self.logger.info("Pressed REMOVE FLAG")

    def save(self, *args):
        '''Callback for when the save button is pressed.'''
        self.logger.info("Pressed SAVE")
    

    def __del__(self):
        '''Runs when DataEntry object is deleted.'''
        self.logger.debug("DataEntry object destroyed")


# ----------------------------------------------------------------------------