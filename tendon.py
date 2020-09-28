import ctypes
import json
import os
import pathlib
import platform
from tkinter import Tk, ttk

from py.collation_layout import Collation
from py.functions import set_tab_on_start
from py.menu import Options
from py.prepare_json_layout import Prepare_json
from py.transcription_layout import Transcription

main_dir = str(pathlib.Path(__file__).parent.absolute()).replace('\\', '/')

with open('py/settings.json', 'r') as settings_file:
    settings_file = json.load(settings_file)
    pass

dpi = settings_file['dpi_awareness']
efficiency_mode = settings_file['efficiency_mode']

my_os = platform.system()
if my_os == "Windows":
    ctypes.windll.shcore.SetProcessDpiAwareness(dpi)


root = Tk()
root.geometry('1200x650')
root.title('Tendon  v0.5')
root.iconbitmap(f'{main_dir}/py/icon.ico')

options_menu = Options(root, main_dir)

tabs = ttk.Notebook(root)
transcription_tab = ttk.Frame(tabs)
prepare_json_tab = ttk.Frame(tabs)
collation_tab = ttk.Frame(tabs)

tabs.add(transcription_tab, text="  Transcribe  ", pad=5)
tabs.add(prepare_json_tab, text="  Prepare JSON  ", pad=5)
tabs.add(collation_tab, text="  Collate  ", pad=5)
tabs.pack(expand=1, fill="both")
tab_to_select = set_tab_on_start(main_dir, transcription_tab,
                                 prepare_json_tab, collation_tab)
tabs.select(tab_to_select)

prepare_json_layout = Prepare_json(prepare_json_tab, main_dir, root)
transcription_layout = Transcription(transcription_tab, main_dir, root)
collation_layout = Collation(collation_tab, main_dir, root, my_os)


root.mainloop()
