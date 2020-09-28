import json
import os
import re
from lxml import etree as ET

# a dict for converting common NT ref styles to either the INTF or SBL format
intf_sbl_books = {
    ('B01', 'Matt'): ('Matt', 'Mt', 'B01'),
    ('B02', 'Mark'): ('Mark', 'Mk', 'B02'),
    ('B03', 'Luke'): ('Luke', 'Lk', 'L', 'B03'),
    ('B04', 'John'): ('John', 'Jn', 'B04'),
    ('B05', 'Acts'): ('Acts', 'Ac', 'A', 'B05'),
    ('B06', 'Rom'): ('Rom', 'Romans', 'R', 'Rm', 'B06'),
    ('B07', '1 Cor'): ('1 Cor', '1Cor', '1C', 'IC', 'I Cor', 'B07'),
    ('B08', '2 Cor'): ('2 Cor', '2Cor', '2C', 'IIC', 'II Cor', 'B08'),
    ('B09', 'Gal'): ('Galatians', 'Gal', 'B09'),
    ('B10', 'Eph'): ('Ephesians', 'Eph', 'B10'),
    ('B11', 'Phil'): ('Philippians', 'Phil', 'B11'),
    ('B12', 'Col'): ('Col', 'Colossians', 'B12'),
    ('B13', '1 Thess'): ('1 Thess', '1Th', 'ITh', 'I Thess', 'B13'),
    ('B14', '2 Thess'): ('2 Thess', '2Th', 'IITh', 'II Thess', 'B14'),
    ('B15', '1 Tim'): ('1 Tim', '1Tim', 'ITim', 'I Tim', 'B15'),
    ('B16', '2 Tim'): ('2 Tim', '2Tim', 'IITim', 'II Tim', 'B16'),
    ('B17', 'Titus'): ('Titus', 'Tit', 'B17'),
    ('B18', 'Phlm'): ('Philm', 'Philemon', 'Philem', 'B18'),
    ('B19', 'Heb'): ('Heb', 'Hebrews', 'B19'),
    ('B20', 'Jas'): ('James', 'Jam', 'Jas', 'B20'),
    ('B21', '1 Pet'): ('1 Pet', '1Pet', '1 Peter', 'IPet', 'I Pet', 'B21'),
    ('B22', '2 Pet'): ('2 Pet', '2Pet', '2 Peter', 'IIPet', 'II Pet', 'B22'),
    ('B23', '1 John'): ('1 John', '1 Jn', '1Jn', '1John',
                        'I John', 'I Jn', 'IJn', 'I John', 'B23'),
    ('B24', '2 John'): ('2 John', '2 Jn', '2Jn', '2John', 'II John',
                        'II Jn', 'IIJn', 'II John', 'B24'),
    ('B25', '3 John'): ('3 John', '3 Jn', '3Jn', '3John', 'III John',
                        'III Jn', 'IIIJn', 'III John', 'B25'),
    ('B26', 'Jude'): ('Jude', 'Jd', 'B26'),
    ('B27', 'Rev'): ('Rev', 'Revelation', 'B27')
}

# a dict for assinging a non-numeral suffic to the witness siglum
siglum_suf = {
    'corrector': 'cor',
    'corrector1': 'a',
    'corrector2': 'b',
    'corrector3': 'c',
    'corrector4': 'd',
    'corrector5': 'e',
    'firsthand': '*'
}


# xml_fn = 'test/0150.xml'
# siglum = '0150'
# ce_path = 'C:/Users/david/OneDrive/_PhD/Research/tx_cx/Collation/Collation_Editor/CE'
# verse_range = ('Rom 13:6', 'Rom 13:7')
# intf_or_sbl = 'sbl'

class XML_to_JSON:

    def __init__(self, xml_fn, siglum, ce_path, verse_range,
                 intf_or_sbl):

        self.ce_path = ce_path
        self.verse_range = verse_range
        self.intf_or_sbl = intf_or_sbl

        with open(xml_fn, 'r', encoding='utf-8') as tree:
            self.tree = tree.read()
            pass
        # remove whitespace for improved regex
        self.tree = re.sub(r'\n|\t', '', self.tree)
        self.tree = re.sub(r'  +', '', self.tree)
        # with these simple files, it is easier for me to scrub namespaces than handle them
        self.tree = re.sub(
            r' xmlns="http://www.tei-c.org/ns/1.0"', '', self.tree)
        self.tree = re.sub(r'<\?xml(.+)1\.0"\?>', '', self.tree)
        # create a temp file because the lxml parser seems to work better
        # when parsing from a file as opposed to from a string
        with open('py/tmp.xml', 'w', encoding='utf-8') as file:
            file.write(self.tree)

        parser = ET.XMLParser(remove_blank_text=True)
        self.tree = ET.parse('py/tmp.xml', parser)

        os.remove('py/tmp.xml')

        self.root = self.tree.getroot()
        self.siglum = siglum

        self.find_books()
        self.make_save_metadata()

    def find_books(self):

        try:
            self.ms_siglum = root.find(
                'teiHeader/fileDesc/sourceDesc/msDesc/msIdentifier').text
        except:
            self.ms_siglum = 'unknown-wit'

        books = self.root.findall('text/body/div[@type="book"]')
        self.all_references = []
        self.whole_doc = ''

        for self.book in books:
            self.intf_book = self.book.get('n')
            # convert intf book name to sbl equivalent
            for x in intf_sbl_books:
                if self.intf_book in intf_sbl_books[x]:
                    self.sbl_book = x[1]
                    self.find_chapters()

    def find_chapters(self):
        all_chapters = self.book.findall('div[@type="chapter"]')

        for self.chapter in all_chapters:
            self.chapter_intf = self.chapter.get('n')
            self.chapter_intf = re.sub(self.intf_book, '', self.chapter_intf)
            self.chapter_str = re.sub('K', '', self.chapter_intf)
            self.find_verses()

    def find_verses(self):

        all_verses = self.chapter.findall('ab')
        self.process_verse = True
        if isinstance(self.verse_range, tuple):
            self.process_verse = False

        for self.verse in all_verses:
            verse_intf = self.verse.get('n')
            verse_string = re.sub(
                self.intf_book+self.chapter_intf, '', verse_intf)
            verse_str = re.sub('V', '', verse_string)
            if self.intf_or_sbl == 'sbl':
                self.full_ref = f'{self.sbl_book} {self.chapter_str}:{verse_str}'
            elif self.intf_or_sbl == 'intf':
                self.full_ref = verse_intf

            if self.process_verse == False:
                if self.full_ref == self.verse_range[0] or self.verse.get('n') == self.verse_range[0]:
                    self.process_verse = True
            if self.process_verse == True:
                # print(self.full_ref)
                self.all_references.append(self.full_ref)
                self.verse_text = ''
                self.tokens = []
                self.corr_tokens = []
                self.corr1_tokens = []
                self.corr2_tokens = []
                self.corr3_tokens = []
                self.corr4_tokens = []
                self.corr5_tokens = []
                self.corr_firsthand_tokens = []

                self.token_list = [
                    (self.tokens, self.siglum),
                    (self.corr_tokens, f'{self.siglum}cor'),
                    (self.corr1_tokens, f'{self.siglum}a'),
                    (self.corr2_tokens, f'{self.siglum}b'),
                    (self.corr3_tokens, f'{self.siglum}c'),
                    (self.corr4_tokens, f'{self.siglum}d'),
                    (self.corr5_tokens, f'{self.siglum}e'),
                    (self.corr_firsthand_tokens, f'{self.siglum}*')
                ]

                self.for_elem_in_verse()
            else:
                continue

            if isinstance(self.verse_range, tuple):
                if self.full_ref == self.verse_range[1] or self.verse.get('n') == self.verse_range[1]:
                    self.process_verse = False

    def for_elem_in_verse(self):
        self.index = 2
        for self.elem in self.verse:
            if self.elem.tag == 'w':
                if self.elem.text != None:
                    if re.search(r'\d|[a-zA-Z]', self.elem.text):
                        pass
                    else:
                        self.elem_tag_w()
            if self.elem.tag == 'app':
                self.elem_tag_app()
            self.index += 2

        self.build_json()

    def elem_tag_w(self):
        word_text = self.elem.text
        if word_text != None and self.elem.getchildren() == []:
            self.tokens.append(self.make_json_token(
                self.index, self.siglum, word_text))

        for w in self.elem:
            if w.tag == 'supplied':
                if w.tail != None:
                    word_text = f'{word_text}[{w.text}]{w.tail}'
                else:
                    word_text = f'{word_text}[{w.text}] '
            if w.tag == 'unclear':
                if w.tail != None:
                    word_text = f'{w.text}{w.tail}'
                else:
                    word_text = f'{word_text}{w.text} '
            if w.tag == 'abbr':
                for y in w:
                    if y.tag == 'hi':
                        word_text = y.text
            if w.tag == 'lb':
                if w.tail != None:
                    word_text = f'{word_text}{w.tail}'
            self.tokens.append(self.make_json_token(
                self.index, self.siglum, word_text))

    def elem_tag_app(self):
        for rdg in self.elem:
            if rdg.get('type') == 'orig':
                for self.sub_w in rdg:
                    self.for_sub_w()
            elif rdg.get('type') == 'corr':
                hand = rdg.get('hand')
                for self.sub_w in rdg:
                    self.if_corr(hand)
                if rdg.getchildren() == []:
                    self.which_corr(hand).append(
                        self.make_json_token(self.index, f'{self.siglum}{siglum_suf[hand]}', 'omit'))

    def if_corr(self, hand):
        if self.sub_w.tag != 'pc':
            sub_w_text = self.sub_w.text
            if sub_w_text != None:
                self.which_corr(hand).append(
                    self.make_json_token(self.index, f'{self.siglum}{siglum_suf[hand]}', sub_w_text))
            else:
                for element in self.sub_w:
                    self.which_corr(hand).append(
                        self.make_json_token(self.index, f'{self.siglum}{siglum_suf[hand]}', element.text))

    def for_sub_w(self):
        if self.sub_w.tag != 'pc':
            word_text = self.sub_w.text
        for sub_sub_w in self.sub_w:
            if sub_sub_w.tag == 'unclear':
                if sub_sub_w.tail != None:
                    word_text = f'{sub_sub_w.text}{sub_sub_w.tail}'
                else:
                    word_text = sub_sub_w.text
            elif sub_sub_w.tag == 'lb':
                word_text = sub_sub_w.tail
            self.tokens.append(self.make_json_token(
                self.index, self.siglum, word_text))

    def make_json_token(self, index: int, siglum, word):
        word = word.replace('None', '')
        token = dict(
            index=str(index),
            siglum=siglum,
            reading=siglum,
            original=word,
            rule_match=[word],
            t=word)
        return token

    # determine which list to append a newly made token
    def which_corr(self, corr):
        if corr == 'corrector':
            return self.corr_tokens
        elif corr == 'firsthand':
            return self.corr_firsthand_tokens
        elif corr == 'corrector1':
            return self.corr1_tokens
        elif corr == 'corrector3':
            return self.corr3_tokens
        elif corr == 'corrector4':
            return self.corr4_tokens
        elif corr == 'corrector5':
            return self.corr5_tokens
        else:
            return self.corr_tokens

    def build_json(self):

        ref = self.full_ref.replace(' ', '')
        verse_dict = dict(
            _id=f'{self.siglum}_{ref}',
            transcription=self.siglum,
            transcription_siglum=self.siglum,
            siglum=self.siglum,
            context=ref,
            n=ref,
        )
        witnesses = []
        for tokens, siglum in self.token_list:
            if tokens != []:
                witnesses.append([dict(id=siglum, tokens=tokens)])

        verse_dict['witnesses'] = witnesses

        self.save_json(verse_dict, ref)

    def save_json(self, verse_dict, ref):

        print(f'{self.ce_path}/collation/data/textrepo/json/{self.siglum}')

        if not os.path.isdir(f'{self.ce_path}/collation/data/textrepo/json/{self.siglum}'):
            os.mkdir(
                f'{self.ce_path}/collation/data/textrepo/json/{self.siglum}')

        with open(f'{self.ce_path}/collation/data/textrepo/json/{self.siglum}/{ref.replace(":", ".")}.json', 'w', encoding='utf-8') as file:
            json.dump(verse_dict, file, indent=4, ensure_ascii=False)
            pass

    def make_save_metadata(self):

        metadata = dict(_id=self.siglum, siglum=self.siglum)

        with open(f'{self.ce_path}/collation/data/textrepo/json/{self.siglum}/metadata.json', 'w', encoding='utf-8') as file:
            json.dump(metadata, file, indent=4, ensure_ascii=False)
            pass

        self.all_references = list(dict.fromkeys(self.all_references))
        self.all_references = ', '.join(self.all_references)


# run_file = XML_to_JSON(xml_fn, siglum, ce_path, verse_range, intf_or_sbl)
