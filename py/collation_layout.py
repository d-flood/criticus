from tkinter import *
from tkinter import messagebox
from tkinter import ttk
import re
import io
import os
import ctypes
import platform
import json
import subprocess



class Collation:
    def __init__(self, collation_tab, main_dir, root, my_os):

        self.my_os = my_os
        self.main_dir = main_dir
        self.reg_font = ('Times', '12')
        self.cx_frame = LabelFrame(collation_tab,
            text='Collation Settings', font=self.reg_font)
        self.cx_frame.pack(fill=BOTH, expand=1)

        self.total_wits = 0

        Grid.rowconfigure(self.cx_frame, 0, weight=1)
        Grid.rowconfigure(self.cx_frame, 1, weight=1)
        Grid.rowconfigure(self.cx_frame, 2, weight=1)
        Grid.rowconfigure(self.cx_frame, 3, weight=1)
        Grid.rowconfigure(self.cx_frame, 4, weight=1)
        Grid.rowconfigure(self.cx_frame, 5, weight=1)

        #column 0
        Grid.columnconfigure(self.cx_frame, 0, weight=1)
        
        #   row 0

        self.add_wit_button = Button(self.cx_frame, text='Add Witness',
            font=self.reg_font, width=20, command=self.add_wit)
        self.add_wit_button.grid(row=0, column=0,
            padx=20, pady=10)

        #   row 1
        self.add_wit_entry = Entry(self.cx_frame, font=self.reg_font,
            width=22)
        self.add_wit_entry.grid(row=1, column=0,
            pady=10, padx=20)
        self.add_wit_entry.bind('<Return>', self.add_wit_on_enter)

        #   row 3
        self.total_wits_label = Label(self.cx_frame, font=self.reg_font, 
                width=20)
        self.total_wits_label.grid(row=3, column=0, pady=20, padx=20)

        #   row 4
        self.remove_wit_button = Button(self.cx_frame, text='Remove Selected',
                font=self.reg_font, width=20, command=self.get_wits_to_remove)
        self.remove_wit_button.grid(row=4, column=0,
            pady=20, padx=20)

        #   row 5
        self.launch_ce_button = Button(self.cx_frame,
            text='Launch Collation Editor', font=self.reg_font,
            command=self.launch_ce)
        self.launch_ce_button.grid(row=5, column=0, columnspan=3, sticky=EW,
            pady=20, padx=20)

        #column 1
        Grid.columnconfigure(self.cx_frame, 1, weight=1)
        #   row 0
        self.listbox_frame = Frame(self.cx_frame)
        self.listbox_frame.grid(row=0, rowspan=5, column=1, sticky=NS,
            padx=20)
        self.wit_listbox = Listbox(self.listbox_frame, width=30, selectmode=EXTENDED)
        self.wit_listbox.pack(side=LEFT, fill=BOTH)
        self.wit_scrollbar = Scrollbar(self.listbox_frame)
        self.wit_listbox.config(yscrollcommand=self.wit_scrollbar.set)
        self.wit_scrollbar.pack(side=RIGHT, fill=Y)
        self.wit_scrollbar.config(command=self.wit_listbox.yview)

        #column 2
        Grid.columnconfigure(self.cx_frame, 2, weight=1)
        self.basetext_label = Label(self.cx_frame, text='Current Basetext:',
            font=self.reg_font, width=20)
        self.basetext_label.grid(row=0, column=2,
                pady=20, padx=20)

        self.basetext_current = Label(self.cx_frame,
            text='------', font=self.reg_font, width=20)
        self.basetext_current.grid(row=1, column=2)


        self.change_basetext_button = Button(self.cx_frame,
            text='Change Basetext', font=self.reg_font, 
            width=20, command=self.change_basetext)
        self.change_basetext_button.grid(row=3, column=2,
            pady=20, padx=20)

        self.basetext_entry = Entry(self.cx_frame,
            font=self.reg_font, width=22)
        self.basetext_entry.grid(row=4, column=2,
            padx=20, pady=20)
        self.basetext_entry.bind('<Return>', self.change_basetext_on_enter)

        self.load_wit_listbox()
        
    
    def load_wit_listbox(self):
        with open(f'{self.main_dir}/py/settings.json', 'r') as settings_file:
            self.settings_file = json.load(settings_file)
            pass
        
        self.ce_path = self.settings_file['CE_path']
        self.config_path = f'{self.ce_path}/collation/data/project/default/config.json'
        try:
            with open(self.config_path, 'r') as config_file:
                config_file = json.load(config_file)
                pass
            self.wit_listbox.delete(0, END)
            for wit in config_file["witnesses"]:
                self.wit_listbox.insert(END, wit)
            self.total_wits = self.wit_listbox.size()
            self.total_wits_label.config(text=f'Total Witnesses: {self.total_wits}')
            self.basetext_current.config(text=config_file['base_text'])
        except:
            self.wit_listbox.insert(END, 'Failed to load; set CE path')

    def add_wit(self):

        if self.add_wit_entry.get() == "":
            messagebox.showinfo("Ruh-roh", "Witness entry cannot be blank")
        else:
            new_wit = self.add_wit_entry.get()
            try:
                with open(f'{self.ce_path}/collation/data/project/default/config.json', "r") as file:
                    config_file = json.load(file)
                    pass
                config_file['witnesses'].append(new_wit)
                with open(f'{self.ce_path}/collation/data/project/default/config.json', 'w') as new_config:
                    json.dump(config_file, new_config, indent=4)
                    pass
                with open(f'{self.ce_path}/collation/data/project/default/config.json', "r") as file:
                    config_file = json.load(file)
                    pass
                self.wit_listbox.delete(0, END)
                for wit in config_file["witnesses"]:
                    self.wit_listbox.insert(END, wit)
            except:
                messagebox.showinfo('Oops', 'Could not find the collation \
configuration file. \nMake sure that the Collation Editor directory is set\n\
by clicking "Settings"')


    def get_wits_to_remove(self):
        wits_to_remove = []
        wit_indices = self.wit_listbox.curselection()
        if wit_indices == ():
            pass
        else:
            for index in wit_indices:
                wits_to_remove.append(self.wit_listbox.get(index))
            if wits_to_remove == ['Failed to load; set CE path']:
                pass
            else:
                self.remove_wits(wits_to_remove)

    
    def remove_wits(self, wits_to_remove):
        
        with open(self.config_path, 'r') as settings_file:
            settings_file = json.load(settings_file)
            pass
        for wit in wits_to_remove:
            settings_file['witnesses'].remove(wit)
        with open(self.config_path, 'w') as file:
            json.dump(settings_file, file, indent=4)
            pass
        self.load_wit_listbox()


    def change_basetext(self):
        if self.wit_listbox.get(0) == 'Failed to load; set CE path':
            messagebox.showerror('Uh-oh', message='Failed to load;\
set CE path by clicking on the "Options" menu.')
        elif self.basetext_entry.get() == '':
            messagebox.showinfo('Forgetting something?', 
                message='Type in the basetext siglum under the\n\
"Change Basetext" button.')
        else:
            with open(self.config_path, 'r') as settings_file:
                settings_file = json.load(settings_file)
                pass
            settings_file['base_text'] = self.basetext_entry.get()
            with open(self.config_path, 'w') as file:
                json.dump(settings_file, file, indent=4)
            self.basetext_current.config(text=settings_file["base_text"])


    def launch_ce(self):
        if self.wit_listbox.get(0) == 'Failed to load; set CE path':
            messagebox.showerror('Uh-oh', message='Failed to load;\
set CE path by clicking on the "Options" menu.')
        os.chdir(self.ce_path)
        if self.my_os == "Windows":
            os.startfile("startup.bat")
            try:
                subprocess.call('start firefox "http://localhost:8080/collation"', shell=True)
            except:
                messagebox.showerror('Issue',
                    message='Could not open Firefox--it is installed?\n\
It is the recommended browser for the Collation Editor.\n\
If Firefox is installed, then you might be able to\n\
open the Collation Editor by manually going to\n\
    http://localhost:8080/collation')
        elif self.my_os != "Windows":
            os.startfile("startup.sh")
            try:
                subprocess.call('start firefox "http://localhost:8080/collation"', shell=True)
            except:
                messagebox.showerror('Issue',
                    message='Could not open Firefox--it is installed?\n\
It is the recommended browser for the Collation Editor.\n\
If Firefox is installed, then you might be able to\n\
open the Collation Editor by manually going to\n\
    http://localhost:8080/collation')
        os.chdir(self.main_dir)

    
    def add_wit_on_enter(self, event):
        self.add_wit()

    
    def change_basetext_on_enter(self, event):
        self.change_basetext()