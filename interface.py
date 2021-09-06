import json
import os
import tkinter as tk
from tkinter import ttk

from db import DEHC_Database

# ----------------------------------------------------------------------------

COMPARISONS = ["=", "<", ">", "≤", "≥", "≠"]

with open(os.path.join(os.path.split(__file__)[0], "fields.json"), "r") as f:
    CAT_JSON = json.loads(f.read())

def GET_CATEGORY(id: str) -> str:
    return id.split("-")[0]

def GET_KEYS(category: str) -> list:
    return CAT_JSON[category]["keys"]

def GET_FIELDS(category: str) -> list:
    return CAT_JSON[category]["fields"]

def GET_LISTNAME(doc: dict) -> str:
    category = GET_CATEGORY(doc["_id"])
    keys = GET_KEYS(category)
    return f", ".join([doc[key] for key in keys])+f" [{category}]"

def GET_SELECTOR(field: str, comparison: str, value: str):
    return {
    "=":{field:{'$eq':value}},
    "<":{field:{'$lt':value}},
    ">":{field:{'$gt':value}},
    "≤":{field:{'$lte':value}},
    "≥":{field:{'$gte':value}},
    "≠":{field:{'$ne':value}}
    }[comparison]

# ----------------------------------------------------------------------------

class IngestApp:
    def __init__(self, db: DEHC_Database):
        '''Object for handling the UI and its functionality.'''
        self.root = tk.Tk()
        self.root.title("DEHC Prototype")
        self.root.resizable(width=False, height=False)
        self.root.geometry("1260x506")
        self.root.bind("<Return>", self._enter)
        self.root.bind("<Escape>", lambda event: self.root.destroy())

        self.categories = list(CAT_JSON.keys())
        self.db = db               # CouchDB database
        self.co_search = None      # Last container search query (dict)
        self.it_search = None      # Last item search query (dict)
        self.co_lookup = {}        # Treeview.index --> _id
        self.it_lookup = {}        # Listbox.index <--> _id
        self.co_selected = None    # Currently selected container (int)
        self.it_selected = None    # Currently selected item (int)
        self.pending_openings = [] # List of ids to open on the Treeview
        self.da_doc = {}           # Doc displayed in data section
        self.search = 0            # 1 = Container; 2 = Item
        self.prepare_widgets()
    
    def prepare_widgets(self):
        '''Prepares and packs all of the UI widgets.'''

        # FRAMES
        self.fr_app = tk.Frame(master=self.root)
        self.fr_co_search = tk.Frame(master=self.fr_app)
        self.fr_co_results = tk.Frame(master=self.fr_app)
        self.fr_co_footer = tk.Frame(master=self.fr_app)
        self.fr_it_search = tk.Frame(master=self.fr_app)
        self.fr_it_results = tk.Frame(master=self.fr_app)
        self.fr_it_footer = tk.Frame(master=self.fr_app)
        self.fr_da_header = tk.Frame(master=self.fr_app)
        self.fr_da_body = tk.Frame(master=self.fr_app)
        self.fr_da_footer =  tk.Frame(master=self.fr_app)

        # CONTAINER SEARCH BAR
        self.var_co_category = tk.StringVar()
        self.var_co_category.trace("w", self._co_category_select)
        self.var_co_field = tk.StringVar()
        self.var_co_comparison = tk.StringVar()
        self.var_co_value = tk.StringVar()
        self.cb_co_category = ttk.Combobox(master=self.fr_co_search, values=self.categories, textvariable=self.var_co_category, state="readonly", width=15)
        self.cb_co_field = ttk.Combobox(master=self.fr_co_search, textvariable=self.var_co_field, state="readonly", width=15)
        self.cb_co_comparison = ttk.Combobox(master=self.fr_co_search, values=COMPARISONS, textvariable=self.var_co_comparison, state="readonly", width=6)
        self.en_co_value = ttk.Entry(master=self.fr_co_search, textvariable=self.var_co_value, width=15)
        self.en_co_value.bind("<FocusIn>", lambda event: setattr(self, 'search', 1))
        self.bu_co_search = ttk.Button(master=self.fr_co_search, text="Search", command=self._co_search, width=6)
        self.cb_co_category.current(0)
        self.cb_co_comparison.current(0)

        # CONTAINER RESULTS
        self.tv_co_tree = ttk.Treeview(master=self.fr_co_results, show="tree", selectmode="browse")
        self.tv_co_tree.bind("<<TreeviewSelect>>", self._co_element_select)
        self.tv_co_tree.bind("<<TreeviewOpen>>", self._co_element_open)

        # CONTAINER FOOTER
        self.bu_co_remove = ttk.Button(master=self.fr_co_footer, text="Remove", command=self._co_remove, width=8)
        self.bu_co_move = ttk.Button(master=self.fr_co_footer, text="Move", command=self._co_move, width=8)

        # ITEM SEARCH BAR
        self.var_it_category = tk.StringVar()
        self.var_it_category.trace("w", self._it_category_select)
        self.var_it_field = tk.StringVar()
        self.var_it_comparison = tk.StringVar()
        self.var_it_value = tk.StringVar()
        self.cb_it_category = ttk.Combobox(master=self.fr_it_search, values=self.categories, textvariable=self.var_it_category, state="readonly", width=15)
        self.cb_it_field = ttk.Combobox(master=self.fr_it_search, textvariable=self.var_it_field, state="readonly", width=15)
        self.cb_it_comparison = ttk.Combobox(master=self.fr_it_search, values=COMPARISONS, textvariable=self.var_it_comparison, state="readonly", width=6)
        self.en_it_value = ttk.Entry(master=self.fr_it_search, textvariable=self.var_it_value, width=15)
        self.en_it_value.bind("<FocusIn>", lambda event: setattr(self, 'search', 2))
        self.bu_it_search = ttk.Button(master=self.fr_it_search, text="Search", command=self._it_search, width=6)
        self.cb_it_category.current(0)
        self.cb_it_comparison.current(0)

        # ITEM RESULTS
        self.lb_it_results = tk.Listbox(master=self.fr_it_results, selectmode=tk.SINGLE, exportselection=False, height=28)
        self.lb_it_results.bind("<<ListboxSelect>>", self._it_element_select)

        # DATA HEADER
        self.la_da_heading = ttk.Label(master=self.fr_da_header, width=45, font="bold")

        # DATA FOOTER
        self.var_da_category = tk.StringVar()
        self.cb_da_category = ttk.Combobox(master=self.fr_da_footer, values=self.categories, textvariable=self.var_da_category, state="readonly", width=15)
        self.bu_da_new = ttk.Button(master=self.fr_da_footer, text="New", command=self._item_new, width=6)
        self.bu_da_save = ttk.Button(master=self.fr_da_footer, text="Save", command=self._item_save, width=6)
        self.bu_da_delete = ttk.Button(master=self.fr_da_footer, text="Delete", command=self._item_delete, width=6)
        self.cb_da_category.current(0)

        # PACKING FRAMES
        self.fr_app.pack(fill=tk.BOTH, expand=True)
        self.fr_co_search.grid(column=0, row=0, sticky="nsew")
        self.fr_co_results.grid(column=0, row=1, sticky="nsew")
        self.fr_co_footer.grid(column=0, row=2, sticky="nsew")
        self.fr_it_search.grid(column=1, row=0, sticky="nsew")
        self.fr_it_results.grid(column=1, row=1, sticky="nsew")
        self.fr_it_footer.grid(column=1, row=2, sticky="nsew")
        self.fr_da_header.grid(column=2, row=0, sticky="nsew")
        self.fr_da_body.grid(column=2, row=1, sticky="nsew")
        self.fr_da_footer.grid(column=2, row=2, sticky="nsew")

        # PACKING CONTAINER SECTION
        self.cb_co_category.grid(column=0, row=0, sticky="nsew")
        self.cb_co_field.grid(column=1, row=0, sticky="nsew")
        self.cb_co_comparison.grid(column=2, row=0, sticky="nsew")
        self.en_co_value.grid(column=3, row=0, sticky="nsew")
        self.bu_co_search.grid(column=4, row=0, sticky="nsew")
        self.tv_co_tree.pack(fill=tk.BOTH, expand=True)
        self.bu_co_remove.grid(column=0, row=0, sticky="nsew")
        self.bu_co_move.grid(column=1, row=0, sticky="nsew")

        # PACKING ITEM SECTION
        self.cb_it_category.grid(column=0, row=0, sticky="nsew")
        self.cb_it_field.grid(column=1, row=0, sticky="nsew")
        self.cb_it_comparison.grid(column=2, row=0, sticky="nsew")
        self.en_it_value.grid(column=3, row=0, sticky="nsew")
        self.bu_it_search.grid(column=4, row=0, sticky="nsew")
        self.lb_it_results.pack(fill=tk.BOTH, expand=True)

        # PACKING DATA SECTION
        self.la_da_heading.pack(fill=tk.BOTH, expand=True)
        self.cb_da_category.grid(column=0, row=0, sticky="nsew")
        self.bu_da_new.grid(column=1, row=0, sticky="nsew")
        self.bu_da_save.grid(column=2, row=0, sticky="nsew")
        self.bu_da_delete.grid(column=3, row=0, sticky="nsew")


    def research_containers(self):
        '''Performs a container search using the last query's settings.'''
        if self.co_search != None:
            data = self.db.db_search(**self.co_search)
            print(len(data))
            self.refresh_containers(data)


    def refresh_containers(self, data: dict):
        '''Redraws the container tree using provided data.'''
        self.pending_openings = self.ids_from_node(node=self.tv_co_tree.focus())
        self.tv_co_tree.delete(*self.tv_co_tree.get_children())
        self.co_selected = None
        self.co_lookup = {}
        if len(data) > 0:
            for row in data:
                element = GET_LISTNAME(row)
                node = self.tv_co_tree.insert(parent="", index=1000000, text=element)
                self.co_lookup[node] = row["_id"]
                if len(row["contains"]) > 0:
                    self.tv_co_tree.insert(parent=node, index=1000000, text="")
                # -vvv- Reselect the node that was selected before the refresh -vvv-
                    if self.pending_openings != [] and self.pending_openings[-1] == row["_id"]:
                        self.pending_openings.pop()
                        self.open_container(node=node)
                elif self.pending_openings != [] and self.pending_openings[-1] == row["_id"]:
                    self.tv_co_tree.item(item=node, open=True)
                    self.tv_co_tree.focus(item=node)
                    self.tv_co_tree.see(item=node)
                    self.tv_co_tree.selection_set(node)
                    self.co_selected = node


    def open_container(self, *, node: str):
        '''Gets and displays the children of a container in the container tree.'''
        self.tv_co_tree.item(item=node, open=True)
        self.tv_co_tree.focus(item=node)
        self.tv_co_tree.see(item=node)
        if node not in self.tv_co_tree.selection():
            self.tv_co_tree.selection_set(node)
            self.co_selected = node

        existing_children = self.tv_co_tree.get_children(item=node)
        if len(existing_children) > 0:
            self.tv_co_tree.delete(*existing_children)
            id = self.co_lookup[node]
            doc = self.doc_from_id(id=id, keyonly=True)
            children = doc['contains']
            for child_id in children:
                child_doc = self.doc_from_id(id=child_id, keyonly=True)
                child_node = self.tv_co_tree.insert(parent=node, index=1000000, text=GET_LISTNAME(child_doc))
                self.co_lookup[child_node] = child_id
                if len(child_doc['contains']) > 0:
                    self.tv_co_tree.insert(parent=child_node, index=1000000, text="")
                    # -vvv- Reselect the node that was selected before the refresh -vvv-
                    if self.pending_openings != [] and self.pending_openings[-1] == child_id:
                        self.pending_openings.pop()
                        self.open_container(node=child_node)


    def research_items(self):
        '''Performs an item search using the last query's settings.'''
        if self.it_search != None:
            data = self.db.db_search(**self.it_search)
            print(len(data))
            self.refresh_items(data)


    def refresh_items(self, data: dict):
        '''Redraws the item list using provided data.'''
        self.lb_it_results.delete(0, "end")

        last_selected = self.it_lookup.get(self.it_selected, None)
        self.it_lookup = {}
        self.it_selected = None

        if len(data) > 0:
            for index, row in enumerate(data):
                element = GET_LISTNAME(row)
                self.lb_it_results.insert(index, element)
                self.it_lookup[index] = row["_id"]
                self.it_lookup[row["_id"]] = index
            if last_selected != None:
                index = self.it_lookup.get(last_selected, None)
                if index != None:
                    self.lb_it_results.selection_set(index, index)
                    self.lb_it_results.see(index)
                    self.it_selected = index


    def refresh_data(self):
        '''Refreshes and repopulates the data page.'''
        for child in self.fr_da_body.winfo_children():
            child.destroy()
        self.var_da_value = []
        self.la_da_field = []
        self.en_da_value = []
        self.la_da_heading.config(text=self.da_doc.get('_id',''))

        category = self.da_doc.get('category',"")
        if category != "":
            fields = GET_FIELDS(category)
            for index, field in enumerate(fields):
                var_da_value = tk.StringVar()
                la_da_field = tk.Label(master=self.fr_da_body, text=field, width=30, justify=tk.LEFT, anchor="w")
                en_da_value = tk.Entry(master=self.fr_da_body, textvariable=var_da_value, width=30)
                la_da_field.grid(column=0, row=index, sticky="nsew")
                en_da_value.grid(column=1, row=index, sticky="nsew")
                self.var_da_value.append(var_da_value)
                self.la_da_field.append(la_da_field)
                self.en_da_value.append(en_da_value)
            for index, field in enumerate(fields):
                self.en_da_value[index].delete(0, "end")
                self.en_da_value[index].insert(0, self.da_doc.get(field,""))


    def ids_from_node(self, *, node: str) -> list:
        '''Takes a tv_co_tree node and returns chain of IDs leading to its position.'''
        if node == "":
            return []
        else:
            ids = [self.co_lookup[node]]
            parent = self.tv_co_tree.parent(item=node)
            ids += self.ids_from_node(node=parent)
            return ids


    def doc_from_id(self, *, id: str, keyonly: bool = False):
        '''Takes a doc id and returns its key fields.'''
        if keyonly == True:
            category = GET_CATEGORY(id)
            fields = GET_KEYS(category)+["_id", "contains"]
        else:
            fields = None
        return self.db.item_get(id=id, fields=fields)


    def run(self):
        self.root.mainloop()


    # ---------
    # CALLBACKS
    # ---------

    def _enter(self, *args):
        '''Callback for when enter is pressed on the keyboard.'''
        if self.search == 1:
            self._co_search()
        elif self.search == 2:
            self._it_search()


    def _co_category_select(self, *args):
        '''Callback for when the container category is changed.'''
        self.cb_co_field['values'] = GET_FIELDS(self.var_co_category.get())
        self.cb_co_field.current(0)


    def _it_category_select(self, *args):
        '''Callback for when the item category is changed.'''
        self.cb_it_field['values'] = GET_FIELDS(self.var_it_category.get())
        self.cb_it_field.current(0)


    def _co_search(self, *args):
        '''Callback for when the container search button is pressed.'''
        category = self.var_co_category.get()
        field = self.var_co_field.get()
        comparison = self.var_co_comparison.get()
        value = self.var_co_value.get()
        selector = GET_SELECTOR(field, comparison, value)
        keys = GET_KEYS(category)
        fields = keys+["_id", "contains"]
        self.co_search = {"category":category, "selector":selector, "fields":fields, "sort":keys}
        self.research_containers()


    def _it_search(self, *args):
        '''Callback for when the item search button is pressed.'''
        category = self.var_it_category.get()
        field = self.var_it_field.get()
        comparison = self.var_it_comparison.get()
        value = self.var_it_value.get()
        selector = GET_SELECTOR(field, comparison, value)
        keys = GET_KEYS(category)
        fields = keys+["_id"]
        self.it_search = {"category":category, "selector":selector, "fields":fields, "sort":keys}
        self.research_items()


    def _co_element_select(self, *args):
        '''Callback for when something is selected in the container list.'''
        event, = args
        selected_items = event.widget.selection()
        if len(selected_items) == 1:
            self.co_selected, = selected_items
            selected_doc = self.co_lookup[self.co_selected]
            self.da_doc = self.doc_from_id(id=selected_doc)
            self.refresh_data()


    def _co_element_open(self, *args):
        '''Callback for when expanding an item in the container list.'''
        event, = args
        self.open_container(node=event.widget.focus())


    def _it_element_select(self, *args):
        '''Callback for when something is selected in the item list.'''
        event, = args
        selected_items = event.widget.curselection()
        if len(selected_items) == 1:
            self.it_selected, = selected_items
            selected_doc = self.it_lookup[self.it_selected]
            self.da_doc = self.doc_from_id(id=selected_doc)
            self.refresh_data()


    def _co_remove(self, *args):
        '''Callback for when the remove button is pressed.'''
        if self.co_selected != None:
            item_id = self.co_lookup[self.co_selected]
            old_containers_id = self.db.container_find(item=item_id)
            for container_id in old_containers_id:
                self.db.container_remove(container=container_id, item=item_id)
            self.research_containers()


    def _co_move(self, *args):
        '''Callback for when the move button is pressed.'''
        if self.co_selected != None and self.it_selected != None:
            item_id = self.it_lookup[self.it_selected]
            new_container_id = self.co_lookup[self.co_selected]

            old_containers_id = self.db.container_find(item=item_id)
            for container_id in old_containers_id:
                self.db.container_remove(container=container_id, item=item_id)
            
            self.db.container_add(container=new_container_id, item=item_id)
            self.research_containers()


    def _item_new(self, *args):
        '''Callback for when the user creates a new item.'''
        self.da_doc = {'category': self.var_da_category.get()}
        self.refresh_data()


    def _item_save(self, *args):
        '''Callback for when the user saves an item.'''
        id = self.da_doc.get("_id", "")
        new_data = {}
        fields = map(lambda field: field['text'], self.la_da_field)
        values = map(lambda value: value.get(), self.var_da_value)
        for field, value in zip(fields, values):
            if self.da_doc.get(field, "") != value:
                self.da_doc[field] = value
                new_data[field] = value

        if id == "":
            id = self.db.item_add(category=self.var_da_category.get(), data=new_data)
            self.la_da_heading['text'] = id
        else:
            self.db.item_edit(id=id, data=new_data)
        self.research_containers()
        self.research_items()


    def _item_delete(self, *args):
        '''Callback for when the user deletes an item.'''
        id = self.da_doc["_id"]
        self.db.item_delete(id=id)
        containers = self.db.container_find(item=id)
        for container in containers:
            self.db.container_remove(container=container, item=id)
        self.da_doc = {}
        self.research_containers()
        self.research_items()
        self.refresh_data()

# ----------------------------------------------------------------------------