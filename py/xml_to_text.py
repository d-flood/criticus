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

def xml_to_text(xml_fn):

    with open(xml_fn, 'r', encoding='utf-8') as tree:
        tree = tree.read()
        pass
    # remove whitespace for improved regex
    tree = re.sub(r'\n|\t', '', tree)
    tree = re.sub(r'  +', '', tree)
    tree = re.sub(r' xmlns="http://www.tei-c.org/ns/1.0"', '', tree)
    tree = re.sub(r'<\?xml(.+)1\.0"\?>', '', tree)
    with open(xml_fn, 'w', encoding='utf-8') as file:
        file.write(tree)
    
    parser = ET.XMLParser(remove_blank_text=True)

    tree = ET.parse(xml_fn, parser)

    root = tree.getroot()

    try:
        ms_siglum = root.find('teiHeader/fileDesc/sourceDesc/msDesc/msIdentifier').text
    except:
        ms_siglum = 'unknown-wit'

    books = root.findall('text/body/div[@type="book"]')
    all_references = []
    whole_doc = ''

    for book in books:
        intf_book = book.get('n')
        # convert intf book name to sbl equivalent
        for x in intf_sbl_books:
            if intf_book in intf_sbl_books[x]:
                sbl_book = x[1]

        all_chapters = book.findall('div[@type="chapter"]')
            
        for chapter in all_chapters:
            chapter_intf = chapter.get('n')
            chapter_intf = re.sub(intf_book, '', chapter_intf)
            chapter_str = re.sub('K', '', chapter_intf)

            all_verses = chapter.findall('ab')
            # if first_chapter
            for verse in all_verses:
                verse_intf = verse.get('n')
                verse_intf = re.sub(intf_book+chapter_intf, '', verse_intf)
                verse_str = re.sub('V', '', verse_intf)
                
                full_ref = f'{sbl_book} {chapter_str}:{verse_str}'
                all_references.append(full_ref)
                verse_text = ''

                for elem in verse:
                    if elem.tag == 'w':
                        word_text = elem.text
                        if word_text != None:
                            verse_text = f'{verse_text} {word_text}'
                            
                        for w in elem:
                            if w.tag == 'supplied':
                                if w.tail != None:
                                    verse_text = f'{verse_text} [{w.text}]{w.tail}'
                                else:
                                    verse_text = f'{verse_text}[{w.text}] '
                            if w.tag == 'unclear':
                                if w.tail != None:
                                    verse_text = f'{verse_text} {w.text}{w.tail}'
                                else:
                                    verse_text = f'{verse_text}{w.text} '
                            if w.tag == 'abbr':
                                for y in w:
                                    if y.tag == 'hi':
                                        verse_text = f'{verse_text} {y.text}'
                            if w.tag == 'lb':
                                if w.tail != None:
                                    verse_text = f'{verse_text}{w.tail}'

                    if elem.tag == 'app':
                        for rdg in elem:
                            if rdg.get('type') == 'orig':
                                for sub_w in rdg:
                                    if sub_w.tag != 'pc':
                                        sub_w_text = sub_w.text
                                        verse_text = f'{verse_text} {sub_w_text}'
                                    for sub_sub_w in sub_w:
                                        if sub_sub_w.tag == 'unclear':
                                            if sub_sub_w.tail != None:
                                                verse_text = f'{verse_text} {sub_sub_w.text}{sub_sub_w.tail}'
                                            else:
                                                verse_text = f'{verse_text}{sub_sub_w.text}'
                                        elif sub_sub_w.tag == 'lb':
                                            verse_text = f'{verse_text}{sub_sub_w.tail}'
                                            

                whole_verse = f'{full_ref} {verse_text.lstrip()}'
                whole_doc = f'{whole_doc.lstrip()}\n{whole_verse}'        

    content = f'{all_references[0]}–{all_references[-1]}'

    save_fn = f'{ms_siglum}_{content}.txt'
    save_fn = re.sub(':', '.', save_fn)

    whole_doc = re.sub(r'~|\+|None|⁘', '', whole_doc) #add other nonstandard punctuation (punctuation in the text rather than <pc> elements) here if needed
    whole_doc = re.sub(r' +', ' ', whole_doc)
    
    # this re pattern is needed because of a quirk of how I kept traxk of
    # information. An alternative should be sought.
    whole_doc = re.sub(r'[^α-ωΑ-Ω\[\]]+\n', '\n', whole_doc)

    # this pattern is for fixing verses that repeat because
    # they begin on one page and end on another
    complete_doc = ''
    whole_doc = whole_doc.splitlines()
    repeat = ''
    for line in whole_doc:
        ref = re.search(r'(.+):(\d+) ', line)
        ref = ref.group(0)
        if ref == repeat:
            line = re.sub(ref, '', line)
            complete_doc = f'{complete_doc}{line}'
        else:
            complete_doc = f'{complete_doc.lstrip()}\n{line}'
        repeat = ref

    return complete_doc, save_fn