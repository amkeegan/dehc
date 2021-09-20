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
    '''

    def __init__(self, master: tk.Misc, db: md.DEHCDatabase, *, cats: list = [], level: str = "NOTSET", prepare: bool = True):
        '''Constructs a DataEntry object.
        
        master: The widget that the DataEntry's component widgets will be instantiated under.
        cats: The categories of items that can be created using the New button.
        level: Minimum level of logging messages to report; "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL", "NONE".
        prepare: If true, automatically prepares widgets for packing.
        '''
        super().__init__(master=master, db=db, level=level)

        self.cats = cats
        self.last_doc = {}

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
        self.w_fr_flags.columnconfigure(index=2, weight=1, minsize=16)
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

        # Widgets
        self.w_la_title = ttk.Label(master=self.w_fr, text="Title")
        self.w_bu_photo = ttk.Button(master=self.w_fr, text="Photo", command=self.photo)
        self.w_la_flags = ttk.Label(master=self.w_fr_flags, text="Flags")
        self.w_li_flags = tk.Listbox(master=self.w_fr_flags, selectmode=tk.SINGLE, relief=tk.GROOVE)
        self.w_bu_add = ttk.Button(master=self.w_fr_flags, text="Remove", command=self.remove)
        self.w_bu_remove = ttk.Button(master=self.w_fr_flags, text="Add", command=self.add)
        self.w_la_data = []
        self.w_misc_data = []
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
        self.w_la_title.grid(column=0, row=0, columnspan=3, sticky="nsew", padx=2, pady=2)
        self.w_bu_photo.grid(column=0, row=1, sticky="nsew", padx=2, pady=2)
        self.w_fr_flags.grid(column=1, row=1, columnspan=2, sticky="nsew", padx=2, pady=2)
        self.w_fr_body.grid(column=0, row=2, columnspan=2, sticky="nsew", padx=2, pady=2)
        self.w_fr_data.grid(column=0, row=0, sticky="nsew")
        self.w_fr_foot.grid(column=0, row=3, columnspan=3, sticky="nsew", padx=2, pady=1)

        self.w_la_flags.grid(column=0, row=0, columnspan=3, sticky="nsew", padx=1, pady=1)
        self.w_li_flags.grid(column=0, row=1, columnspan=2, sticky="nsew", padx=1, pady=1)
        self.w_sc_flags.grid(column=2, row=1, sticky="nse", padx=1, pady=1)
        self.w_bu_add.grid(column=0, row=2, sticky="nsew", padx=1, pady=1)
        self.w_bu_remove.grid(column=1, row=2, sticky="nsew", padx=1, pady=1)

        self.w_bu_edit.grid(column=0, row=0, sticky="nsew", padx=1, pady=1)
        self.w_bu_cancel.grid(column=1, row=0, sticky="nsew", padx=1, pady=1)
        self.w_co_cat.grid(column=2, row=0, sticky="nsew", padx=1, pady=1)
        self.w_bu_new.grid(column=3, row=0, sticky="nsew", padx=1, pady=1)
        self.w_bu_save.grid(column=4, row=0, sticky="nsew", padx=1, pady=1)
        self.w_bu_delete.grid(column=5, row=0, sticky="nsew", padx=1, pady=1)


    def add(self, *args):
        '''Callback for when the flag add button is pressed'''
        self.logger.info("Pressed ADD FLAG")


    def cancel(self, *args):
        '''Callback for when the cancel button is pressed.'''
        self.show()


    def delete(self, *args):
        '''Callback for when the delete button is pressed'''
        self.logger.info("Pressed DELETE")


    def edit(self, *args):
        '''Callback for when the edit button is pressed'''
        for entry in self.w_misc_data:
            entry.config(state="normal")
        self.w_bu_edit.config(state="disabled")
        self.w_bu_cancel.config(state="normal")
        self.w_bu_save.config(state="normal")
        self.w_bu_delete.config(state="normal")


    def new(self, *args):
        '''Callback for when the new button is pressed.'''
        self.logger.info("Pressed NEW")
        self.last_doc = {"category": self.w_var_cat.get()}
        self.show()
        self.edit()


    def photo(self, *args):
        '''Callback for when the photo is pressed'''
        self.logger.info("Pressed PHOTO")

    def remove(self, *args):
        '''Callback for when the flag remove button is pressed'''
        self.logger.info("Pressed REMOVE FLAG")

    def save(self, *args):
        '''Callback for when the save button is pressed.'''
        self.logger.info("Pressed SAVE")


    def show(self, doc: dict = None):
        '''Displays a new document.
        
        doc: The document to display. If omitted, the previous document will be used.
        '''
        if doc != None:
            self.last_doc = doc

        for child in self.w_fr_data.winfo_children():
            child.destroy()

        self.w_var_data = []
        self.w_la_data = []
        self.w_misc_data = []

        self.w_bu_edit.config(state="disabled")
        self.w_bu_cancel.config(state="disabled")
        self.w_bu_save.config(state="disabled")
        self.w_bu_delete.config(state="disabled")

        if len(self.last_doc) > 0:
            self.w_bu_edit.config(state="normal")
            schema = self.db.schema_schema(cat=self.last_doc["category"])
            self.w_la_title.config(text=self.last_doc.get(self.db.schema_name(cat=self.last_doc["category"]), ""))
            self.w_fr_data.columnconfigure(index=0, weight=1000)
            self.w_fr_data.columnconfigure(index=1, weight=1000)

            for index, (field, info) in enumerate(schema.items()):
                value = self.last_doc.get(field, "")
                var = tk.StringVar()
                var.set(value)
                label = tk.Label(master=self.w_fr_data, text=field, justify=tk.LEFT, anchor="w")

                w_type = info['type']
                if w_type == "text":
                    entry = ttk.Entry(master=self.w_fr_data, textvariable=var, state="disabled")
                elif w_type == "option":
                    entry = ttk.Combobox(master=self.w_fr_data, textvariable=var, values=info['options'], state="disabled")
                else:
                    entry = ttk.Label(master=self.w_fr_data)

                #self.w_fr_data.rowconfigure(index=index, weight=1000, minsize=17)
                label.grid(column=0, row=index, sticky="new", padx=1, pady=1)
                entry.grid(column=1, row=index, sticky="new", padx=1, pady=1)
                self.w_var_data.append(var)
                self.w_la_data.append(label)
                self.w_misc_data.append(entry)


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
    select: If present, a callback function that triggers when a tree item is selected.
    selection: The last selected element of the tree.
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

        self.select = select

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
        self.w_fr.columnconfigure(1, weight=1000)
        self.w_fr.columnconfigure(2, weight=1, minsize=16)
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
        self.w_li_search = tk.Listbox(master=self.w_fr, selectmode=tk.SINGLE, exportselection=False, relief=tk.GROOVE)
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

        # Misc
        self.tree_refresh()


    def _pack_children(self):
        '''Packs & grids children frames and widgets of the SearchTree.'''
        # Frames & Canvas
        self.w_fr_search.grid(column=0, row=0, columnspan=3, sticky="nsew")

        # Widgets
        self.w_co_cat.grid(column=0, row=0, sticky="nsew", padx=1, pady=1)
        self.w_co_field.grid(column=1, row=0, sticky="nsew", padx=1, pady=1)
        self.w_co_op.grid(column=2, row=0, sticky="nsew", padx=1, pady=1)
        self.w_en_value.grid(column=3, row=0, sticky="nsew", padx=1, pady=1)
        self.w_bu_search.grid(column=4, row=0, sticky="nsew", padx=1, pady=1)
        self.w_li_search.grid(column=0, row=1, sticky="nsew", padx=1, pady=1)
        self.w_tr_tree.grid(column=1, row=1, sticky="nsew", padx=1, pady=1)
        self.w_sc_tree.grid(column=2, row=1, sticky="nse", padx=1, pady=1)


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
            elif rebase == True:
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
        base_name = self.base[self.db.schema_name(id=base_id)]
        self.selection = self.w_tr_tree.selection()
        self.w_tr_tree.delete(*self.w_tr_tree.get_children(item=""))
        self.tree_insert(parent="", iid=base_id, text=base_name)
        if len(self.selection) == 1:
            selection, = self.selection
            self.tree_focus(goal=selection)


    def tree_select(self, *args):
        '''Callback for when an item in the tree is selected.'''
        if self.select != None:
            event, = args
            selected = event.widget.selection()
            if len(selected) == 1:
                id, = selected
                doc = self.db.item_get(id=id)
                self.select(doc)


    def tree_open(self, node: str = None):
        '''Open a node on the tree view.
        
        node: The node to open. If omitted, opens currently selected node.
        '''
        id = node if node != None else self.w_tr_tree.focus()
        children = self.db.container_children(container=id, result="DOC")
        children.sort(key=lambda doc: (doc["category"], doc[self.db.schema_name(cat=doc["category"])]))
        self.w_tr_tree.delete(*self.w_tr_tree.get_children(item=id))
        for child in children:
            child_id = child["_id"]
            child_name = child[self.db.schema_name(id=child_id)]
            self.tree_insert(parent=id, iid=child_id, text=child_name)


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
        self.w_bu_move = ttk.Button(master=self.w_fr, text="Move", command=self.move)

        self.w_fr.columnconfigure(0, weight=1000)
        self.w_fr.rowconfigure(0, weight=1000)
        self.w_fr.rowconfigure(1, weight=1000)
        self.w_fr.rowconfigure(2, weight=1, minsize=25)


    def _pack_children(self):
        '''Packs & grids children frames and widgets of the ContainerManager.'''
        self.w_se_top.grid(column=0, row=0, sticky="nsew", padx=2, pady=2)
        self.w_se_bottom.grid(column=0, row=1, sticky="nsew", padx=2, pady=2)
        self.w_bu_move.grid(column=0, row=2, sticky="nsew", padx=2, pady=2)


    def move(self, *args):
        '''Callback for when the move button is pressed.'''
        self.logger.info("Pressed MOVE")


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
