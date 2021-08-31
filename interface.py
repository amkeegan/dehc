import tkinter as tk
from tkinter import ttk
from db import Database
from globals import G_FIELDS_EVACUEE

# ----------------------------------------------------------------------------

KEY, KEY2, *_ = G_FIELDS_EVACUEE

# ----------------------------------------------------------------------------

class GUI(tk.Tk):
    def __init__(self, db: Database):
        '''Constructs a GUI object.'''
        super().__init__()
        self.db = db
        self.search_results = []
        self.search_selected = -1
        self.prepare_gui()
    
    def prepare_gui(self):
        '''Prepares the GUI and its widgets.'''
        self.title("DEHC Protoype")
        self.prepare_frames()
        self.prepare_left()
        self.prepare_right()
    
    def prepare_frames(self):
        '''Prepares and places frames.'''
        self.f_left = tk.Frame(master=self)
        self.f_right = tk.Frame(master=self)
        self.f_lbase = tk.Frame(master=self)
        self.f_rbase = tk.Frame(master=self)
        self.f_search = tk.Frame(master=self.f_left)
        self.f_list = tk.Frame(master=self.f_left)
        self.f_data = tk.Frame(master=self.f_right)

        self.f_left.grid(row=0, column=0, sticky="nsew")
        self.f_right.grid(row=0, column=1, sticky="nsew")
        self.f_lbase.grid(row=1, column=0, sticky="nsew")
        self.f_rbase.grid(row=1, column=1, sticky="nsew")
        self.f_search.grid(row=0, column=0, sticky="nsew")
        self.f_list.grid(row=1, column=0, sticky="nsew")
        self.f_data.grid(row=0, column=0, sticky="nsew")

    def prepare_left(self):
        '''Prepares and places left side widgets.'''
        self.v_sfield = tk.StringVar()
        self.v_svalue = tk.StringVar()

        self.c_search = ttk.Combobox(master=self.f_search, width=25, 
        values=G_FIELDS_EVACUEE, textvariable=self.v_sfield)
        self.c_search.set(KEY)
        self.e_search = ttk.Entry(master=self.f_search, width=25, 
        textvariable=self.v_svalue)
        self.b_search  = ttk.Button(master=self.f_search, width=10, 
        text="Search", command=self.run_search)

        self.l_list = tk.Listbox(master=self.f_list, width=60, height=42)
        self.l_list.bind("<<ListboxSelect>>", self.select_evacuee)
        
        self.b_add = ttk.Button(master=self.f_lbase, width=9, text="New", 
        command=self.new_evacuee)
        self.b_remove = ttk.Button(master=self.f_lbase, width=9, 
        text="Delete", command=self.delete_evacuee)

        self.c_search.grid(row=0, column=0, sticky="nsew")
        self.e_search.grid(row=0, column=1, sticky="nsew")
        self.b_search.grid(row=0, column=2, sticky="nsew")
        self.l_list.pack(fill=tk.BOTH, expand=True)
        self.b_add.grid(row=0, column=0, sticky="nsew")
        self.b_remove.grid(row=0, column=1, sticky="nsew")
    
    def prepare_right(self):
        '''Prepares and places right side widgets.'''
        self.v_data = []
        self.t_data = []
        self.e_data = []
        for index, field in enumerate(G_FIELDS_EVACUEE):
            v_data = tk.StringVar()
            t_data = ttk.Label(master=self.f_right, width=30, 
            justify=tk.LEFT, anchor="w", text=field)
            e_data = ttk.Entry(master=self.f_right, width=30, 
            textvariable=v_data)
            t_data.grid(row=index, column=0, sticky="w")
            e_data.grid(row=index, column=1, sticky="ew")
            self.v_data.append(v_data)
            self.t_data.append(t_data)
            self.e_data.append(e_data)
        
        self.b_save = ttk.Button(master=self.f_rbase, width=9, text="Save", 
        command=self.save_data)
        self.b_save.pack(anchor="e")

    def run_search(self):
        '''Queries the database and displays the results.'''
        self.search_results = self.db.db_query(self.v_sfield.get(), 
        self.v_svalue.get(), KEY)
        self.populate_search()
    
    def populate_search(self):
        '''Populates the search list on the left side.'''
        self.l_list.delete(0, "end")
        if len(self.search_results) > 0:
            for index, row in enumerate(self.search_results):
                self.l_list.insert(index, f"{row[KEY].upper()}, {row[KEY2]}")

    def select_evacuee(self, event):
        '''A callback which triggers when an evacuee is selected.'''
        selection = event.widget.curselection()
        if len(selection) == 1:
            self.search_selected = selection[0]
            self.populate_data()

    def populate_data(self):
        '''Populates the input boxes on the right side with data.'''
        for index, field in enumerate(G_FIELDS_EVACUEE):
            data = self.search_results[self.search_selected]
            self.e_data[index].delete(0, "end")
            self.e_data[index].insert(0, data.get(field, ""))

    def clear_data(self):
        '''Clears the data from the input boxes on the right side.'''
        for entry in self.e_data:
            entry.delete(0, "end")

    def save_data(self):
        '''Saves data to database for currently selected evacuee.'''
        if self.search_selected >= 0:
            old_data = self.search_results[self.search_selected]
            new_data = {}
            for index, field in enumerate(G_FIELDS_EVACUEE):
                data = self.e_data[index].get()
                if old_data.get(field,"") != data:
                    old_data[field] = data
                    new_data[field] = data
            self.db.doc_edit(new_data, old_data["_id"])
            self.populate_search()

    def new_evacuee(self):
        '''Adds a new evacuee.'''
        data = {field: "" for field in G_FIELDS_EVACUEE}
        id = self.db.doc_get_id("per-")
        data["_id"] = id
        data[KEY] = "New"
        self.search_results = [data]
        self.search_selected = 0
        self.populate_search()
        self.populate_data()

    def delete_evacuee(self):
        '''Deletes the currently selected evacuee from the database.'''
        if self.search_selected >= 0:
            deleted = self.search_results.pop(self.search_selected)
            self.db.doc_delete(deleted["_id"])
            self.populate_search()
            self.clear_data()

    def run(self):
        '''Runs the GUI's main loop.'''
        self.mainloop()
