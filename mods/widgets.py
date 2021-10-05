'''The module containing objects that create and manage groups of tkinter widgets.'''

import json
import time

from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk
from typing import Callable

import mods.database as md
import mods.log as ml
import mods.photo as mp
import mods.dehc_hardware as hw

# ----------------------------------------------------------------------------

class SuperWidget:
    '''A class which represents a self-contained collection of tkinter widgets.
    
    Not to be instantiated directly; use the various sub-classes instead.
    When subclassing, overwrite _pack_children() with code to pack the various child widgets beneath self.w_fr.

    db: The database object which the widget uses for database transactions.
    master: The widget that the SuperWidget's component widgets will be instantiated under.
    logger: The logger object used for logging.
    w_fr: The frame widget that contains the SuperWidget's component widgets.
    '''

    def __init__(self, master: tk.Misc, db: md.DEHCDatabase, *, level: str = "NOTSET"):
        '''Constructs a SuperWidget object.
        
        master: The widget that the SuperWidget's component widgets will be instantiated under.
        db: The database object which the widget uses for database transactions.
        level: Minimum level of logging messages to report; "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL", "NONE".
        '''
        # Logging
        suffix = 1
        while True:
            logger_name = f"{type(self).__name__}{suffix if suffix > 1 else ''}"
            if not ml.check(name=logger_name) or suffix > 99:
                break
            suffix += 1
        self.logger = ml.get(logger_name, level=level)
        self.logger.debug(f"{logger_name} object instantiated")
        self.db = db

        # Placement
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


# ----------------------------------------------------------------------------

class DataEntry(SuperWidget):
    '''A SuperWidget representing a data entry pane.
    
    cats: The categories for which new items can be created using this DataEntry.
    current_photo: The PIL data of the photo currently shown in the data pane.
    db: The database object which the widget uses for database transactions.
    last_doc: The last doc that was shown in the data pane.
    last_photo: The PIL data of the photo last loaded into the data pane.
    level: Minimum level of logging messages to report; "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL", "NONE".
    logger: The logger object used for logging.
    master: The widget that the DataEntry's component widgets will be instantiated under.
    _delete: If present, a callback function that triggers when an item is deleted.
    _save: If present, a callback function that triggers when an item is saved.
    '''

    def __init__(self, master: tk.Misc, db: md.DEHCDatabase, *, cats: list = [], delete: Callable = None, level: str = "NOTSET", prepare: bool = True, save: Callable = None, show: Callable = None, hardware: hw.Hardware = None):
        '''Constructs a DataEntry object.
        
        master: The widget that the DataEntry's component widgets will be instantiated under.
        cats: The categories of items that can be created using the New button.
        level: Minimum level of logging messages to report; "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL", "NONE".
        save: If present, a callback function that triggers when an item is saved.
        show: If present, a callback function that triggers when 'show' or 'back' is pressed in the data pane.
        prepare: If true, automatically prepares widgets for packing.
        '''
        super().__init__(master=master, db=db, level=level)

        self.cats = cats
        self.back_doc = {}
        self.last_doc = {}
        self.current_photo = None
        self.last_photo = None
        self.level = level
        self._delete = delete
        self._save = save
        self._show = show

        self.hardware = hardware

        if prepare == True:
            self.prepare()


    def prepare(self):
        '''Constructs the frames and widgets of the DataEntry.'''
        self.w_fr_head = ttk.Frame(master=self.w_fr)
        self.w_fr_photo = ttk.Frame(master=self.w_fr)
        self.w_fr_flags = ttk.Frame(master=self.w_fr)
        self.w_fr_body = ttk.Frame(master=self.w_fr)
        self.w_fr_data = ttk.Frame(master=self.w_fr_body)
        self.w_fr_foot = ttk.Frame(master=self.w_fr)

        self.w_fr.columnconfigure(index=0, weight=1000)
        self.w_fr.columnconfigure(index=1, weight=1000)
        self.w_fr.columnconfigure(index=2, weight=1, minsize=16)
        self.w_fr.rowconfigure(index=0, weight=1, minsize=25)
        self.w_fr.rowconfigure(index=1, weight=500)
        self.w_fr.rowconfigure(index=2, weight=1000)
        self.w_fr.rowconfigure(index=3, weight=1, minsize=25)

        self.w_fr_head.columnconfigure(index=0, weight=1000)
        self.w_fr_head.columnconfigure(index=1, weight=1, minsize=48)
        self.w_fr_head.columnconfigure(index=2, weight=1, minsize=48)
        self.w_fr_head.columnconfigure(index=3, weight=1, minsize=48)
        self.w_fr_head.rowconfigure(index=0, weight=1000)

        self.w_fr_photo.columnconfigure(index=0, weight=1000)
        self.w_fr_photo.rowconfigure(index=0, weight=1000)

        self.w_fr_flags.columnconfigure(index=0, weight=1000)
        self.w_fr_flags.columnconfigure(index=1, weight=1000)
        self.w_fr_flags.columnconfigure(index=2, weight=1000)
        self.w_fr_flags.columnconfigure(index=3, weight=1, minsize=16)
        self.w_fr_flags.rowconfigure(index=0, weight=1, minsize=25)
        self.w_fr_flags.rowconfigure(index=1, weight=1000)
        self.w_fr_flags.rowconfigure(index=2, weight=1, minsize=25)

        self.w_fr_body.columnconfigure(index=0, weight=1000)
        self.w_fr_body.rowconfigure(index=0, weight=1000)

        self.w_fr_foot.columnconfigure(index=0, weight=1000)
        self.w_fr_foot.columnconfigure(index=1, weight=1000)
        self.w_fr_foot.columnconfigure(index=2, weight=1000)
        self.w_fr_foot.columnconfigure(index=3, weight=1000)
        self.w_fr_foot.columnconfigure(index=4, weight=1000)
        self.w_fr_foot.columnconfigure(index=5, weight=1000)
        self.w_fr_foot.rowconfigure(index=0, weight=1000)

        # Variables
        self.w_var_data = []
        self.w_var_cat = tk.StringVar()
        self.w_var_flags = tk.StringVar()

        # Widgets
        self.w_la_title = ttk.Label(master=self.w_fr_head, text="Title", font="Arial 12 bold")
        self.w_bu_generate_id = ttk.Button(master=self.w_fr_head, text="Print ID", command=self.generate_id_card)
        self.w_bu_copyid = ttk.Button(master=self.w_fr_head, text="Copy ID", command=self.copyid)
        self.w_bu_back = ttk.Button(master=self.w_fr_head, text="Back", command=self.back)
        self.w_bu_photo = ttk.Button(master=self.w_fr_photo, text="Photo", command=self.photo)
        self.w_la_flags = ttk.Label(master=self.w_fr_flags, text="Flags")
        self.w_li_flags = tk.Listbox(master=self.w_fr_flags, selectmode=tk.SINGLE, relief=tk.GROOVE, exportselection=False)
        self.w_co_flags = ttk.Combobox(master=self.w_fr_flags, textvariable=self.w_var_flags, state="readonly")
        self.w_bu_add = ttk.Button(master=self.w_fr_flags, text="Add", command=self.add)
        self.w_bu_remove = ttk.Button(master=self.w_fr_flags, text="Remove", command=self.remove)
        self.w_la_data = []
        self.w_input_data = []
        self.w_bu_edit = ttk.Button(master=self.w_fr_foot, text="Edit", command=self.edit)
        self.w_bu_cancel = ttk.Button(master=self.w_fr_foot, text="Cancel", command=self.cancel)
        self.w_co_cat = ttk.Combobox(master=self.w_fr_foot, values=self.cats, textvariable=self.w_var_cat, state="readonly")
        self.w_bu_new = ttk.Button(master=self.w_fr_foot, text="New", command=self.new)
        self.w_bu_save = ttk.Button(master=self.w_fr_foot, text="Save", command=self.save)
        self.w_bu_delete = ttk.Button(master=self.w_fr_foot, text="Delete", command=self.delete)
        self.w_co_cat.current(0)
        self.show()

        # Scrollbars
        self.w_sc_flags = ttk.Scrollbar(master=self.w_fr_flags, orient="vertical", command=self.w_li_flags.yview)
        self.w_li_flags.config(yscrollcommand=self.w_sc_flags.set)


    def _pack_children(self):
        '''Packs & grids children frames and widgets of the DataEntry.'''
        self.w_fr_head.grid(column=0, row=0, columnspan=3, sticky="nsew", padx=2, pady=2)
        self.w_fr_photo.grid(column=0, row=1, sticky="nsew", padx=2, pady=2)
        self.w_fr_flags.grid(column=1, row=1, sticky="nsew", padx=2, pady=2)
        self.w_fr_body.grid(column=0, row=2, columnspan=2, sticky="nsew", padx=2, pady=2)
        self.w_fr_data.grid(column=0, row=0, sticky="nsew")
        self.w_fr_foot.grid(column=0, row=3, columnspan=3, sticky="nsew", padx=2, pady=1)

        self.w_la_title.grid(column=0, row=0, columnspan=2, sticky="nsew", padx=2, pady=2)
        self.w_bu_generate_id.grid(column=1,row=0,sticky="nsew",padx=2,pady=2)
        self.w_bu_copyid.grid(column=2, row=0, sticky="nsew", padx=2, pady=2)
        self.w_bu_back.grid(column=3, row=0, sticky="nsew", padx=2, pady=2)

        self.w_bu_photo.grid(column=0, row=0, sticky="nsew", padx=2, pady=2)

        self.w_la_flags.grid(column=0, row=0, columnspan=4, sticky="nsew", padx=1, pady=1)
        self.w_li_flags.grid(column=0, row=1, columnspan=3, sticky="nsew", padx=1, pady=1)
        self.w_sc_flags.grid(column=3, row=1, sticky="nse", padx=1, pady=1)
        self.w_co_flags.grid(column=0, row=2, sticky="nsew", padx=1, pady=1)
        self.w_bu_add.grid(column=1, row=2, sticky="nsew", padx=1, pady=1)
        self.w_bu_remove.grid(column=2, row=2, sticky="nsew", padx=1, pady=1)

        self.w_bu_edit.grid(column=0, row=0, sticky="nsew", padx=1, pady=1)
        self.w_bu_cancel.grid(column=1, row=0, sticky="nsew", padx=1, pady=1)
        self.w_co_cat.grid(column=2, row=0, sticky="nsew", padx=1, pady=1)
        self.w_bu_new.grid(column=3, row=0, sticky="nsew", padx=1, pady=1)
        self.w_bu_save.grid(column=4, row=0, sticky="nsew", padx=1, pady=1)
        self.w_bu_delete.grid(column=5, row=0, sticky="nsew", padx=1, pady=1)


    def read_scales(self):
        if self.scales is not None:
            if self.scales.in_waiting > 0:
                line = self.scales.readline()
                self.last_weight = float(line.decode().strip('\r\n').strip('KG'))
        else:
            #TODO: Remove random weight generation
            import random
            self.last_weight = round(90+random.random()*5, 2)


    def close_scales(self):
        if self.scales is not None:
            self.scales.close()
            self.scales = None


    def add(self, *args):
        '''Callback for when the flag add button is pressed.'''
        flag = self.w_var_flags.get()
        if flag not in self.w_li_flags.get(0, "end"):
            self.w_li_flags.insert("end", flag)


    def back(self, *args):
        '''Callback for when the back button is pressed.'''
        if "_id" in self.back_doc:
            self.last_doc, self.back_doc = self.back_doc, self.last_doc
            self._show(self.last_doc["_id"])


    def cancel(self, *args):
        '''Callback for when the cancel button is pressed.'''
        self.show()


    def show_id_window(self):
        button = self.w_bu_generate_id
        state = str(button.cget("state"))
        if state != "disabled":
            for child in button.winfo_children():
                child.destroy()
            window = tk.Toplevel(master=button)
            window.attributes("-topmost", True)
            window.focus_force()
            window.title("ID Generation")

            msg = ttk.Label(master=window)
            print_button = ttk.Button(master=window, text="Print")

            def show_image(image: Image):
                
                panel = tk.Label(window, image=image)
                panel.grid(column=0,row=0)

            def print_id_card():
                #TODO Link to self.hw.Hardware and print
                print('Printing ID Card..')

            #TODO: Add / get generated ID Card bitmap etc
            self.id_card_image = ImageTk.PhotoImage(Image.new('RGB', (400,640), (128,0,238)))

            show_image(self.id_card_image)

            print_button.config(command=print_id_card)
            msg.grid(column=0, row=0, sticky="nsew", padx=10, pady=10)
            print_button.grid(column=0, row=1, sticky="nsew", padx=10, pady=10)


    def generate_id_card(self, *args):
        #TODO Get active evacuee details and MAKE id card, store to self.current_id_card?
        self.show_id_window()


    def copyid(self, *args):
        '''Call back for when the copy id button is pressed.'''
        root = self.w_fr.winfo_toplevel()
        root.clipboard_clear()
        root.clipboard_append(self.last_doc.get("_id", ""))


    def delete(self, *args):
        '''Callback for when the delete button is pressed'''
        id = self.last_doc["_id"]
        parents = self.db.item_parents(item=id)
        if len(parents) > 0:
            self.db.item_delete(id=id, all=True, recur=True)
            self.last_doc = {}
            self.show()
            if self._delete != None:
                self._delete(id, parents)
        else:
            self.logger.error("Could not delete top level item")


    def edit(self, *args):
        '''Callback for when the edit button is pressed'''
        for entry, buttona, buttonb, hidden in zip(self.w_input_data, self.w_buttona_data, self.w_buttonb_data, self.w_hidden_data):
            if hidden == None:
                entry.config(state="normal")
            if buttona != None:
                buttona.config(state="normal")
            if buttonb != None:
                buttonb.config(state="normal")
        self.w_bu_photo.config(command=self.photo)
        self.w_bu_edit.config(state="disabled")
        self.w_bu_cancel.config(state="normal")
        self.w_bu_save.config(state="normal")
        self.w_bu_delete.config(state="normal")
        self.w_bu_add.config(state="normal")
        self.w_bu_remove.config(state="normal")
        self.w_co_flags.config(state="normal")
        if "category" in self.last_doc:
            flags = self.db.schema_flags(cat=self.last_doc["category"])
            if len(flags) > 0:
                self.w_co_flags['values'] = flags
                self.w_co_flags.current(0)


    def new(self, *args):
        '''Callback for when the new button is pressed.'''
        self.back_doc = self.last_doc
        self.last_doc = {"category": self.w_var_cat.get()}
        self.show()
        self.edit()
        self.w_bu_delete.config(state="disabled")


    def photo(self, *args):
        '''Callback for when the photo is pressed.'''
        for child in self.w_bu_photo.winfo_children():
            child.destroy()
        window = tk.Toplevel(master=self.w_bu_photo)
        window.attributes("-topmost", True)
        window.focus_force()
        window.title("Photo")
        photomanager = mp.PhotoManager(level=self.level)

        def clear():
            '''Removes current photo from data pane.'''
            self.current_photo = None
            self.w_bu_photo.config(image="")
            self.w_bu_photo.image = ""

        def fetch_photo():
            '''Updates the photoframe with a new photo.'''
            try:
                img = ImageTk.PhotoImage(photomanager.take_photo())
                photoframe.config(image=img)
                photoframe.image = img
                window.after(250, fetch_photo)
            except:
                self.logger.error("Could not take photo. Webcam may be unavailable.")
        
        def on_close():
            '''Callback for when the window is closed.'''
            photomanager.destroy()
            window.destroy()

        def update():
            '''Pushes current photo to data pane.'''
            self.current_photo = photomanager.take_photo()
            img = ImageTk.PhotoImage(self.current_photo)
            self.w_bu_photo.config(image=img)
            self.w_bu_photo.image = img

        photoframe = ttk.Label(master=window)
        clearbut = ttk.Button(master=window, text="Clear", command=clear)
        updatebut = ttk.Button(master=window, text="Update", command=update)

        window.columnconfigure(index=0, weight=1000)
        window.columnconfigure(index=1, weight=1000)
        window.rowconfigure(index=0, weight=1000)
        window.rowconfigure(index=1, weight=1000)

        photoframe.grid(column=0, row=0, columnspan=2, sticky='nsew', padx=2, pady=2)
        clearbut.grid(column=0, row=1, sticky='nsew', padx=2, pady=2)
        updatebut.grid(column=1, row=1, sticky='nsew', padx=2, pady=2)

        window.protocol("WM_DELETE_WINDOW", on_close)
        fetch_photo()


    def read(self, event: tk.Event, source: str):
        '''Callback for when read field's read button is pressed.
        
        event: The tkinter event object associated with the callback.
        source: The source to read from.
        '''
        button = event.widget
        state = str(button.cget("state"))
        if state != "disabled":
            row = self.w_buttona_data.index(button)
            entry = self.w_input_data[row]
            field = self.w_la_data[row]
            for child in button.winfo_children():
                child.destroy()
            window = tk.Toplevel(master=button)
            window.attributes("-topmost", True)
            window.focus_force()
            window.title(field.cget("text"))

            if source == "WEIGHT":
                import random
                
                msg = ttk.Label(master=window)
                getbutton = ttk.Button(master=window, text="Update")

                def read_weight(*args):
                    '''Reads the current weight from another device.'''
                    reading = round(80+random.random()*10, 2)
                    msg.config(text=str(reading))
                    window.after(500, read_weight)

                def commit_weight(*args):
                    '''Inserts current weight into data pane.'''
                    entry.delete(0, "end")
                    entry.insert(0, msg.cget('text'))

                read_weight()
                getbutton.config(command=commit_weight)
                msg.grid(column=0, row=0, sticky="nsew", padx=10, pady=10)
                getbutton.grid(column=0, row=1, sticky="nsew", padx=10, pady=10)


    def readlist(self, event: tk.Event, source: str):
        '''Callback for when list field's read button is pressed.
        
        event: The tkinter event object associated with the callback.
        source: The source to read from.
        '''
        button = event.widget
        state = str(button.cget("state"))
        if state != "disabled":
            row = self.w_buttonb_data.index(button)
            entry = self.w_input_data[row]
            field = self.w_la_data[row]
            for child in button.winfo_children():
                child.destroy()
            window = tk.Toplevel(master=button)
            window.attributes("-topmost", True)
            window.focus_force()
            window.title(field.cget("text"))

            if source == "IDS":
                cur_id = self.last_doc.get("_id","")
                parents = self.db.item_parents(item=cur_id)
                base = self.db.item_get(id=parents[0]) if len(parents) > 0 else self.db.items_query(cat="Evacuation", selector={"Display Name":{"$eq":"DEHC"}}, fields=["_id", "Display Name"])[0]

                listids = [] if self.w_hidden_data[row] == "" else self.w_hidden_data[row]

                def addname():
                    '''Callback when tree -> list button is pressed.'''
                    id, name = tree.tree_get()
                    if name not in namelist.get(0, "end"):
                        listids.append(id)
                        namelist.insert("end", name)

                def removename():
                    '''Callback when tree <- list button is pressed.'''
                    indexes = namelist.curselection()
                    if len(indexes) > 0:
                        index, *_ = indexes
                        listids.pop(index)
                        namelist.delete(index)

                def submit(*args):
                    '''Submits current list to the data pane.'''
                    entry.config(values=namelist.get(0,"end"))
                    entry.current(0)
                    self.w_hidden_data[row] = listids

                tree = SearchTree(master=window, db=self.db, base=base, cats=self.cats, level=self.level, prepare=True, style="top.Treeview")
                namelistlb = ttk.Label(master=window, text="Guardians")
                namelist = tk.Listbox(master=window, selectmode=tk.SINGLE)
                for name in entry['values']:
                    namelist.insert("end", name)
                addbut = ttk.Button(master=window, text="→", command=addname)
                removebut = ttk.Button(master=window, text="←", command=removename)
                scanbut = ttk.Button(master=window, text="Scan")
                submitbut = ttk.Button(master=window, text="Update", command=submit)

                window.columnconfigure(0, weight=1000)
                window.columnconfigure(1, weight=1000)
                window.columnconfigure(2, weight=1000)
                window.columnconfigure(3, weight=1000)
                window.columnconfigure(4, weight=1000)
                window.columnconfigure(5, weight=1000)
                window.rowconfigure(0, weight=1, minsize=25)
                window.rowconfigure(1, weight=1000)
                window.rowconfigure(2, weight=1000)

                tree.grid(column=0, row=0, rowspan=3, sticky="nsew", padx=2, pady=2)
                addbut.grid(column=1, row=1, sticky="nsew", padx=2, pady=2)
                removebut.grid(column=1, row=2, sticky="nsew", padx=2, pady=2)
                namelistlb.grid(column=2, row=0, sticky="nsew", padx=2, pady=2)
                namelist.grid(column=2, row=1, rowspan=2, sticky="nsew", padx=2, pady=2)
                scanbut.grid(column=3, row=1, sticky="nsew", padx=2, pady=2)
                submitbut.grid(column=3, row=2, sticky="nsew", padx=2, pady=2)
            
            elif source == "PHYSIDS":

                def addid():
                    '''Callback when add button is pressed.'''
                    id = idvar.get()
                    if id not in idlist.get(0, "end") and len(id) > 0:
                        idlist.insert("end", id)
                        identry.delete(0, "end")

                def removeid():
                    '''Callback when remove button is pressed.'''
                    indexes = idlist.curselection()
                    if len(indexes) > 0:
                        index, *_ = indexes
                        idlist.delete(index)

                def getNFCorBarcode():
                    result = ''
                    if self.hardware is not None:
                        nfcResult = self.hardware.getCurrentNFCUID()
                        barcodeResult = self.hardware.getCurrentBarcode()
                        print(f'Barcode result: {barcodeResult}')
                        if nfcResult == '':
                            if barcodeResult != '':
                                result = barcodeResult
                        if barcodeResult == '':
                            if nfcResult != '':
                                result = nfcResult
                    else:
                        print('Hardware is None')
                    idvar.set(result)

                def submit():
                    '''Callback when submit button is pressed.'''
                    values = idlist.get(0,"end")
                    entry.config(values=values)
                    entry.current(0)
                    self.w_hidden_data[row] = values

                idvar = tk.StringVar()
                idlistlb = ttk.Label(master=window, text="Physical IDs")
                idlist = tk.Listbox(master=window, selectmode=tk.SINGLE)
                for id in entry['values']:
                    idlist.insert("end", id)
                identry = ttk.Entry(master=window, textvariable=idvar)
                addbut = ttk.Button(master=window, text="Add", command=addid)
                removebut = ttk.Button(master=window, text="Remove", command=removeid)
                scanbut = ttk.Button(master=window, text="Scan", command=getNFCorBarcode)
                submitbut = ttk.Button(master=window, text="Update", command=submit)

                window.columnconfigure(0, weight=1000)
                window.columnconfigure(1, weight=1000)
                window.columnconfigure(2, weight=1000)
                window.rowconfigure(0, weight=1, minsize=17)
                window.rowconfigure(1, weight=1, minsize=25)
                window.rowconfigure(2, weight=1000)
                window.rowconfigure(3, weight=1000)

                idlistlb.grid(column=0, row=0, columnspan=3, sticky="nsew", padx=2, pady=2)
                idlist.grid(column=0, row=1, rowspan=3, sticky="nsew", padx=2, pady=2)
                identry.grid(column=1, row=1, columnspan=2, sticky="nsew", padx=2, pady=2)
                addbut.grid(column=1, row=2, sticky="nsew", padx=2, pady=2)
                removebut.grid(column=1, row=3, sticky="nsew", padx=2, pady=2)
                scanbut.grid(column=2, row=2, sticky="nsew", padx=2, pady=2)
                submitbut.grid(column=2, row=3, sticky="nsew", padx=2, pady=2)


    def remove(self, *args):
        '''Callback for when the flag remove button is pressed'''
        self.w_li_flags.delete(self.w_li_flags.curselection())


    def save(self, *args):
        '''Callback for when the save button is pressed.'''
        doc = self.last_doc
        physid = None
        schema = self.db.schema_schema(cat=self.last_doc["category"])
        for index, (field, info) in enumerate(schema.items()):
            if self.w_hidden_data[index] == None:
                value = self.w_var_data[index].get()
            else:
                if info.get('type','') == 'list' and info.get('source') == 'PHYSIDS':
                    physid = self.w_hidden_data[index]
                    value = ""
                else:
                    value = self.w_hidden_data[index]
            if info['required'] == True and value == "":
                break
            doc[field] = value
        else:
            doc["flags"] = list(self.w_li_flags.get(0, "end"))
            if "_id" in doc:
                self.db.item_edit(id=doc["_id"], data=doc)
                id = None
            else:
                doc["_id"] = self.db.item_create(cat=doc["category"], doc=doc)
                id = doc["_id"]
            if physid != None:
                self.db.ids_edit(item=doc["_id"], ids=physid)
            if self.current_photo != None:
                self.db.photo_save(item=doc["_id"], img=self.current_photo)
            else:
                if self.last_photo != None:
                    self.db.photo_delete(item=doc["_id"])
            if self._save != None:
                self._save(id)
            self.back_doc = self.last_doc
            self.last_doc = doc
            return True
        self.logger.error("Could not save item because required fields are missing")
        return False


    def show(self, doc: dict = None):
        '''Displays a new document.
        
        doc: The document to display. If omitted, the previous document will be used.
        '''
        if doc != None:
            if self.last_doc != doc:
                self.back_doc = self.last_doc
                self.last_doc = doc
            id = self.last_doc.get("_id", "")
            self.last_photo = self.db.photo_load(item=id)

        for child in self.w_fr_data.winfo_children():
            child.destroy()
        self.w_bu_photo.config(image="")
        self.current_photo = self.last_photo
        self.w_li_flags.delete(0, "end")
        self.w_co_flags.set("")
        self.w_co_flags['values'] = []

        self.w_var_data = []
        self.w_la_data = []
        self.w_input_data = []
        self.w_buttona_data = []
        self.w_buttonb_data = []
        self.w_hidden_data = []

        self.w_bu_photo.config(command="")
        self.w_bu_edit.config(state="disabled")
        self.w_bu_cancel.config(state="disabled")
        self.w_bu_save.config(state="disabled")
        self.w_bu_delete.config(state="disabled")
        self.w_bu_add.config(state="disabled")
        self.w_bu_remove.config(state="disabled")
        self.w_co_flags.config(state="disabled")

        if len(self.last_doc) > 0:
            self.w_bu_edit.config(state="normal")
            cat = self.last_doc["category"]
            schema = self.db.schema_schema(cat=cat)
            title = f"{self.last_doc.get(self.db.schema_name(cat=cat), cat)} ({self.last_doc.get('_id','New')})"
            self.w_la_title.config(text=title)
            self.w_fr_data.columnconfigure(index=0, weight=1000)
            self.w_fr_data.columnconfigure(index=1, weight=1000)
            self.w_fr_data.columnconfigure(index=2, weight=1000)
            self.w_fr_data.columnconfigure(index=3, weight=1000)

            for index, (field, info) in enumerate(schema.items()):
                value = self.last_doc.get(field, "")
                var = tk.StringVar()
                var.set(value)
                label = ttk.Label(master=self.w_fr_data, text=field, justify=tk.LEFT, anchor="w")

                w_type = info['type']

                if w_type == "text":
                    entry = ttk.Entry(master=self.w_fr_data, textvariable=var, state="disabled")
                    buttona = None
                    buttonb = None
                    hidden = None

                elif w_type == "option":
                    entry = ttk.Combobox(master=self.w_fr_data, textvariable=var, values=info['options'], state="disabled")
                    buttona = None
                    buttonb = None
                    hidden = None

                elif w_type == "read":
                    entry = ttk.Entry(master=self.w_fr_data, textvariable=var, state="disabled")
                    buttona = ttk.Button(master=self.w_fr_data, text="Read", state="disabled")
                    source = info['source']
                    if source == "WEIGHT":
                        buttona.bind("<Button-1>", lambda e: self.read(event=e, source="WEIGHT"))
                    buttonb = None
                    hidden = None

                elif w_type == "list":
                    source = info['source']
                    if value != "":
                        names = [item["Display Name"] for item in self.db.items_get(ids=value, fields=["Display Name"])]
                    else:
                        last_id = self.last_doc.get("_id", "")
                        if last_id != "" and source == "PHYSIDS":
                            names = self.db.ids_get(item=self.last_doc["_id"])
                            value = names
                        else:
                            names = []
                    
                    entry = ttk.Combobox(master=self.w_fr_data, values=names, state="readonly")
                    if len(entry['values']) > 0:
                        entry.current(0)
                    
                    buttonb = ttk.Button(master=self.w_fr_data, text="Edit", state="disabled")
                    if source == "IDS":
                        buttonb.bind("<Button-1>", lambda e: self.readlist(event=e, source="IDS"))
                        buttona = ttk.Button(master=self.w_fr_data, text="Show", state="normal")
                        buttona.bind("<Button-1>", lambda e: self.showlist(event=e, source="IDS"))
                    elif source == "PHYSIDS":
                        buttonb.bind("<Button-1>", lambda e: self.readlist(event=e, source="PHYSIDS"))
                    else:
                        buttona = None
                    hidden = value

                elif w_type == "sum":
                    entry = ttk.Entry(master=self.w_fr_data)
                    if self.last_doc.get('_id','') != "":
                        children = self.db.container_children_all(container=self.last_doc["_id"], cat=info['cat'], result="DOC")
                        target = info['target']
                        default = info.get('default', 0)
                        items = []
                        defaulted = False
                        for child in children:
                            value = child.get(target, "")
                            if value == "":
                                value = default
                                defaulted = True
                            items.append(float(value))
                        itemsum = f"{sum(items):.1f}" if len(items) > 0 else ""
                        if defaulted == True:
                            itemsum += "*"
                        entry.insert(0, itemsum)
                    entry.config(state="disabled")
                    buttona = None
                    buttonb = None
                    hidden = ""
                
                elif w_type == "count":
                    entry = ttk.Entry(master=self.w_fr_data)
                    if self.last_doc.get('_id','') != "":
                        children = self.db.container_children_all(container=self.last_doc["_id"], cat=info['cat'], result="DOC")
                        counts = len(children)
                        entry.insert(0, counts)
                    entry.config(state="disabled")
                    buttona = None
                    buttonb = None
                    hidden = ""

                else:
                    entry = ttk.Label(master=self.w_fr_data)
                    buttona = None
                    buttonb = None
                    hidden = None

                label.grid(column=0, row=index, sticky="nsew", padx=1, pady=1)

                if buttona != None:
                    if buttonb != None:
                        entry.grid(column=1, row=index, sticky="nsew", padx=1, pady=1)
                        buttona.grid(column=2, row=index, sticky="nsew", padx=1, pady=1)
                        buttonb.grid(column=3, row=index, sticky="nsew", padx=1, pady=1)
                    else:
                        entry.grid(column=1, row=index, columnspan=2, sticky="nsew", padx=1, pady=1)
                        buttona.grid(column=3, row=index, sticky="nsew", padx=1, pady=1)
                else:
                    if buttonb != None:
                        entry.grid(column=1, row=index, columnspan=2, sticky="nsew", padx=1, pady=1)
                        buttonb.grid(column=3, row=index, sticky="nsew", padx=1, pady=1)
                    else:
                        entry.grid(column=1, row=index, columnspan=3, sticky="nsew", padx=1, pady=1)

                self.w_var_data.append(var)
                self.w_la_data.append(label)
                self.w_input_data.append(entry)
                self.w_buttona_data.append(buttona)
                self.w_buttonb_data.append(buttonb)
                self.w_hidden_data.append(hidden)
            
            if self.current_photo != None:
                img = ImageTk.PhotoImage(self.current_photo)
                self.w_bu_photo.config(image=img)
                self.w_bu_photo.image = img

            flags = self.last_doc.get("flags", [])
            flags.sort()
            for index, flag in enumerate(flags):
                self.w_li_flags.insert(index, flag)
            if len(flags) > 0:
                self.w_li_flags.selection_set(0)
            
            # Correct tab order
            for entry, buttona, buttonb in zip(self.w_input_data, self.w_buttona_data, self.w_buttonb_data):
                if entry != None:
                    entry.rise()
                if buttona != None:
                    buttona.rise()
                if buttonb != None:
                    buttonb.rise()


    def showlist(self, event: tk.Event, source: str):
        '''Callback for when the 'show' button is pressed for a given list field.
        
        event: The tkinter event object associated with the callback.
        source: The source to read from.
        '''
        button = event.widget
        state = str(button.cget("state"))
        if state != "disabled":
            row = self.w_buttona_data.index(button)
            entry = self.w_input_data[row]
            hidden = self.w_hidden_data[row]
            if source == "IDS":
                if len(entry['values']) > 0:
                    id = hidden[entry.current()]
                    self._show(id)


    def __del__(self):
        '''Runs when DataEntry object is deleted.'''
        self.logger.debug("DataEntry object destroyed")


# ----------------------------------------------------------------------------

class SearchTree(SuperWidget):
    '''A SuperWidget representing a searchable tree.
    
    base: The id of the tree's root node.
    cats: The categories which may be searched using this SearchTree.
    db: The database object which the widget uses for database transactions.
    headings: A mapping of column names -> column IDs in the search tree.
    logger: The logger object used for logging.
    master: The widget that the SearchTree's component widgets will be instantiated under.
    ops: The operations that can be used in searches.
    search_result: The contents of the last search result.
    selection: The last selected element of the tree.
    summables: A list of summable fields defined in the database schema.
    summation: Whether or not to sum summable fields in the tree.
    style: The style to use for the tree's appearence.
    _select: If present, a callback function that triggers when a tree item is selected.
    '''

    def __init__(self, master: tk.Misc, db: md.DEHCDatabase, base: dict, *, cats: list = [], level: str = "NOTSET", prepare: bool = True, select: Callable = None, style: str = ""):
        '''Constructs a SearchTree object.
        
        master: The widget that the SearchTree's component widgets will be instantiated under.
        db: The database object which the widget uses for database transactions.
        base: The document of the item upon which the tree is initially based.
        cats: The categories of items that can be searched.
        level: Minimum level of logging messages to report; "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL", "NONE".
        prepare: If true, automatically prepares widgets for packing.
        select: If present, a callback function that triggers when a tree item is selected.
        style: The style to use for the tree's appearence.
        '''
        super().__init__(master=master, db=db, level=level)

        self.cats = cats
        self.ops = ["=", "<", ">", "≤", "≥", "≠", "≈"]

        self._select = select

        self.base = base
        self.headings = {}
        self.selection = None
        self.search_result = None
        self.summables = self.db.schema_sums()
        self.summation = False
        self.style = style

        if prepare == True:
            self.prepare()


    def prepare(self):
        '''Constructs the frames and widgets of the SearchTree.'''
        # Frames & Canvas
        self.w_fr_search = ttk.Frame(master=self.w_fr)

        self.w_fr.columnconfigure(0, weight=500)
        self.w_fr.columnconfigure(1, weight=1, minsize=16)
        self.w_fr.columnconfigure(2, weight=1000)
        self.w_fr.columnconfigure(3, weight=1, minsize=16)
        self.w_fr.rowconfigure(0, weight=1, minsize=25)
        self.w_fr.rowconfigure(1, weight=1000)
        self.w_fr.rowconfigure(2, weight=1, minsize=17)

        self.w_fr_search.columnconfigure(0, weight=1000)
        self.w_fr_search.columnconfigure(1, weight=1000)
        self.w_fr_search.columnconfigure(2, weight=1000)
        self.w_fr_search.columnconfigure(3, weight=1000)
        self.w_fr_search.columnconfigure(4, weight=1000)
        self.w_fr_search.columnconfigure(5, weight=1000)
        self.w_fr_search.rowconfigure(0, weight=1000)

        # Variables
        self.w_var_cat = tk.StringVar()
        self.w_var_cat.trace("w", self.search_cat)
        self.w_var_field = tk.StringVar()
        self.w_var_op = tk.StringVar()
        self.w_var_value = tk.StringVar()
        self.w_var_summation = tk.IntVar()
        self.w_var_summation.trace("w", self.summation_toggle)

        # Widgets
        self.w_co_cat = ttk.Combobox(master=self.w_fr_search, values=self.cats, textvariable=self.w_var_cat, state="readonly")
        self.w_co_field = ttk.Combobox(master=self.w_fr_search, textvariable=self.w_var_field, state="readonly")
        self.w_co_op = ttk.Combobox(master=self.w_fr_search, value=self.ops, textvariable=self.w_var_op, state="readonly")
        self.w_en_value = ttk.Entry(master=self.w_fr_search, textvariable=self.w_var_value)
        self.w_bu_search = ttk.Button(master=self.w_fr_search, text="Search", command=self.search)
        self.w_bu_scan = ttk.Button(master=self.w_fr_search, text="Scan", command=self.scan)
        self.w_li_search = tk.Listbox(master=self.w_fr, selectmode=tk.SINGLE, relief=tk.GROOVE, exportselection=False)
        self.w_tr_tree = ttk.Treeview(master=self.w_fr, columns=list(range(1,len(self.summables)+2)), show="tree", selectmode="browse", style=self.style)
        self.w_ch_summation = ttk.Checkbutton(master=self.w_fr, variable=self.w_var_summation, text="Show Sums?")
        if self.style == "bottom.Treeview":
            self.w_li_search.configure(bg="#fcf0cf")

        self.w_li_search.bind("<<ListboxSelect>>", self.search_select)
        self.w_tr_tree.bind("<<TreeviewSelect>>", self.tree_select)
        self.w_tr_tree.bind("<<TreeviewOpen>>", lambda *_: self.tree_open())
        self.w_tr_tree.bind("<Button-3>", self.tree_rebase)

        self.w_co_cat.current(0)
        self.w_co_field.current(1)
        self.w_co_op.current(0)
        self.w_tr_tree.column(column="#0", anchor=tk.E, stretch=False, width=300)
        self.w_tr_tree.heading("#0", text="Item")
        for index, field in enumerate(self.summables):
            headname = field
            headid = index+1
            self.headings[headname] = index
            self.w_tr_tree.column(column=headid, anchor=tk.E, stretch=False, width=120)
            self.w_tr_tree.heading(headid, text=headname)
        self.w_tr_tree.column(column=len(self.summables)+1, anchor=tk.E, stretch=False, width=120)
        self.w_tr_tree.heading(len(self.summables)+1, text="Flags")

        # Scrollbars
        self.w_sc_tree = ttk.Scrollbar(master=self.w_fr, orient="vertical", command=self.w_tr_tree.yview)
        self.w_tr_tree.config(yscrollcommand=self.w_sc_tree.set)
        self.w_sc_search = ttk.Scrollbar(master=self.w_fr, orient="vertical", command=self.w_li_search.yview)
        self.w_li_search.config(yscrollcommand=self.w_sc_search.set)

        # Misc
        self.tree_refresh()
        self.w_tr_tree.selection_set(self.base["_id"])
        


    def _pack_children(self):
        '''Packs & grids children frames and widgets of the SearchTree.'''
        # Frames & Canvas
        self.w_fr_search.grid(column=0, row=0, columnspan=4, sticky="nsew")

        # Widgets
        self.w_co_cat.grid(column=0, row=0, sticky="nsew", padx=1, pady=1)
        self.w_co_field.grid(column=1, row=0, sticky="nsew", padx=1, pady=1)
        self.w_co_op.grid(column=2, row=0, sticky="nsew", padx=1, pady=1)
        self.w_en_value.grid(column=3, row=0, sticky="nsew", padx=1, pady=1)
        self.w_bu_search.grid(column=4, row=0, sticky="nsew", padx=1, pady=1)
        self.w_bu_scan.grid(column=5, row=0, sticky="nsew", padx=1, pady=1)
        self.w_li_search.grid(column=0, row=1, rowspan=2, sticky="nsew", padx=1, pady=1)
        self.w_sc_search.grid(column=1, row=1, rowspan=2, sticky="nse", padx=1, pady=1)
        self.w_tr_tree.grid(column=2, row=1, sticky="nsew", padx=1, pady=1)
        self.w_sc_tree.grid(column=3, row=1, sticky="nse", padx=1, pady=1)
        self.w_ch_summation.grid(column=2, row=2, columnspan=2, sticky="nsew", padx=1, pady=1)


    def scan(self, *args):
        '''Callback for when the scan button is pressed.'''
        for child in self.w_bu_scan.winfo_children():
            child.destroy()
        window = tk.Toplevel(master=self.w_bu_scan)
        window.attributes("-topmost", True)
        window.focus_force()
        window.title("Scan")
        
        def scan():
            self.logger.info("You pressed SCAN.")

        def find():
            physid = input_var.get()
            ids = self.db.ids_find(physid=physid)
            if len(ids) > 0:
                id, *_ = ids
                self.tree_focus(goal=id, rebase=True)

        window.bind("<Return>", lambda *_: find())
        input_var = tk.StringVar()
        input_box = ttk.Entry(master=window, textvariable=input_var)
        scan_button = ttk.Button(master=window, text="Scan", command=scan)
        find_button = ttk.Button(master=window, text="Find", command=find)
        input_box.focus_set()

        window.columnconfigure(0, weight=1000)
        window.columnconfigure(1, weight=1000)
        window.rowconfigure(0, weight=1000)
        window.rowconfigure(1, weight=1000)

        input_box.grid(column=0, row=0, columnspan=2, sticky="nsew", padx=2, pady=2)
        scan_button.grid(column=0, row=1, sticky="nsew", padx=2, pady=2)
        find_button.grid(column=1, row=1, sticky="nsew", padx=2, pady=2)


    def search(self, *args):
        '''Callback for when the search button is pressed.'''
        cat = self.w_var_cat.get()
        field = self.w_var_field.get()
        value = self.w_var_value.get()
        opvalue = {
            "=": {"$eq": value}, 
            "<": {"$lt": value}, 
            ">": {"$gt": value}, 
            "≤": {"$lte": value},
            "≥": {"$gte": value}, 
            "≠": {"$ne": value},
            "≈": {"$regex": value}
            }[self.w_var_op.get()]
        selector = {field: opvalue}
        name = self.db.schema_name(cat=cat)
        fields = ["_id", name]
        sort = [{key: 'asc'} for key in self.db.schema_keys(cat=cat)]
        self.search_result = self.db.items_query(cat=cat, selector=selector, fields=fields, sort=sort)
        self.w_li_search.delete(0, "end")
        for index, result in enumerate(self.search_result):
            self.w_li_search.insert(index, result[name])


    def search_cat(self, *args):
        '''Callback for when the search category is changed.'''
        cat = self.w_var_cat.get()
        fields = ['_id']+self.db.schema_fields(cat=cat)

        # Searching by IDS and PHYSIDS fields doesn't work, so hide them:
        for field, info in self.db.schema_schema(cat=cat).items():
            if info.get('source','') in ["IDS", "PHYSIDS"]:
                fields.remove(field)

        self.w_co_field['values'] = fields
        self.w_co_field.current(1)


    def search_select(self, *args):
        '''Callback for when an item in the search is clicked.'''
        event, = args
        selected = event.widget.curselection()
        if len(selected) == 1:
            index, = selected
            id = self.search_result[index]["_id"]
            self.tree_focus(goal=id, rebase=True)


    def summation_toggle(self, *args):
        '''Callback for when the summation checkbox is toggled.'''
        state = self.w_var_summation.get()
        if state == 0:
            self.summation = False
            self.w_tr_tree.config(show="tree")
        elif state == 1:
            self.summation = True
            self.w_tr_tree.config(show="tree headings")
        self.tree_refresh()


    def tree_focus(self, goal: str, rebase: bool = False):
        '''Selects a node in the tree, opening parent nodes as required.
        
        goal: The node to select.
        rebase: If true, will rebase in attempt to find focus item.
        '''
        path = self.db.item_parents_all(item=goal)
        path.reverse()
        old_base = self.base
        while True:
            for step in path:
                if self.w_tr_tree.exists(item=step):
                    self.tree_open(node=step)
            if self.w_tr_tree.exists(item=goal):
                self.w_tr_tree.selection_set(goal)
                self.w_tr_tree.see(item=goal)
            elif rebase == True and len(path) > 0:
                if self.base != path[0]:
                    self.base = self.db.item_get(id=path[0])
                    self.tree_refresh()
                    continue
                else:
                    self.base = old_base
                    self.tree_refresh()
            break


    def tree_get(self):
        '''Returns a tuple consisting of the currently selected node's id and name.'''
        id, *_ = self.w_tr_tree.selection()
        name = self.w_tr_tree.item(item=id)['text']
        return (id, name)


    def tree_insert(self, parent: str, iid: str, text: str, values: list = []):
        '''Inserts a node into the tree view.
        
        parent: The id of the parent node in the tree.
        iid: The id of the node being inserted.
        text: The text of the node.
        values: The values to put in the nodes's columns.
        '''
        self.w_tr_tree.insert(parent=parent, index=1000000, iid=iid, text=text, values=values)
        if len(self.db.container_children(container=iid)) > 0:
            self.w_tr_tree.insert(parent=iid, index=1000000, iid=iid+"_stub")


    def tree_rebase(self, *args):
        '''Callback for when the tree is rebased using right-click.'''
        event, = args
        target = event.widget.identify_row(event.y)
        self.w_tr_tree.selection_set(target)
        if self.w_tr_tree.parent(target) == "":
            parents = self.db.item_parents(item=target, result="DOC")
            if len(parents) > 0:
                self.base, *_ = parents
        else:
            self.base = self.db.item_get(id=target)
        self.tree_refresh()
        self.tree_open(target)


    def tree_refresh(self):
        '''Refreshes the tree view.'''
        base_id = self.base["_id"]
        self.selection = self.w_tr_tree.selection()
        self.w_tr_tree.delete(*self.w_tr_tree.get_children(item=""))
        if self.db.item_exists(id=base_id):
            base_name = self.base[self.db.schema_name(id=base_id)]
            self.tree_insert(parent="", iid=base_id, text=base_name)
            self.tree_sum(node=base_id)
            if len(self.selection) == 1:
                selection, = self.selection
                self.tree_focus(goal=selection, rebase=True)


    def tree_select(self, *args):
        '''Callback for when an item in the tree is selected.'''
        event, = args
        self.selection = event.widget.selection()
        if self._select != None:
            if len(self.selection) == 1:
                id, = self.selection
                doc = self.db.item_get(id=id, lazy=True)
                self._select(doc)


    def tree_open(self, node: str = None):
        '''Open a node on the tree view.
        
        node: The node to open. If omitted, opens currently selected node.
        '''
        self.logger.debug("Tree opened")
        start_time = time.perf_counter()
        self.selection = self.w_tr_tree.selection()
        if node != None:
            id = node
        elif self.w_tr_tree.focus() != "":
            id = self.w_tr_tree.focus()
        elif len(self.selection) == 1:
            id, = self.selection
        else:
            id = None
            raise RuntimeError("Unable to open tree nodes")

        children = self.db.container_children(container=id, result="DOC")
        self.logger.debug("Container Load finished at  %.5f" % (time.perf_counter() - start_time)  )
        children.sort(key=lambda doc: (doc["category"], doc[self.db.schema_name(cat=doc["category"])]))
        self.logger.debug("Children sort finished at  %.5f" % (time.perf_counter() - start_time)  )
        self.w_tr_tree.delete(*self.w_tr_tree.get_children(item=id))
        for child in children:
            child_id = child["_id"]
            child_name = child[self.db.schema_name(id=child_id)]
            self.tree_insert(parent=id, iid=child_id, text=child_name)
            self.tree_sum(node=child_id)
        self.w_tr_tree.item(item=id, open=True)
        self.logger.debug("Tree open finished in %.5f" % (time.perf_counter() - start_time)  )


    def tree_sum(self, node: str):
        '''Sums and displays summable fields of a node.
        
        node: The node to display sums of.
        '''
        if self.summation == True:
            schema = self.db.schema_schema(id=node)
            values = [""]*(len(self.summables)+1)
            doc = self.db.item_get(id=node)
            all_children = self.db.container_children_all(container=node, result="DOC")
            
            for field, info in schema.items():
                if field in self.summables:
                    defaulted = False

                    if info['type'] == "sum":
                        children = [child for child in all_children if child['category'] in info['cat']]
                        target = info['target']
                        default = info.get('default', 0)
                        items = []
                        for child in children:
                            value = child.get(target, "")
                            if value == "":
                                value = default
                                defaulted = True
                            items.append(float(value))
                        itemsum = f"{sum(items):.1f}" if len(items) > 0 else ""
                    elif info['type'] == "count":
                        children = [child for child in all_children if child['category'] in info['cat']]
                        itemsum = len(children)
                    else:
                        value = doc.get(field, "")
                        if value == "":
                            value = info.get('default', 0)
                            defaulted = True
                        itemsum = f"{float(value):.1f}"

                    if defaulted == True:
                        itemsum += "*"
                    values[self.headings[field]] = itemsum

            all_flags = []
            for child in [doc]+all_children:
                flags = child.get("flags",[])
                all_flags.extend(flags)
            all_flags = list(dict.fromkeys(all_flags))
            minilist = ""
            for flag in all_flags:
                minilist += f"{flag[:2]}"
            values[len(self.summables)] = minilist

            self.w_tr_tree.item(item=node, values=values)



    def __del__(self):
        '''Runs when SearchTree object is deleted.'''
        self.logger.debug("SearchTree object destroyed")


# ----------------------------------------------------------------------------

class ContainerManager(SuperWidget):
    '''A SuperWidget representing a container manager.
    
    bookmarks: Dictionary describing where to base trees when bookmark buttons are pressed.
    cats: The categories which may be searched using this ContainerManager.
    db: The database object which the widget uses for database transactions.
    level: Minimum level of logging messages to report; "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL", "NONE".
    logger: The logger object used for logging.
    master: The widget that the ContainerManager's component widgets will be instantiated under.
    ops: The operations that can be used in seraches.
    select: If present, a callback function that triggers when a tree item is selected.
    '''

    def __init__(self, master: tk.Misc, db: md.DEHCDatabase, topbase: dict, botbase: dict,  *, bookmarks: str = "bookmarks.json", cats: list = [], level: str = "NOTSET", prepare: bool = True, select: Callable = None):
        '''Constructs a ContainerManager object.
        
        master: The widget that the ContainerManager's component widgets will be instantiated under.
        db: The database object which  the widget uses for database transactions.
        topbase: The document of the item upon which the top tree is initially based.
        botbase: The document of the item upon which the bottom tree is initially based.
        bookmarks: Relative filepath to the bookmarks definition file.
        cats: The categories of items that can be searched.
        level: Minimum level of logging messages to report; "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL", "NONE".
        ops: The operations that can be used in seraches.
        prepare: If true, automatically prepares widgets for packing.
        select: If present, a callback function that triggers when a tree item is selected.
        '''
        super().__init__(master=master, db=db, level=level)

        self.topbase = topbase
        self.botbase = botbase
        self.cats = cats
        self.level = level
        self.select = select

        with open(bookmarks, "r") as f:
            self.bookmarks = json.loads(f.read())

        if prepare == True:
            self.prepare()


    def prepare(self):
        '''Constructs the frames and widgets of the ContainerManager.'''
        # Frames
        self.w_fr_bookmarks = ttk.Frame(master=self.w_fr)
        
        # Widgets
        self.w_bu_bm1 = ttk.Button(master=self.w_fr_bookmarks, text=self.bookmarks["1"]["name"], command=lambda *_: self.bookmark(preset="1"))
        self.w_bu_bm2 = ttk.Button(master=self.w_fr_bookmarks, text=self.bookmarks["2"]["name"], command=lambda *_: self.bookmark(preset="2"))
        self.w_bu_bm3 = ttk.Button(master=self.w_fr_bookmarks, text=self.bookmarks["3"]["name"], command=lambda *_: self.bookmark(preset="3"))
        self.w_bu_bm4 = ttk.Button(master=self.w_fr_bookmarks, text=self.bookmarks["4"]["name"], command=lambda *_: self.bookmark(preset="4"))
        self.w_la_top = ttk.Label(master=self.w_fr, text="Source")
        self.w_se_top = SearchTree(master=self.w_fr, db=self.db, base=self.topbase, cats=self.cats, level=self.level, prepare=True, select=self.select, style="top.Treeview")
        self.w_bu_move_item = ttk.Button(master=self.w_fr, text="Move Item", command=self.move)
        self.w_bu_move_subs = ttk.Button(master=self.w_fr, text="Move Sub-Items", command=self.submove)
        self.w_la_bottom = ttk.Label(master=self.w_fr, text="Destination")
        self.w_se_bottom = SearchTree(master=self.w_fr, db=self.db, base=self.botbase, cats=self.cats, level=self.level, prepare=True, style="bottom.Treeview")

        self.w_fr.columnconfigure(0, weight=1000)
        self.w_fr.columnconfigure(1, weight=1000)
        self.w_fr.rowconfigure(0, weight=1, minsize=17)
        self.w_fr.rowconfigure(1, weight=1, minsize=17)
        self.w_fr.rowconfigure(2, weight=1000)
        self.w_fr.rowconfigure(3, weight=1, minsize=25)
        self.w_fr.rowconfigure(4, weight=1, minsize=17)
        self.w_fr.rowconfigure(5, weight=1000)
        self.w_fr.rowconfigure(6, weight=1) # Currently unused, but reserved for things below both trees

        self.w_fr_bookmarks.columnconfigure(0, weight=1000)
        self.w_fr_bookmarks.columnconfigure(1, weight=1000)
        self.w_fr_bookmarks.columnconfigure(2, weight=1000)
        self.w_fr_bookmarks.columnconfigure(3, weight=1000)
        self.w_fr_bookmarks.rowconfigure(0, weight=1000)


    def _pack_children(self):
        '''Packs & grids children frames and widgets of the ContainerManager.'''
        self.w_fr_bookmarks.grid(column=0, row=0, columnspan=2, sticky="nsew", padx=2, pady=2)
        self.w_bu_bm1.grid(column=0, row=0, sticky="nsew", padx=2, pady=2)
        self.w_bu_bm2.grid(column=1, row=0, sticky="nsew", padx=2, pady=2)
        self.w_bu_bm3.grid(column=2, row=0, sticky="nsew", padx=2, pady=2)
        self.w_bu_bm4.grid(column=3, row=0, sticky="nsew", padx=2, pady=2)
        self.w_la_top.grid(column=0, row=1, columnspan=2, sticky="nsew", padx=2, pady=1)
        self.w_se_top.grid(column=0, row=2, columnspan=2, sticky="nsew", padx=2, pady=2)
        self.w_bu_move_item.grid(column=0, row=3, sticky="nsew", padx=2, pady=4)
        self.w_bu_move_subs.grid(column=1, row=3, sticky="nsew", padx=2, pady=4)
        self.w_la_bottom.grid(column=0, row=4, columnspan=2, sticky="nsew", padx=2, pady=1)
        self.w_se_bottom.grid(column=0, row=5, columnspan=2, sticky="nsew", padx=2, pady=2)



    def base(self, newbase: str = None):
        '''Sets or returns the base of the top tree.
        
        newbase: If specified, rebases the top tree to the new base.
        '''
        if newbase == None:
            return self.w_se_top.base
        else:
            self.w_se_top.base = newbase


    def basebot(self, newbase: str = None):
        '''Sets or returns the base of the bottom tree.
        
        newbase: If specified, rebases the bottom tree to the new base.
        '''
        if newbase == None:
            return self.w_se_bottom.base
        else:
            self.w_se_bottom.base = newbase


    def bookmark(self, preset: str):
        '''Sets both trees to the settings described by a bookmark.
        
        preset: Which bookmark to use.
        '''
        guide = self.bookmarks[preset]
        top, bottom = self.db.items_get(ids=[guide["top"], guide["bottom"]])
        self.base(newbase=top)
        self.basebot(newbase=bottom)
        self.refresh()
        self.highlight(item=top["_id"], botitem=bottom["_id"])
        self.open()
        self.botopen()
        

    def highlight(self, item: str = None, botitem: str = None):
        '''Selects an item in the top and/or bottom tree with the matching id.
        
        Note: requires item to already exist in the tree.
        '''
        if item != None:
            self.w_se_top.tree_focus(goal=item, rebase=True)
        if botitem != None:
            self.w_se_bottom.tree_focus(goal=botitem, rebase=True)


    def move(self, *args):
        '''Callback for when the item move button is pressed.'''
        target, *_ = self.w_se_top.selection
        source, *_ = self.db.item_parents(item=target)
        destination, *_ = self.w_se_bottom.selection
        self.db.container_move(from_con=source, to_con=destination, item=target)
        self.highlight(item=source)
        self.refresh()
        self.highlight(botitem=destination)
        self.open()
        self.botopen()


    def submove(self, *args):
        '''Callback for when the sub-item move button is pressed.'''
        source, *_ = self.w_se_top.selection
        targets = self.db.container_children(container=source)
        destination, *_ = self.w_se_bottom.selection
        self.db.container_moves(from_con=source, to_con=destination, items=targets)
        self.highlight(item=source)
        self.refresh()
        self.highlight(botitem=destination)
        self.botopen()


    def botopen(self):
        '''Opens the bottom tree's currently selected container.'''
        self.w_se_bottom.tree_open()


    def open(self):
        '''Opens the top tree's currently selected container.'''
        self.w_se_top.tree_open()


    def refresh(self):
        '''Refreshes both trees.'''
        self.w_se_top.tree_refresh()
        self.w_se_bottom.tree_refresh()


    def selections(self):
        '''Returns a tuple containing the IDs of the selected items in the top and bottom tree respectively.'''
        top, *_ = self.w_se_top.selection
        bot, *_ = self.w_se_bottom.selection
        return (top, bot)


    def __del__(self):
        '''Runs when ContainerManager object is deleted.'''
        self.logger.debug("ContainerManager object destroyed")


# ----------------------------------------------------------------------------

class StatusBar(SuperWidget):
    '''A SuperWidget representing a database status bar.
    
    db: The database object which the widget uses for database transactions.
    logger: The logger object used for logging.
    master: The widget that the StatusBar's component widgets will be instantiated under.
    '''

    def __init__(self, master: tk.Misc, db: md.DEHCDatabase, *, level: str = "NOTSET", prepare: bool = True):
        '''Constructs a StatusBar object.
        
        master: The widget that the StatusBar's component widgets will be instantiated under.
        level: Minimum level of logging messages to report; "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL", "NONE".
        prepare: If true, automatically prepares widgets for packing.
        '''
        super().__init__(master=master, db=db, level=level)

        if prepare == True:
            self.prepare()


    def prepare(self):
        '''Constructs the frames and widgets of the StatusBar.'''
        self.w_status = ttk.Label(master=self.w_fr, text="Status Online", justify=tk.LEFT, anchor="w")
        
    
    def _pack_children(self):
        '''Packs & grids children frames and widgets of the StatusBar.'''
        self.w_status.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)


    def __del__(self):
        '''Runs when StatusBar object is deleted.'''
        self.logger.debug("StatusBar object destroyed")
