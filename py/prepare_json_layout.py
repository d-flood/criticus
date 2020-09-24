from tkinter import *
from tkinter import messagebox as mb
from tkinter import ttk
from tkinter import filedialog as fd
import re
import io
import os
import ctypes
import platform
import json
 


class Prepare_json:

    def __init__(self, prepare_json_tab, main_dir, root):

        self.reg_font = ('Times', '12')
        self.main_dir = main_dir
        self.root = root
        self.a = IntVar()
        self.v_or_chv = IntVar()

        #frames
        self.prepare_json_frame = Frame(prepare_json_tab)
        self.prepare_json_frame.pack(fill=BOTH, expand=1)

        Grid.rowconfigure(self.prepare_json_frame, 0, weight=1)
        Grid.rowconfigure(self.prepare_json_frame, 1, weight=1)
        Grid.rowconfigure(self.prepare_json_frame, 2, weight=1)
        Grid.columnconfigure(self.prepare_json_frame, 0, weight=1)
        Grid.columnconfigure(self.prepare_json_frame, 1, weight=1)
        Grid.columnconfigure(self.prepare_json_frame, 2, weight=1)
        Grid.columnconfigure(self.prepare_json_frame, 3, weight=1)

        self.all_or_range_frame = LabelFrame(self.prepare_json_frame, text='Prepare: ',
                font=self.reg_font)
        self.all_or_range_frame.grid(row=0, column=0, pady=20, padx=20, 
                        columnspan=4, sticky=EW)

        self.ref_format_frame = LabelFrame(self.prepare_json_frame, text='Reference Format',
                font=self.reg_font)
        self.ref_format_frame.grid(row=1, column=0, pady=20, padx=20, 
                        columnspan=4, sticky=EW)

        self.buttons_frame = Frame(self.prepare_json_frame)
        self.buttons_frame.grid(row=2, column=0, pady=20, padx=20, 
                        columnspan=4, sticky=EW)

        #all_or_range_frame
        self.range_rb1 = Radiobutton(self.all_or_range_frame, 
                text='All verses in file', variable=self.a, width=15,
                value=1, font=self.reg_font, anchor=W)
        self.range_rb1.grid(row=0, column=0)
        self.range_rb2 = Radiobutton(self.all_or_range_frame,
                text='Range', variable=self.a, width=15,
                value=2, font=self.reg_font, anchor=W)
        self.range_rb2.grid(row=1, column=0)
        self.range_rb3 = Radiobutton(self.all_or_range_frame,
                text='Auto', variable=self.a, width=15,
                value=3, font=self.reg_font, anchor=W, state=DISABLED)
        self.range_rb3.grid(row=2, column=0)

        self.from_label = Label(self.all_or_range_frame,
                text='from:', font=self.reg_font)
        self.from_label.grid(row=1, column=1)

        self.range_from_entry = Entry(self.all_or_range_frame,
                font=self.reg_font, width=10)
        self.range_from_entry.grid(row=1, column=2, pady=10)

        self.to_label = Label(self.all_or_range_frame, text='to:',
                font=self.reg_font)
        self.to_label.grid(row=1, column=3, padx=25, pady=10)

        self.range_to_entry = Entry(self.all_or_range_frame,
                font=self.reg_font, width=10)
        self.range_to_entry.grid(row=1, column=4, padx=10, pady=10)

        self.auto_label = Label(self.all_or_range_frame,
                text='unit:', font=self.reg_font)
        self.auto_label.grid(row=2, column=1, pady=10, padx=10)

        self.auto_unit_entry = Entry(self.all_or_range_frame,
                font=self.reg_font, width=10, state=DISABLED)
        self.auto_unit_entry.grid(row=2, column=2, pady=10, padx=10)

        #ref_format frame
        self.vrs_rb = Radiobutton(self.ref_format_frame,
                text='verse', variable=self.v_or_chv, width=15,
                value=1, font=self.reg_font, anchor=W)
        self.vrs_rb.grid(row=0, column=0)

        self.vrs_chp_rb = Radiobutton(self.ref_format_frame,
                text='chapter:verse', variable=self.v_or_chv, width=15,
                value=2, font=self.reg_font, anchor=W)
        self.vrs_chp_rb.grid(row=1, column=0)

        self.chapter_label = Label(self.ref_format_frame,
                text='book and chapter or pericope:', font=self.reg_font)
        self.chapter_label.grid(row=0, column=1, pady=10, padx=10)
        
        self.chapter_entry = Entry(self.ref_format_frame,
                font=self.reg_font, width=10)
        self.chapter_entry.grid(row=0, column=2, pady=10, padx=10)

        self.chapter_example_label = Label(self.ref_format_frame,
                text='e.g. Rom13 or Rom1.1-8\n\
the style of abbreviation is not important')
        self.chapter_example_label.grid(row=0, column=3, pady=10, padx=10)

        #bottom
        self.siglum_label = Label(self.buttons_frame,
                text='siglum:', font=self.reg_font)
        self.siglum_label.grid(row=0, column=0, padx=10,)

        self.siglum_entry = Entry(self.buttons_frame,
                font=self.reg_font, width=10)
        self.siglum_entry.grid(row=0, column=1, padx=20, pady=10)

        self.prepare_json_button = Button(self.buttons_frame,
                text='Prepare JSON Files', font=self.reg_font,
                command=self.get_text_to_prepare)
        self.prepare_json_button.grid(row=0, column=3, padx=20, pady=10)


    def get_text_to_prepare(self):

        self.line_errors = []
        self.all_or_range = self.a.get()
        self.v_or_vrschp = self.v_or_chv.get()

        if self.all_or_range == 0 or self.v_or_vrschp == 0 or self.siglum_entry.get() == '':
            mb.showinfo('Forget something?', message='"All" or "Range" \
must be selected; "verse" or "chapter:verse" must be selected; and \
the witness siglum must be entered.')
            return

        if self.v_or_vrschp == 1 and self.chapter_entry.get() == '':
            mb.showinfo('One more thing', message='If the verse lines \
in your text file begin with only the verse numbers, then the \
"Chapter or Pericope" field must be filled.')
            return
    
        if self.v_or_vrschp == 1 and self.all_or_range == 2:
            mb.showinfo('Info', message='If the text file does not have \
full references, e.g. "Rom 1:1" beginning every line, then "Prepare:" must \
be set to "All verses in file"')
            return

        if self.all_or_range == 2: 
            if self.range_from_entry.get() == '' or self.range_to_entry.get() == '':
                mb.showinfo('Forgetting something?', message='If a range \
of verses in a file is to be prepared, then both the "from" and "to" \
input fields must be filled.')
                return

        with open(f'{self.main_dir}/py/settings.json') as settings_file:
            settings_file = json.load(settings_file)

        if settings_file['mss_path'] == '':
            mss_path = self.main_dir
        else:
            mss_path = settings_file['mss_path']
            if os.path.isdir(f'{mss_path}/{self.siglum_entry.get()}/Plain Text Transcriptions'):
                mss_path = f'{mss_path}/{self.siglum_entry.get()}/Plain Text Transcriptions'

        if settings_file['CE_path'] == '':
            mb.showerror('Uh-oh', message='The Collation Editor directory \
must be set. Do this in Settings.')
            return

        self.ce_path = settings_file['CE_path']


        text_path = fd.askopenfilename(initialdir=mss_path,
                title='Select Plain Text Transcription', 
                filetypes=[("Plain Text files", '*.txt')])
        if not text_path:
            return

        if self.all_or_range == 1:

            with open(text_path, 'r', encoding='utf-8') as text:
                text = text.readlines()

            self.prepare_lines(text)
        
        elif self.all_or_range == 2:

            with open(text_path, 'r', encoding='utf-8') as text:
                text = text.read()
            text = re.sub('\n', 'zzz', text)
            text = re.search(
                self.range_from_entry.get() + r'(.+)' + self.range_to_entry.get(), 
                text)
            
            try:
                text = text.group(0)
                text = re.sub('zzz', '\n', text)        
                text = text.splitlines()
                self.prepare_lines(text)
            except:
                mb.showerror('Uh-oh',
                            message='The chosen range is not in the chosen \
document; at least, not as expected')

        # This is only for those who have set up their directories structures exactly.
        # It can only be enabled by directly editing the settings file--this is to 
        # prevent anyone from accidentally using it.
        elif self.all_or_range == 3:
            pass

        if self.line_errors == []:
            mb.showinfo('All Done', message=f'The text file has been \
divided into individual verse files and saved to {self.ce_path}/collation\
/data/textrepo/json/.')
        else:
            mb.showinfo('All Done', message=f'The conversion is done, \
but the following lines could not be processed:\n{self.line_errors}')


    def prepare_lines(self, text):
        

        siglum = self.siglum_entry.get()
        if self.v_or_vrschp == 2:
            for line in text:
                ref = re.search(r'(.+):(\d+)|(.+).(\d+)', line)

                try:
                    ref = ref.group(0)
                except:
                    self.line_errors.append(line)
                    continue

                line = re.sub(ref, '', line)
                ref = ref.replace(':', '.')
                ref = ref.replace(' ', '')

                self.build_json_files(line, siglum, ref)

        elif self.v_or_vrschp == 1:
            for line in text:
                ref = re.search(r'(\d+)', line)

                try:
                    ref = ref.group(0)
                except:
                    self.line_errors.append(line)
                    continue

                line = re.sub(ref, '', line)
                ref = f'{self.chapter_entry.get()}.{ref}'

                self.build_json_files(line, siglum, ref)


    def build_json_files(self, line, siglum, ref):
            
        line = line.split()
        index = 2

        verse_dict = dict(
            _id=f'{siglum}_{ref}',
            transcription=siglum,
            transcription_siglum=siglum, 
            siglum=siglum, 
            context=ref, 
            n=ref,
        )

        tokens = []
        for word in line:
            token = dict(
                index=str(index),
                siglum=siglum,
                reading=siglum,
                original=word,
                rule_match=[word],
                t=word)
            tokens.append(token)
            index += 2

        witnesses = [dict(id=siglum, tokens=tokens)]
        verse_dict['witnesses'] = witnesses

        metadata = dict(_id=siglum, siglum=siglum)

        if os.path.isdir(f'{self.ce_path}/collation/data/textrepo/json/{siglum}'):
            pass
        else:
            try:
                os.mkdir(f'{self.ce_path}/collation/data/textrepo/json/{siglum}')
            except:
                mb.showerror('So close...', message='Could not save completed \
files. Most likely this is because the path to the main Collation Editor \
directory was not set properly. Ensure that this is set in Settings and \
that all the directories in the Collation Editor main directory are unchanged \
from their original state.')
                return
            
        with open(f'{self.ce_path}/collation/data/textrepo/json/{siglum}/{ref}.json', 
                'w', encoding='utf-8') as file:
            json.dump(verse_dict, file, indent=4, ensure_ascii=False)

        with open(f'{self.ce_path}/collation/data/textrepo/json/{siglum}/metadata.json', 
                'w', encoding='utf-8') as file:
            json.dump(metadata, file, indent=4, ensure_ascii=False)