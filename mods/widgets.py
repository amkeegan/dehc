'''The module containing objects that create and manage groups of tkinter widgets.'''

import tkinter as tk
from tkinter import ttk
from typing import Callable

import mods.database as md
import mods.log as ml


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
    db: The database object which the widget uses for database transactions.
    last_doc: The last doc that was shown in the data pane.
    logger: The logger object used for logging.
    master: The widget that the DataEntry's component widgets will be instantiated under.
    _delete: If present, a callback function that triggers when an item is deleted.
    _save: If present, a callback function that triggers when an item is saved.
    '''

    def __init__(self, master: tk.Misc, db: md.DEHCDatabase, *, cats: list = [], delete: Callable = None, flags: list = [], level: str = "NOTSET", prepare: bool = True, save: Callable = None):
        '''Constructs a DataEntry object.
        
        master: The widget that the DataEntry's component widgets will be instantiated under.
        cats: The categories of items that can be created using the New button.
        flags: The flags that can be added to items using this DataEntry.
        level: Minimum level of logging messages to report; "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL", "NONE".
        save: If present, a callback function that triggers when an item is saved.
        prepare: If true, automatically prepares widgets for packing.
        '''
        super().__init__(master=master, db=db, level=level)

        self.cats = cats
        self.flags = flags
        self.last_doc = {}
        self._delete = delete
        self._save = save

        if prepare == True:
            self.prepare()


    def prepare(self):
        '''Constructs the frames and widgets of the DataEntry.'''
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
        self.w_la_title = ttk.Label(master=self.w_fr, text="Title", font="Arial 12 bold")
        self.w_bu_photo = ttk.Button(master=self.w_fr, text="Photo", command=self.photo)
        self.w_la_flags = ttk.Label(master=self.w_fr_flags, text="Flags")
        self.w_li_flags = tk.Listbox(master=self.w_fr_flags, selectmode=tk.SINGLE, relief=tk.GROOVE, exportselection=False)
        self.w_co_flags = ttk.Combobox(master=self.w_fr_flags, values=self.flags, textvariable=self.w_var_flags, state="readonly")
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
        self.w_co_flags.current(0)
        self.w_co_cat.current(0)
        self.show()

        # Scrollbars
        self.w_sc_flags = ttk.Scrollbar(master=self.w_fr_flags, orient="vertical", command=self.w_li_flags.yview)
        self.w_li_flags.config(yscrollcommand=self.w_sc_flags.set)


    def _pack_children(self):
        '''Packs & grids children frames and widgets of the DataEntry.'''
        self.w_la_title.grid(column=0, row=0, columnspan=3, sticky="nsew", padx=2, pady=2)
        self.w_bu_photo.grid(column=0, row=1, sticky="nsew", padx=2, pady=2)
        self.w_fr_flags.grid(column=1, row=1, columnspan=2, sticky="nsew", padx=2, pady=2)
        self.w_fr_body.grid(column=0, row=2, columnspan=2, sticky="nsew", padx=2, pady=2)
        self.w_fr_data.grid(column=0, row=0, sticky="nsew")
        self.w_fr_foot.grid(column=0, row=3, columnspan=3, sticky="nsew", padx=2, pady=1)

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


    def add(self, *args):
        '''Callback for when the flag add button is pressed'''
        flag = self.w_var_flags.get()
        if flag not in self.w_li_flags.get(0, "end"):
            self.w_li_flags.insert("end", flag)


    def cancel(self, *args):
        '''Callback for when the cancel button is pressed.'''
        self.show()


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
            self.logger.error("Could not delete top level item.")


    def edit(self, *args):
        '''Callback for when the edit button is pressed'''
        for entry, buttona, buttonb, hidden in zip(self.w_input_data, self.w_buttona_data, self.w_buttonb_data, self.w_hidden_data):
            if hidden == None:
                entry.config(state="normal")
            if buttona != None:
                buttona.config(state="normal")
            if buttonb != None:
                buttonb.config(state="normal")
        self.w_bu_edit.config(state="disabled")
        self.w_bu_cancel.config(state="normal")
        self.w_bu_save.config(state="normal")
        self.w_bu_delete.config(state="normal")
        self.w_bu_add.config(state="normal")
        self.w_bu_remove.config(state="normal")
        self.w_co_flags.config(state="normal")


    def new(self, *args):
        '''Callback for when the new button is pressed.'''
        self.last_doc = {"category": self.w_var_cat.get()}
        self.show()
        self.edit()
        self.w_bu_delete.config(state="disabled")


    def photo(self, *args):
        '''Callback for when the photo is pressed.'''
        self.logger.info("Pressed PHOTO")


    def read(self, event: tk.Event, source: str):
        '''Callback for when read field's read button is pressed.
        
        event: The tkinter event object associated with the callback.
        source: The source to read from.
        '''
        button = event.widget
        row = self.w_buttona_data.index(button)
        entry = self.w_input_data[row]
        field = self.w_la_data[row]
        for child in button.winfo_children():
            child.destroy()
        window = tk.Toplevel(master=button)
        window.title(field.cget("text"))

        if source == "WEIGHT":
            import random
            
            msg = tk.Label(master=window, font="Arial 14 bold")
            getbutton = tk.Button(master=window, text="Update", font="Arial 14 bold")

            def read_weight(*args):
                '''Reads the current weight from another device.'''
                reading = round(90+random.random()*5, 2)
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
        row = self.w_buttona_data.index(button)
        entry = self.w_input_data[row]
        field = self.w_la_data[row]
        for child in button.winfo_children():
            child.destroy()
        window = tk.Toplevel(master=button)
        window.title(field.cget("text"))

        if source == "IDS":
            cur_id = self.last_doc.get("_id","")
            parents = self.db.item_parents(item=cur_id)
            children = self.db.container_children(container=cur_id)
            parents_children = self.db.containers_children(containers=parents)
            name_ids = list(dict.fromkeys(parents+children+parents_children))
            if cur_id in name_ids:
                name_ids.remove(cur_id)
            db_result = self.db.items_get(ids=name_ids, fields=["_id", "Display Name"])
            names = [item["Display Name"] for item in db_result]
            ids = [item["_id"] for item in db_result]
            active_ids = [] if self.w_hidden_data[row] == "" else self.w_hidden_data[row]

            namevar = tk.StringVar()

            def add(*args):
                '''Adds name to the list.'''
                name = namevar.get()
                if name not in namelist.get(0, "end"):
                    namelist.insert("end", name)
                    active_ids.append(ids[namecombo.current()])
            
            def remove(*args):
                '''Removes name from the list.'''
                index, = namelist.curselection()
                namelist.delete(index)
                active_ids.pop(index)
            
            def submit(*args):
                '''Submits current list to the data pane.'''
                entry.config(values=namelist.get(0,"end"))
                entry.current(0)
                self.w_hidden_data[row] = active_ids

            namelist = tk.Listbox(master=window, font="Arial 12 bold", selectmode=tk.SINGLE)
            for name in entry.cget("values"):
                namelist.insert("end", name)
            namecombo = ttk.Combobox(master=window, values=names, textvariable=namevar, font="Arial 12 bold", state="readonly")
            addbutton = tk.Button(master=window, text="Add", command=add, font="Arial 12 bold")
            removebutton = tk.Button(master=window, text="Remove", command=remove, font="Arial 12 bold")
            submitbutton = tk.Button(master=window, text="Update", command=submit, font="Arial 12 bold")
            namelist.grid(column=0, row=0, rowspan=3, sticky="nsew", padx=2, pady=2)
            namecombo.grid(column=1, row=0, sticky="nsew", padx=2, pady=2)
            addbutton.grid(column=1, row=1, sticky="nsew", padx=2, pady=2)
            removebutton.grid(column=1, row=2, sticky="nsew", padx=2, pady=2)
            submitbutton.grid(column=0, row=3, columnspan=2, sticky="nsew", padx=2, pady=2)


    def remove(self, *args):
        '''Callback for when the flag remove button is pressed'''
        self.w_li_flags.delete(self.w_li_flags.curselection())


    def save(self, *args):
        '''Callback for when the save button is pressed.'''
        doc = self.last_doc
        schema = self.db.schema_schema(cat=self.last_doc["category"])
        for index, (field, info) in enumerate(schema.items()):
            if self.w_hidden_data[index] == None:
                value = self.w_var_data[index].get()
            else:
                value = self.w_hidden_data[index]
            if info['required'] == True and value == "":
                break
            doc[field] = value
        else:
            old_flags = set([field for field in self.last_doc.keys() if field not in schema and field not in ["_id", "_rev", "category"]])
            new_flags = set(self.w_li_flags.get(0, "end"))
            flags = old_flags.union(new_flags)
            for flag in flags:
                if flag in new_flags:
                    doc[flag] = 1
                else:
                    doc[flag] = 0
            if "_id" in doc:
                self.db.item_edit(id=doc["_id"], data=doc)
                id = None
            else:
                id = self.db.item_create(cat=doc["category"], doc=doc)
            if self._save != None:
                self._save(id)
            self.last_doc = doc
            return True
        self.logger.error("Could not save item because required fields are missing.")
        return False


    def show(self, doc: dict = None):
        '''Displays a new document.
        
        doc: The document to display. If omitted, the previous document will be used.
        '''
        if doc != None:
            self.last_doc = doc

        for child in self.w_fr_data.winfo_children():
            child.destroy()
        self.w_li_flags.delete(0, "end")

        self.w_var_data = []
        self.w_la_data = []
        self.w_input_data = []
        self.w_buttona_data = []
        self.w_buttonb_data = []
        self.w_hidden_data = []

        self.w_bu_edit.config(state="disabled")
        self.w_bu_cancel.config(state="disabled")
        self.w_bu_save.config(state="disabled")
        self.w_bu_delete.config(state="disabled")
        self.w_bu_add.config(state="disabled")
        self.w_bu_remove.config(state="disabled")
        self.w_co_flags.config(state="disabled")

        if len(self.last_doc) > 0:
            self.w_bu_edit.config(state="normal")
            schema = self.db.schema_schema(cat=self.last_doc["category"])
            self.w_la_title.config(text=self.last_doc.get(self.db.schema_name(cat=self.last_doc["category"]), ""))
            self.w_fr_data.columnconfigure(index=0, weight=1000)
            self.w_fr_data.columnconfigure(index=1, weight=1000)
            self.w_fr_data.columnconfigure(index=2, weight=1000)
            self.w_fr_data.columnconfigure(index=3, weight=1000)

            for index, (field, info) in enumerate(schema.items()):
                value = self.last_doc.get(field, "")
                var = tk.StringVar()
                var.set(value)
                label = tk.Label(master=self.w_fr_data, text=field, justify=tk.LEFT, anchor="w")

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
                    if value != "":
                        names = [item["Display Name"] for item in self.db.items_get(ids=value, fields=["Display Name"])]
                    else:
                        names = []
                    entry = ttk.Combobox(master=self.w_fr_data, values=names, state="readonly")
                    if value != "":
                        entry.current(0)
                    buttona = ttk.Button(master=self.w_fr_data, text="Edit", state="disabled")
                    source = info['source']
                    if source == "IDS":
                        buttona.bind("<Button-1>", lambda e: self.readlist(event=e, source="IDS"))
                    buttonb = None
                    hidden = value

                elif w_type == "sum":
                    entry = ttk.Entry(master=self.w_fr_data)
                    if self.last_doc.get('_id','') != "":
                        children = self.db.container_children_all(container=self.last_doc["_id"], cat=info['cat'], result="DOC")
                        target = info['target']
                        items = [float(child.get(target, "")) for child in children if child.get(target,"") != ""]
                        itemsum = str(sum(items)) if len(items) > 0 else ""
                        entry.insert(0, itemsum)
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
                    entry.grid(column=1, row=index, columnspan=3, sticky="nsew", padx=1, pady=1)

                self.w_var_data.append(var)
                self.w_la_data.append(label)
                self.w_input_data.append(entry)
                self.w_buttona_data.append(buttona)
                self.w_buttonb_data.append(buttonb)
                self.w_hidden_data.append(hidden)
            
            flags = [field for field in self.last_doc.keys() if field not in schema and field not in ["_id", "_rev", "category"]]
            
            for index, flag in enumerate(flags):
                if self.last_doc[flag] > 0:
                    self.w_li_flags.insert(index, flag)
            
            if len(flags) > 0:
                self.w_li_flags.selection_set(0)


    def __del__(self):
        '''Runs when DataEntry object is deleted.'''
        self.logger.debug("DataEntry object destroyed")


# ----------------------------------------------------------------------------

class SearchTree(SuperWidget):
    '''A SuperWidget representing a searchable tree.
    
    base: The id of the tree's root node.
    cats: The categories which may be searched using this SearchTree.
    db: The database object which the widget uses for database transactions.
    logger: The logger object used for logging.
    master: The widget that the SearchTree's component widgets will be instantiated under.
    ops: The operations that can be used in searches.
    search_result: The contents of the last search result.
    selection: The last selected element of the tree.
    _select: If present, a callback function that triggers when a tree item is selected.
    '''

    def __init__(self, master: tk.Misc, db: md.DEHCDatabase, base: dict, *, cats: list = [], level: str = "NOTSET", prepare: bool = True, select: Callable = None):
        '''Constructs a SearchTree object.
        
        master: The widget that the SearchTree's component widgets will be instantiated under.
        db: The database object which the widget uses for database transactions.
        base: The document of the item upon which the tree is initially based.
        cats: The categories of items that can be searched.
        level: Minimum level of logging messages to report; "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL", "NONE".
        prepare: If true, automatically prepares widgets for packing.
        select: If present, a callback function that triggers when a tree item is selected.
        '''
        super().__init__(master=master, db=db, level=level)

        self.cats = cats
        self.ops = ["=", "<", ">", "≤", "≥", "≠"]

        self._select = select

        self.base = base
        self.selection = None
        self.search_result = None

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

        self.w_fr_search.columnconfigure(0, weight=1000)
        self.w_fr_search.columnconfigure(1, weight=1000)
        self.w_fr_search.columnconfigure(2, weight=1000)
        self.w_fr_search.columnconfigure(3, weight=1000)
        self.w_fr_search.columnconfigure(4, weight=1000)
        self.w_fr_search.rowconfigure(0, weight=1000)

        # Variables
        self.w_var_cat = tk.StringVar()
        self.w_var_cat.trace("w", self.search_cat)
        self.w_var_field = tk.StringVar()
        self.w_var_op = tk.StringVar()
        self.w_var_value = tk.StringVar()

        # Widgets
        self.w_co_cat = ttk.Combobox(master=self.w_fr_search, values=self.cats, textvariable=self.w_var_cat, state="readonly")
        self.w_co_field = ttk.Combobox(master=self.w_fr_search, textvariable=self.w_var_field, state="readonly")
        self.w_co_op = ttk.Combobox(master=self.w_fr_search, value=self.ops, textvariable=self.w_var_op, state="readonly")
        self.w_en_value = ttk.Entry(master=self.w_fr_search, textvariable=self.w_var_value)
        self.w_bu_search = ttk.Button(master=self.w_fr_search, text="Search", command=self.search)
        self.w_li_search = tk.Listbox(master=self.w_fr, selectmode=tk.SINGLE, relief=tk.GROOVE, exportselection=False)
        self.w_tr_tree = ttk.Treeview(master=self.w_fr, show="tree", selectmode="browse")

        self.w_li_search.bind("<<ListboxSelect>>", self.search_select)
        self.w_tr_tree.bind("<<TreeviewSelect>>", self.tree_select)
        self.w_tr_tree.bind("<<TreeviewOpen>>", lambda *_: self.tree_open())
        self.w_tr_tree.bind("<Button-3>", self.tree_rebase)

        self.w_co_cat.current(0)
        self.w_co_field.current(0)
        self.w_co_op.current(0)
        self.w_tr_tree.column(column="#0")

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
        self.w_li_search.grid(column=0, row=1, sticky="nsew", padx=1, pady=1)
        self.w_sc_search.grid(column=1, row=1, sticky="nse", padx=1, pady=1)
        self.w_tr_tree.grid(column=2, row=1, sticky="nsew", padx=1, pady=1)
        self.w_sc_tree.grid(column=3, row=1, sticky="nse", padx=1, pady=1)


    def search(self, *args):
        '''Callback for when the search button is pressed.'''
        cat = self.w_var_cat.get()
        field = self.w_var_field.get()
        op = {"=":"$eq", "<":"$lt", ">":"$gt", "≤":"$lte", "≥":"$gte", "≠":"$ne"}[self.w_var_op.get()]
        value = self.w_var_value.get()
        selector = {field: {op: value}}
        name = self.db.schema_name(cat=cat)
        fields = ["_id", name]
        sort = [{key: 'asc'} for key in self.db.schema_keys(cat=cat)]
        self.search_result = self.db.items_query(cat=cat, selector=selector, fields=fields, sort=sort)
        self.w_li_search.delete(0, "end")
        for index, result in enumerate(self.search_result):
            self.w_li_search.insert(index, result[name])


    def search_cat(self, *args):
        '''Callback for when the search category is changed.'''
        self.w_co_field['values'] = self.db.schema_fields(cat=self.w_var_cat.get())
        self.w_co_field.current(0)


    def search_select(self, *args):
        '''Callback for when an item in the search is clicked.'''
        event, = args
        selected = event.widget.curselection()
        if len(selected) == 1:
            index, = selected
            id = self.search_result[index]["_id"]
            self.tree_focus(goal=id, rebase=True)


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


    def tree_insert(self, parent: str, iid: str, text: str):
        '''Inserts a node into the tree view.
        
        parent: The id of the parent node in the tree.
        iid: The id of the node being inserted.
        text: The text of the node.'''
        self.w_tr_tree.insert(parent=parent, index=1000000, iid=iid, text=text)
        if len(self.db.container_children(container=iid)) > 0:
            self.w_tr_tree.insert(parent=iid, index=1000000, iid=iid+"_stub")


    def tree_rebase(self, *args):
        '''Callback for when the tree is rebased using right-click.'''
        event, = args
        target = event.widget.identify_row(event.y)
        if self.w_tr_tree.parent(target) == "":
            parents = self.db.item_parents(item=target, result="DOC")
            if len(parents) > 0:
                self.base, *_ = parents
        else:
            self.base = self.db.item_get(id=target)
        self.tree_refresh()


    def tree_refresh(self):
        '''Refreshes the tree view.'''
        base_id = self.base["_id"]
        self.selection = self.w_tr_tree.selection()
        self.w_tr_tree.delete(*self.w_tr_tree.get_children(item=""))
        if self.db.item_exists(id=base_id):
            base_name = self.base[self.db.schema_name(id=base_id)]
            self.tree_insert(parent="", iid=base_id, text=base_name)
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
        self.selection = self.w_tr_tree.selection()
        if node != None:
            id = node
        elif self.w_tr_tree.focus() != "":
            id = self.w_tr_tree.focus()
        elif len(self.selection) == 1:
            id, = self.selection
        else:
            id = None
            raise RuntimeError("Unable to open tree nodes.")

        children = self.db.container_children(container=id, result="DOC")
        children.sort(key=lambda doc: (doc["category"], doc[self.db.schema_name(cat=doc["category"])]))
        self.w_tr_tree.delete(*self.w_tr_tree.get_children(item=id))
        for child in children:
            child_id = child["_id"]
            child_name = child[self.db.schema_name(id=child_id)]
            self.tree_insert(parent=id, iid=child_id, text=child_name)
        self.w_tr_tree.item(item=id, open=True)


    def __del__(self):
        '''Runs when SearchTree object is deleted.'''
        self.logger.debug("SearchTree object destroyed")


# ----------------------------------------------------------------------------

class ContainerManager(SuperWidget):
    '''A SuperWidget representing a container manager.
    
    cats: The categories which may be searched using this ContainerManager.
    db: The database object which the widget uses for database transactions.
    level: Minimum level of logging messages to report; "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL", "NONE".
    logger: The logger object used for logging.
    master: The widget that the ContainerManager's component widgets will be instantiated under.
    ops: The operations that can be used in seraches.
    select: If present, a callback function that triggers when a tree item is selected.
    '''

    def __init__(self, master: tk.Misc, db: md.DEHCDatabase, topbase: dict, botbase: dict,  *, cats: list = [], level: str = "NOTSET", prepare: bool = True, select: Callable = None):
        '''Constructs a ContainerManager object.
        
        master: The widget that the ContainerManager's component widgets will be instantiated under.
        db: The database object which  the widget uses for database transactions.
        topbase: The document of the item upon which the top tree is initially based.
        botbase: The document of the item upon which the bottom tree is initially based.
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

        if prepare == True:
            self.prepare()


    def prepare(self):
        '''Constructs the frames and widgets of the ContainerManager.'''
        # Widgets
        self.w_se_top = SearchTree(master=self.w_fr, db=self.db, base=self.topbase, cats=self.cats, level=self.level, prepare=True, select=self.select)
        self.w_se_bottom = SearchTree(master=self.w_fr, db=self.db, base=self.botbase, cats=self.cats, level=self.level, prepare=True)
        self.w_bu_move_item = ttk.Button(master=self.w_fr, text="Move Item", command=self.move)
        self.w_bu_move_subs = ttk.Button(master=self.w_fr, text="Move Sub-Items", command=self.submove)

        self.w_fr.columnconfigure(0, weight=1000)
        self.w_fr.columnconfigure(1, weight=1000)
        self.w_fr.rowconfigure(0, weight=1000)
        self.w_fr.rowconfigure(1, weight=1000)
        self.w_fr.rowconfigure(2, weight=1, minsize=25)


    def _pack_children(self):
        '''Packs & grids children frames and widgets of the ContainerManager.'''
        self.w_se_top.grid(column=0, row=0, columnspan=2, sticky="nsew", padx=2, pady=2)
        self.w_se_bottom.grid(column=0, row=1, columnspan=2, sticky="nsew", padx=2, pady=2)
        self.w_bu_move_item.grid(column=0, row=2, sticky="nsew", padx=2, pady=2)
        self.w_bu_move_subs.grid(column=1, row=2, sticky="nsew", padx=2, pady=2)


    def base(self, newbase: str = None):
        '''Sets or returns the base of the top tree.
        
        newbase: If specified, rebases the top tree to the new base.
        '''
        if newbase == None:
            return self.w_se_top.base
        else:
            self.w_se_top.base = newbase


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
        self.highlight(botitem=target)
        self.open()


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
        self.w_status = tk.Label(master=self.w_fr, text="Status Online", justify=tk.LEFT, anchor="w")
        
    
    def _pack_children(self):
        '''Packs & grids children frames and widgets of the StatusBar.'''
        self.w_status.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)


    def __del__(self):
        '''Runs when StatusBar object is deleted.'''
        self.logger.debug("StatusBar object destroyed")
