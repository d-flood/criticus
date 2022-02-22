import random
import re
import xml.etree.ElementTree as et
from lxml.etree import _Element # pylint: disable=no-name-in-module
import lxml.etree as ET
from typing import List

from markdown.core import Markdown
from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor
from markdown.treeprocessors import Treeprocessor


def preprocess_md(md: str):
    for x in punctuation:
        md = md.replace(x, f'<pc>{x}</pc>')
    md = md.replace('-\n', '') # this replacement must come before the <lb> sub
    md = md.replace('[', '~~')
    md = md.replace(']', '~~')
    md = re.sub(r'\n<lb([^<>]*)> *', r'\n<lb\1> ', md)
    return md

###########################################################
# post process markup before final xml processing.
# This section must result in valid xml to be parsed with lxml

def add_text_body_opening_tags(markup: str):
    '''User defines in markdown where the TEI header information ends
    and the transcription begins by placing three or more fullstops
    (e.g. '...') on their own line. Only replace first occurance so that
    the use of fullstops is available to user for other things (e.g. lacunae).'''
    return re.sub(r'\.\.\.+', '<text xml:lang="grc"><body>', markup, count=1)

def h4_to_book_div(markup: str):
    '''Repurpose the h4 tags renderd from the '#### <book>' markup syntax
    for a div tag that wraps all transcription pertaining to the book
    specified in the h4 text. User most close this tag by adding '####'
    without any text at the end of the book transcription.'''
    book_match = re.search(r'<h4>[^<>]+</h4>', markup).group(0)
    book = book_match.replace('<h4>', '')
    book = book.replace('</h4>', '')
    try:
        book = nt_to_igntp[book]
    except KeyError:
        pass
    book_elem = f'<div type="book" n="{book}">\n'
    markup = markup.replace(book_match, book_elem)
    return markup, book

def h5_to_chapter_div(markup: str, book):
    '''Repurpose the h5 tags renderd from the '##### <chapter number>' markup syntax
    for a div tag that wraps all transcription pertaining to the chapter
    specified in the h5 text. User most close this tag by adding '#####'
    without any text at the end of the chapter transcription.'''
    chapters = re.findall(r'<h5>[^<>]+</h5>', markup)
    for chapter_match in chapters:
        chapter = chapter_match.replace('<h5>', '')
        chapter = chapter.replace('</h5>', '')
        chapter_elem = f'<div type="chapter" n="{book}K{chapter}">'
        markup = markup.replace(chapter_match, chapter_elem)
    return markup

def bulk_replace(markup: str):
    '''Convert Markdown tag names to TEI tags
    (and other things).'''
    for x in html_to_tei:
        markup = markup.replace(x[0], x[1])
    return markup

def add_tei_boilerplate_and_ending_tags(markup: str):
    return f'''<!DOCTYPE TEI><?xml-stylesheet type="text/xsl" href="tei_transcription.xsl"?><TEI xmlns="http://www.tei-c.org/ns/1.0">{markup}</body></text></TEI>'''

def postprocess_markup(markup: str):
    markup = add_text_body_opening_tags(markup)
    markup, book = h4_to_book_div(markup)
    markup = h5_to_chapter_div(markup, book)
    markup = bulk_replace(markup)
    markup = bulk_replace(markup)
    markup = add_tei_boilerplate_and_ending_tags(markup)

    return markup

###########################################################
###########################################################
# Post process by parsing xml

def fill_out_untranscribed_commentary_markup(root: _Element):
    '''convert abbreviated "<comm/>" and "<comm lines=4> tags into IGNTP equivalent markup'''
    tei_ns = 'http://www.tei-c.org/ns/1.0'
    xml_ns = 'http://www.w3.org/XML/1998/namespace'
    comms = root.xpath(f'//tei:comm', namespaces={'tei': tei_ns}) # type: List[_Element]
    for comm in comms:
        if comm.get('lines'):
            index = comm.getparent().index(comm)
            try:
                lines = int(comm.get('lines'))
            except:
                lines = 1
            for _ in range(lines):
                parent = comm.getparent() #type: _Element
                comm_element = ET.Element('note', type='commentary', nsmap={None: tei_ns, 'xml': xml_ns})
                comm_element.text = 'One line of untranscribed commentary text'
                lb = ET.Element('lb', nsmap={None: tei_ns, 'xml': xml_ns})
                parent.insert(index, lb)
                parent.insert(index+1, comm_element)
            comm.getparent().remove(comm)
        else:
            comm.tag = 'note'
            comm.attrib['type'] = 'commentary'
            comm.text = 'untranscribed commentary text'
    return root

def fill_out_verse_unit_attributes(root: _Element):
    '''Convert verse number e.g. n="6" to full IGNTP format e.g. n="B06K11V6"'''
    tei_ns = 'http://www.tei-c.org/ns/1.0'
    verse_units = root.xpath(f'//tei:ab', namespaces={'tei': tei_ns}) # type: List[_Element]
    for v in verse_units: #type: _Element
        v.attrib['n'] = f'{v.getparent().get("n")}V{v.get("n")}'
    return root

def add_page_break_type(root: _Element):
    '''adds type="folio" to the page break element
    for a very minor convenvience'''
    tei_ns = 'http://www.tei-c.org/ns/1.0'
    for pb in root.xpath('//tei:pb', namespaces={'tei': tei_ns}):
        pb.attrib['type'] = 'folio'
    return root

def postprocess_xml(root: _Element):
    root = fill_out_untranscribed_commentary_markup(root)
    root = fill_out_verse_unit_attributes(root)
    root = add_page_break_type(root)
    return root

###########################################################
###########################################################

class TokenizeText(Preprocessor):
    """ wrap individual transcribed words in <w> tags """
    def rando_str(self):
        chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        random_list = [random.choice(chars) for _ in range(5)]
        rando =  ''.join(random_list)
        return f'$$${rando}'

    def replace_words_with_mid_break(self, text, replacements):
        breaks_in_word = re.findall(r'<lb[^<>]*>', text)
        for brk in breaks_in_word:
            rando = self.rando_str()
            text = text.replace(brk, f'{rando}')
            replacements.append((brk, rando))
        return text, replacements

    def replace_user_markups(self, text, replacements):
        user_markups = re.findall(r'{[^{}]+}', text)
        for m in user_markups:
            rando = self.rando_str()
            text = text.replace(m, f'{rando} ')
            replacements.append((m, rando))
        return text, replacements

    def replace_markups(self, text, replacements):
        markups = re.findall(r'<[^<>]+>', text)
        for m in markups:
            rando = self.rando_str()
            text = text.replace(m, f' {rando} ')
            replacements.append((m, f'{rando}'))
        return text, replacements

    def replace_notes(self, text, replacements):
        notes = re.findall(r'\*[^*]+\*', text)
        for n in notes:
            rando = self.rando_str()
            text = text.replace(n, f'{rando}')
            replacements.append((n, f'{rando}'))
        return text, replacements

    def build_new_text(self, text):
        new_text = []
        for word in text.split():
            if (word not in punctuation_no_spaces
                and word != '|'
                and word[0] not in ['*', '+']
                and not word.startswith('$$$')):

                word = word.replace(word, f'<w>{word}</w>')
            new_text.append(word)
        text = ''.join(new_text)
        return text

    def replace_randos(self, text, replacements):
        for r in replacements:
            text = text.replace(r[1], r[0])
        return text

    def tokenize_text(self, text: str):
        '''tokenize transcription words but ignore other 
        words (e.g. notes) and markup that may contain 
        spaces but should not be tokenized'''
        replacements = []
        text, replacements = self.replace_words_with_mid_break(text, replacements)
        text, replacements = self.replace_user_markups(text, replacements)
        text, replacements = self.replace_markups(text, replacements)
        text, replacements = self.replace_notes(text, replacements)   
        text = self.build_new_text(text)
        text = self.replace_randos(text, replacements)
        return text

    def run(self, lines: list):
        new_lines = []
        for line in lines:
            if line.startswith('#') or line.startswith('...') or line.startswith('>'):
                new_lines.append(line)
            else:
                new_line = self.tokenize_text(line)
                new_lines.append(new_line)
        return new_lines

class RestructureTree(Treeprocessor):
    def create_elements(self):
        return (
            et.Element('teiHeader'),
            et.Element('fileDesc'),
            et.Element('titleStmt'),
            et.Element('respStmt'),
            et.Element('name'),
            et.Element('resp')
        )
    def remove_elements(self, root, elements_to_remove: tuple):
        for elem in elements_to_remove:
            root.remove(elem)

    def get_header_info(self, root):
        return (
            root.find('h1'),
            root.find('h2'),
            root.find('h3'),
        )

    def build_tei_header(self, root):
        (tei_header, file_desc, title_statement, resp_statement, 
         name, resp) = self.create_elements()
        title, person, date = self.get_header_info(root)
        root.insert(0, tei_header)
        tei_header.append(file_desc)
        file_desc.append(title_statement)
        title_statement.append(title)
        title_statement.append(resp_statement)
        resp_statement.append(resp)
        resp_statement.append(name)
        title.attrib = {'type': 'document'}
        name.text = person.text
        name.attrib = {'type': 'person'}
        resp.text = 'Transcribed by'
        resp.attrib = {'when-iso': date.text}
        self.remove_elements(root, (title, date, person))

    def run(self, root: et.Element):
        self.build_tei_header(root)         


class TEI(Extension):
    def extendMarkdown(self, md: Markdown, key="TEI", index=200):
        md.treeprocessors.register(RestructureTree(md), 'RestructureTree', 200)
        md.preprocessors.register(TokenizeText(md), 'tokenize', 200)


punctuation = (' . ', ' , ', ' \u0387 ', ' : ', ' + ', ' ~ ')
punctuation_no_spaces = ('.', ',', '\u0387', ':', '+', '~')

html_to_tei = (
    ('<h1', '<title'),
    ('</h1>', '</title>'),
    ('<h2', '<respStmt'),
    ('</h2>', '</respStmt>'),
    ('<code', '<unclear'),
    ('</code>', '</unclear>'),
    ('<v', '<ab'),
    ('</v>', '</ab>'),
    ('<p>', ''),
    ('</p>', ''),
    ('<p/>', ''),
    ('<h4/>', '</div>'),
    ('<h4></h4>', '</div>'),
    ('<h5/>', '</div>'),
    ('<h5></h5>', '</div>'),
    ('<strong', '<seg type="margin" '),
    ('</strong>', '</seg>'),
    ('<del>', '<supplied>'),
    ('</del>', '</supplied>'),
    ('<em', '<note type="local"'),
    ('</em>', '</note>'),
    ('<ins>', '<app><rdg type="orig" hand="firsthand">'),
    ('|', '</rdg><rdg type="corr" hand="corrector">'),
    ('</ins>', '</rdg></app>'),
    ('\n', ''),
)

nt_to_igntp = {
    'Matt': 'B01',
    'Matthew': 'B01',
    'Mark': 'B02',
    'Luke': 'B03',
    'John': 'B04',
    'Acts': 'B05',
    'Rom': 'B06',
    'Romans': 'B06',
    '1 Cor': 'B07',
    '1Cor': 'B07',
    '1 Corinthians': 'B07',
    '2 Cor': 'B08',
    '2Cor': 'B08',
    '2 Corinthians': 'B08',
    'Gal': 'B09',
    'Galatians': 'B09',
    'Eph': 'B10',
    'Ephesians': 'B10',
    'Phil': 'B11',
    'Philippians': 'B11',
    'Col': 'B12',
    'Colossians': 'B12',
    '1 Thess': 'B13',
    '1Thess': 'B13',
    '1 Thessalonians': 'B13',
    '2 Thess': 'B14',
    '2Thess': 'B14',
    '2 Thessalonians': 'B14',
    '1 Tim': 'B15',
    '1Tim': 'B15',
    '1 Timothy': 'B15',
    '2 Tim': 'B16',
    '2Tim': 'B16',
    '2 Timothy': 'B16',
    'Titus': 'B17',
    'Phlm': 'B18',
    'Philemon': 'B18',
    'Heb': 'B19',
    'Hebrews': 'B19',
    'Jas': 'B20',
    'James': 'B20',
    '1 Pet': 'B21',
    '1Pet': 'B21',
    '1 Peter': 'B21',
    '2 Pet': 'B22',
    '2Pet': 'B22',
    '2 Peter': 'B22',
    '1 John': 'B23',
    '1John': 'B23',
    '2 John': 'B24',
    '2John': 'B24',
    '3 John': 'B25',
    '3John': 'B25',
    'Jude': 'B26',
    'Rev': 'B27',
    'Revelation': 'B27',
}
