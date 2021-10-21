'''The module containing the marshalling application.'''

import math

from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk

import mods.log as ml
import mods.database as md

# ----------------------------------------------------------------------------

class GC():
    '''A class which represents the Gatecheck application.'''

    def __init__(self, db: md.DEHCDatabase, vessel: str, *, level: str = "NOTSET", autorun: bool = False):
        '''Constructs a GC object.'''
        self.level = level
        self.logger = ml.get("GC", level=self.level)
        self.logger.debug("GC object instantiated")

        self.blank = Image.new("RGB", (256, 256), (240, 240, 240))
        self.db = db
        self.vessel = vessel
        self.vesselname = self.db.item_get(id=self.vessel)[self.db.schema_name(id=vessel)]

        self.root = tk.Tk()
        self.root.title(f"GC ({self.db.namespace} @ {self.db.db.data['url']})")
        self.root.state('zoomed')
        self.root.configure(background="#DCDAD5")

        if autorun == True:
            self.logger.info(f"Performing autorun")
            self.prepare()
            self.pack()
            self.run()


    def prepare(self):
        '''Constructs the frames and widgets of the GC.'''
        self.logger.debug(f"Preparing widgets")

        self.w_var_search = tk.StringVar()

        self.w_la_title = tk.Label(master=self.root, text=f"Boarding {self.vesselname}", font="Arial 48 bold")
        self.w_bu_photo = tk.Button(master=self.root, highlightthickness=0, bd=0)
        self.newphoto(img=self.blank)
        self.w_la_result = tk.Label(master=self.root, text="", font="Arial 48")
        self.w_en_search = tk.Entry(master=self.root, textvariable=self.w_var_search, font="Arial 16")
        self.w_bu_search = tk.Button(master=self.root, text="Search", command=self.search, font="Arial 16")

        self.root.columnconfigure(index=0, weight=1000)
        self.root.rowconfigure(index=0, weight=1000)
        self.root.rowconfigure(index=1, weight=1000)
        self.root.rowconfigure(index=2, weight=1000)
        self.root.rowconfigure(index=3, weight=1, minsize=48)
        self.root.rowconfigure(index=4, weight=1, minsize=48)


    def pack(self):
        '''Packs & grids children frames and widgets of the GC.'''
        self.logger.debug(f"Packing and gridding widgets")

        self.w_la_title.grid(column=0, row=0, sticky="nsew", padx=6, pady=(6,3))
        self.w_bu_photo.grid(column=0, row=1, sticky="nsew", padx=6, pady=3)
        self.w_la_result.grid(column=0, row=2, sticky="nsew", padx=6, pady=3)
        self.w_en_search.grid(column=0, row=3, sticky="nsew", padx=6, pady=3)
        self.w_bu_search.grid(column=0, row=4, sticky="nsew", padx=6, pady=(3,6))


    def run(self):
        '''Enters the root's main loop, drawing the app screen.'''
        self.logger.info(f"Starting main UI loop")
        self.root.mainloop()
        self.logger.info(f"Ending main UI loop")


    def accept(self):
        '''Changes app appearence to be green'''
        color = "#70FF70"
        self.root.configure(background=color)
        self.w_la_title.configure(background=color)
        self.w_bu_photo.configure(background=color)
        self.w_la_result.configure(background=color)
        self.w_bu_search.configure(background=color)
        self.w_la_result.configure(text="Accepted")


    def deny(self, reason: str):
        '''Changes app appearence to be red'''
        color = "#FF7070"
        self.root.configure(background=color)
        self.w_la_title.configure(background=color)
        self.w_bu_photo.configure(background=color)
        self.w_la_result.configure(background=color)
        self.w_bu_search.configure(background=color)
        self.w_la_result.configure(text=f"Denied ({reason})")


    def newphoto(self, img: Image):
        '''Changes the photo to be the one specified.'''
        target_width, target_height = (512, 512)
        width, height = img.size
        
        if width > height:
            ratio = target_width/width
        else:
            ratio = target_height/height

        img = img.resize((math.floor(width*ratio), math.floor(height*ratio)))
        img = ImageTk.PhotoImage(image=img)
        self.w_bu_photo.configure(image=img)
        self.w_bu_photo.image = img


    def search(self):
        '''Callback for when the search button is pressed.'''
        self.logger.debug(f"Search button activated")

        value = self.w_var_search.get()
        
        # Guard against empty searches
        if value == "":
            return

        person_doc = self.db.get_item_by_any_id(value)
        
        if person_doc == False:
            self.newphoto(img=self.blank)
            self.deny(reason="ID not found")
            self.logger.debug(f"Person rejected, ID not found")
        else:
            person = person_doc['_id']
            person_flags = person_doc.get("flags", [])
            person_photo = self.db.photo_load(item=person)

            if person_photo != None:
                self.newphoto(img=person_photo)
            else:
                self.newphoto(img=self.blank)

            self.logger.debug(f"Verifying person {person}")

            if "Ub-Unboarded" in person_flags:
                vessel_children = self.db.container_children_all(container=self.vessel, cat="Person")
                if person in vessel_children:
                    self.accept()
                    self.logger.debug(f"Person {person} is acceptable")
                    person_flags.remove("Ub-Unboarded")
                    self.db.item_edit(id=person, data={"flags": person_flags})
                else:
                    self.deny(reason="Not assigned to vessel")
                    self.logger.debug(f"Person rejected, not assigned to vessel")
            else:
                self.deny(reason="Not flagged as unboarded")
                self.logger.debug(f"Person rejected, not flagged as unboarded")
