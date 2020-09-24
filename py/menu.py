from tkinter import *
from tkinter import messagebox, filedialog as fd
import re
import io
import json


class Options:

    def __init__(self, root, main_dir):

        self.root = root
        self.menubar = Menu(root)
        self.main_dir = main_dir

        self.options = Menu(self.menubar, tearoff=0)
        self.options.add_command(label='Set Online Transcription Editor Directory', command=self.set_ote)
        self.options.add_command(label='Set Collation Editor Directory', command=self.set_ce)
        self.options.add_command(label='Set Witnesses Directory', command=self.set_wits)
        self.options.add_separator()
        self.options.add_command(label='Change Scaling (if blurry on Windows)', command=self.change_dpi)
        self.options.add_separator()
        self.options.add_command(label='Change the tab to open on startup', command=self.change_default_tab)
        self.menubar.add_cascade(label='Settings', menu=self.options)
        
        self.v = IntVar()
        self.tv = StringVar(value='transcription')

        root.config(menu=self.menubar)
    
    def set_ote(self):
        self.update_settings_file('OTE_path')

    def set_ce(self):
        self.update_settings_file('CE_path')

    def set_wits(self):
        self.update_settings_file('mss_path')

    def change_dpi(self):
        self.dpi_window = Toplevel()
        self.dpi_window.title('Set Scaling')
        self.dpi_window.geometry('350x160')
        self.dpi_window.iconbitmap(f'{self.main_dir}/py/icon.ico')
        temp_frame = Frame(self.dpi_window)
        temp_frame.pack()

        self.rb_one = Radiobutton(temp_frame, text='0', variable=self.v, value=1)
        self.rb_one.pack(side=TOP)

        self.rb_two = Radiobutton(temp_frame, text='1', variable=self.v, value=2)
        self.rb_two.pack(side=TOP)

        self.rb_three = Radiobutton(temp_frame, text='2', variable=self.v, value=3)
        self.rb_three.pack(side=TOP)

        self.submit_button = Button(temp_frame, text='Set', 
                font=('Times', '12'), width=10, command=self.submit_dpi)
        self.submit_button.pack(side=TOP)
        

    def submit_dpi(self):
        dpi = self.v.get()
        dpi -= 1

        self.submit_button.config(state=DISABLED)
        
        with open(f'{self.main_dir}/py/settings.json', 'r') as settings_file:
            settings_file = json.load(settings_file)
            pass

        settings_file['dpi_awareness'] = dpi

        with open(f'{self.main_dir}/py/settings.json', 'w') as new_settings:
            json.dump(settings_file, new_settings, indent=4)
            pass
        
        self.dpi_window.destroy()

        messagebox.showinfo('Success', message='Setting changed; restart the app to see changes.')

    def update_settings_file(self, which):

        self.new_value = fd.askdirectory(initialdir=self.main_dir)
        if self.new_value == '':
            pass
        else:
            with open(f'{self.main_dir}/py/settings.json', 'r') as settings_file:
                settings_file = json.load(settings_file)
                pass

            settings_file[which] = self.new_value

            with open(f'{self.main_dir}/py/settings.json', 'w') as file_to_save:
                json.dump(settings_file, file_to_save, indent=4)
                pass

            messagebox.showinfo('Success', message='Directory Saved')


    def change_default_tab(self):
        self.set_tab_window = Toplevel()
        self.set_tab_window.title('Set Default Tab')
        self.set_tab_window.geometry('350x160')
        self.set_tab_window.iconbitmap(f'{self.main_dir}/py/icon.ico')
        temp_frame = Frame(self.set_tab_window)
        temp_frame.pack()

        self.rb_one = Radiobutton(temp_frame, text='Transcribe', 
                variable=self.tv, value='transcription')
        self.rb_one.pack(side=TOP)

        self.rb_two = Radiobutton(temp_frame, text='Prepare JSON', 
                variable=self.tv, value='prepare_json')
        self.rb_two.pack(side=TOP)

        self.rb_three = Radiobutton(temp_frame, text='Collate', 
                variable=self.tv, value='collation')
        self.rb_three.pack(side=TOP)

        self.submit_tab_button = Button(temp_frame, text='Set', 
                font=('Times', '12'), width=10, command=self.submit_tab)
        self.submit_tab_button.pack(side=TOP)

    def submit_tab(self):
        with open(f'{self.main_dir}/py/settings.json', 'r') as settings_file:
            settings_file = json.load(settings_file)
            pass
        settings_file['tab_on_start'] = self.tv.get()
        with open(f'{self.main_dir}/py/settings.json', 'w') as file:
            json.dump(settings_file, file, indent=4)
        self.set_tab_window.destroy()
        messagebox.showinfo('Success', message=f'Next time you start Tendon,\n\
the {settings_file["tab_on_start"]} tab will open by default.')