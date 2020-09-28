from py.xml_to_text import xml_to_text
from natsort import natsorted
import pathlib
from subprocess import Popen
import subprocess
import json
import platform
import ctypes
import os
import io
import re
from tkinter import (Grid, Label, LabelFrame, BOTH, N, S, E, W,
                     Button, BOTTOM, Text, END, messagebox, ttk,
                     filedialog as fd)


class Transcription:

    def __init__(self, transcription_tab, main_dir, root):

        self.root = root
        self.main_dir = main_dir
        self.reg_font = ('Times', '12')
        self.tx_frame = LabelFrame(transcription_tab,
                                   text='Transcription', font=self.reg_font)
        self.tx_frame.pack(fill=BOTH, expand=1)

        Grid.rowconfigure(self.tx_frame, 0, weight=1)
        Grid.rowconfigure(self.tx_frame, 1, weight=1)
        Grid.columnconfigure(self.tx_frame, 0, weight=1)
        Grid.columnconfigure(self.tx_frame, 1, weight=1)

        self.launch_ote_button = Button(self.tx_frame,
                                        text='Launch OTE', font=self.reg_font, height=2,
                                        width=20, command=self.launch_ote)
        self.launch_ote_button.grid(row=0, column=0,
                                    padx=50, pady=20)

        self.save_html_button = Button(self.tx_frame,
                                       text='Save HTML', font=self.reg_font, height=2,
                                       width=20, command=self.save_html)
        self.save_html_button.grid(row=1, column=0,
                                   padx=50, pady=20)

        self.combine_html_button = Button(self.tx_frame,
                                          text='Combine HTML', font=self.reg_font, height=2,
                                          width=20, command=self.combine_html)
        self.combine_html_button.grid(row=0, column=1,
                                      padx=50, pady=20)

        self.xml_to_txt_button = Button(self.tx_frame,
                                        text='XML to TXT', font=self.reg_font, height=2,
                                        width=20, command=self.xml_to_txt)
        self.xml_to_txt_button.grid(row=1, column=1,
                                    padx=50, pady=20)

        self.text_box_frame = LabelFrame(transcription_tab,
                                         text='text box', font=self.reg_font)
        self.text_box_frame.pack(side=BOTTOM, fill=BOTH, expand=1)

        self.text_box = Text(self.text_box_frame, relief="sunken",
                             bd=2, height=3)
        self.text_box.pack(fill=BOTH, expand=1)

    def launch_ote(self):
        cont = False
        with open(f'{self.main_dir}/py/settings.json', 'r') as settings_file:
            settings_file = json.load(settings_file)
            pass
        ote_path = settings_file['OTE_path']
        if ote_path == '':
            messagebox.showinfo('Not quite ready',
                                message="The Online Transcription Editor's directory\n\
has not been set yet. Do this under 'Options'.")
        else:
            try:
                os.chdir(ote_path)
                cont = True
            except:
                messagebox.showerror('Uh-oh',
                                     message='Could not find the OTE directory--set it by clicking on "Options"')
            if cont == True:
                try:
                    Popen("start python -m http.server 8000", shell=True)
                    subprocess.call(
                        'start chrome "http://localhost:8000/wce-ote/"', shell=True)
                except:
                    messagebox.showerror('Uh-oh',
                                         message='There was a problem starting the OTE')
                os.chdir(self.main_dir)

    # Gather settings, filename, template
    def save_html(self):
        self.cont = False
        try:
            with open(f'{self.main_dir}/py/settings.json', 'r') as settings_file:
                settings_file = json.load(settings_file)
                pass

            ote_path = settings_file['OTE_path']
            self.cont = True
        except:
            messagebox.showerror('Uh-oh', 'There was a problem loading the OTE directory.\n\
Make sure it is set properly by setting it under "Settings".')
        if self.cont == True:
            html = self.text_box.get(1.0, END).strip()
            if html == '':
                messagebox.showinfo("Forgetting something?", "Paste the\
HTML from the OTE into the text box on the bottom")
            else:
                fname = re.search(r"\*(.+)\*", html)
                if fname.group(0) is not None:
                    fname = re.sub(r"\*", "", fname.group(0))
                    ms = re.sub(r"_(.+)", "", fname)
                    fname = f'{fname}.html'

                try:
                    with open(f'{ote_path}/template.html', 'r') as file:
                        html_template = file.read()
                    html_for_viewing = re.sub("xxxyyyzzz", html, html_template)
                except:
                    messagebox.showwarning('Uh-oh', f'Did not find \
template.html in the OTE directory.\nTendon will still try to save the \
HTML to <your witnesses folder>/{ms}/OTE-code.')
                self.save_html_2(html, html_for_viewing, fname,
                                 ote_path, settings_file, ms)

    def save_html_2(self, html, html_for_viewing, fname, ote_path, settings_file, ms):

        mss_path = settings_file['mss_path']
        if mss_path == '':
            messagebox.showerror('Forget something?', 'Your witnesses\
 directory must be set. Find it in "Settings".')
        if self.cont == True:
            try:
                with open(f'{ote_path}/wce-ote/{ms}/{fname}', 'w') as file:
                    file.write(html_for_viewing)
            except:
                os.mkdir(f'{ote_path}/wce-ote/{ms}')
            try:
                with open(f'{ote_path}/wce-ote/{ms}/{fname}', 'w') as file:
                    file.write(html_for_viewing)
            except:
                messagebox.showerror('Uh-oh', message=f'\
Could not find or even make the directory "{ote_path}/wce-ote/{ms}".\n\
Make sure that the OTE folder is set up according to the tutorial.')
        try:
            with open(f'{mss_path}/{ms}/OTE-html/{fname}', 'w', encoding='utf-8') as plain_html:
                plain_html.write(html)
        except:
            try:
                os.mkdir(f'{mss_path}/{ms}')
            except:
                pass
            try:
                os.mkdir(f'{mss_path}/{ms}/OTE-html')
                with open(f'{mss_path}/{ms}/OTE-html/{fname}') as file:
                    file.write(html)
                    pass
            except:
                fname = fd.asksaveasfilename(initialdir=f'{self.main_dir}',
                                             defaultextension='.html', filetypes=[("HTML files", '*.html')])
                with open(fname.name, 'w') as file:
                    file.write(html)

        is_it_in_mss = os.path.isfile(f'{mss_path}/{ms}/OTE-html/{fname}')
        is_it_in_ote = os.path.isfile(f'{ote_path}/wce-ote/{ms}/{fname}')
        messagebox.showinfo('Result',
                            message=f'Saved to witnesses directory: {is_it_in_mss}\n\
Saved to OTE: {is_it_in_ote}')

    def combine_html(self):
        combined_html = ''
        with open(f'{self.main_dir}/py/settings.json', 'r') as settings_file:
            settings_file = json.load(settings_file)
        if settings_file['mss_path'] == '':
            messagebox.showerror(
                'Uh-oh', message='Set witnesses directory in Settigs.')
        else:
            html_directory = fd.askdirectory(
                initialdir=settings_file['mss_path'])
            html_fnames = os.listdir(html_directory)
            html_fnames = natsorted(html_fnames)
            for fname in html_fnames:
                if os.path.isfile(f'{html_directory}/{fname}') and fname.endswith('.html'):
                    with open(f'{html_directory}/{fname}', 'r', encoding='utf-8') as file:
                        html = file.read()
                        pass
                    combined_html = f'{combined_html}{html}'
            if combined_html == '':
                messagebox.showinfo('Aww', message='No HTML files were found')
            else:
                with open(f'{html_directory}/combined_html_transcriptions.html', 'w', encoding='utf-8') as file:
                    file.write(combined_html)
                    pass
                self.root.clipboard_clear()
                self.root.clipboard_append(combined_html)
                messagebox.showinfo('Finished',
                                    message=f'All HTML files in the selected directory\n\
have been combined and saved to \n\
{html_directory}/combined_html_transcriptions.html\n\
and coped to the clipboard. It can now be pasted into\n\
the OTE for viewing a full document or converting to XML')

    def xml_to_txt(self):
        with open(f'{self.main_dir}/py/settings.json', 'r') as settings_file:
            settings_file = json.load(settings_file)
        mss_path = settings_file['mss_path']
        if mss_path != '':
            xml_fn = fd.askopenfilename(initialdir=self.main_dir, title='Select XML Transcription',
                                        filetypes=[("XML files", '*.xml')])
        else:
            xml_fn = fd.askopenfilename(
                initialdir=mss_path, title='Select XML Transcription')
        if xml_fn.endswith('.xml'):
            # main function
            complete_doc, save_fn = xml_to_text(xml_fn)

            save_as = fd.asksaveasfile(initialdir=self.main_dir,
                                       title='Save Plain Text Transcription', initialfile=save_fn,
                                       defaultextension='.txt', filetypes=[("plain text files", '*.txt')])
            with open(save_as.name, 'w', encoding='utf-8') as file:
                file.write(complete_doc)
                pass
            messagebox.showinfo('All Done',
                                message='A plain text version of the transcription has been saved.\n\
The file should be inspected and cleaned; look especially for repeated verses.\n\
This happens when a verse begins on one page and ends on another.')
        else:
            messagebox.showerror('Not XML', message='"XML to Txt" requires \
an XML (.xml) file.')
