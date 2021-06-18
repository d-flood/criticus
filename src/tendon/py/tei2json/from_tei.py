import re
from typing import List

import lxml.etree as et

###########################################################
###########################################################
# namespaces
tei_ns = 'http://www.tei-c.org/ns/1.0'
xml_ns = 'http://www.w3.org/XML/1998/namespace'

def get_file(tei: str):
    with open(tei, 'r', encoding='utf-8') as f:
        return f.read()

###########################################################
###########################################################

# pre parse cleanup
def pre_parse_cleanup(text): #* PASSING
    text = re.sub(r' +|\t', ' ', text)
    # text = re.sub(r' *<supplied> *', '[', text)
    text = re.sub(r' *<supplied[^<>]*>', '[', text)
    text = re.sub(r' *</supplied> *', ']', text)
    text = re.sub(r'<lb[^<>]*>', '', text)
    text = text.replace('\n', '')
    text = text.replace('<hi rend="overline">', '')
    text = text.replace('</hi>', '')
    return text

def parse(text: str):
    parser = et.XMLParser(remove_blank_text=True, encoding='utf-8', recover=True)
    return et.fromstring(text, parser)


###########################################################
###########################################################
# after parsed

def add_underdot_to_unclear_letters(root: et._Element): #* PASSING
    unclear = root.xpath('//tei:unclear', namespaces={'tei': tei_ns})
    for u in unclear:
        underdotted = []
        if u.text is None:
            print(f'NONE WORD!!!{et.tostring(u, encoding="unicode")=}')
        for letter in u.text:
            underdotted.append(f'{letter}\u0323')
        u.text = ''.join(underdotted)

def remove_unclear_tags(text: str): #* PASSING
    text = re.sub(r'<unclear[^<>]*>', '', text)
    text = re.sub(r'</unclear[^<>]*>', '', text)
    return text

def write_xml(root):
    tree = root.getroottree()
    tree.write('output.xml', encoding='utf-8', pretty_print=True)

def handle_abbr(abbr: et._Element): #* PASSING
    if not abbr.text and abbr.getchildren():
        if abbr.getchildren()[0].text:
            return abbr.getchildren()[0].text
    elif abbr.text and not abbr.getchildren():
        return abbr.text

def handle_app(app: et._Element, hand: str):
    words = []
    if hand == 'firsthand':
        rdg_type = 'orig'
    else:
        rdg_type = 'corr'
    for rdg in app.getchildren():
        if rdg.get('type') == rdg_type and rdg.get('hand') == hand:
            for word in rdg.getchildren():
                if word.text:
                    words.append(word.text)
                elif word.getchildren():
                    if word.getchildren()[0].text:
                        words.append(word.getchildren()[0].text)
                    elif word.getchildren()[0].tag == '{http://www.tei-c.org/ns/1.0}abbr':
                        t = handle_abbr(word.getchildren()[0])
                        if t:
                            words.append(t)
    return words

def get_all_words_in_verse(verse: et._Element, hand: str) -> List[str]:
    words = []
    for elem in verse:
        if elem.tag == f'{{{tei_ns}}}w' and not elem.getchildren() and elem.text:
            words.append(elem.text)
        elif elem.tag == f'{{{tei_ns}}}w' and elem.getchildren():
            for child in elem:
                if child.tag == f'{{{tei_ns}}}abbr':
                    words.append(handle_abbr(child))
                elif child.text:
                    words.append(child.text)
        elif elem.tag == f'{{{tei_ns}}}app':
            words += handle_app(elem, hand)  
    return words

def handle_lacunae(words: List[str]) -> List[str]: ###* PASSING
    indices_of_lac_words = []
    for i, word in enumerate(words):
        if not word:
            print(f'\n{word=}\n')
        lac_word_found = re.search(r'\[[^\[\]]*\]', word)
        if lac_word_found and lac_word_found.group(0) == word: # entire word is supplied, i.e. lacunose b/c word == [word]
            indices_of_lac_words.append(i)
    if 0 in indices_of_lac_words and 1 not in indices_of_lac_words:
        words[1] = words[1].replace(words[1], f'___{words[1]}')
    furthest_lac_index = None
    for index in indices_of_lac_words:
        if furthest_lac_index:
            if index <= furthest_lac_index:
                continue
            else:
                furthest_lac_index = None
        if index + 1 not in indices_of_lac_words and index != 0:
            words[index-1] = words[index-1].replace(words[index-1], f'{words[index-1]}___')
        elif index + 1 in indices_of_lac_words:
            words[index-1] = words[index-1].replace(words[index-1], f'{words[index-1]}___')
            for i, _ in enumerate(words, 1):
                if index + i in indices_of_lac_words:
                    furthest_lac_index = index + i
                else:
                    break 
    new_words = []
    for i, w in enumerate(words):
        if i in indices_of_lac_words:
            continue
        else:
           new_words.append(w) 
    return new_words

def remove_duplicate_witnesses(witnesses: List[list]):
    found_wits = []
    new_wits = []
    for w in witnesses:
        if w[1] not in found_wits:
            found_wits.append(w[1])
            new_wits.append(w)
    return new_wits

def get_verse_as_tuple(verse: et._Element, hands: list = ['firsthand']) -> List[tuple]:
    witnesses = []
    for hand in hands:
        words = get_all_words_in_verse(verse, hand)
        words = handle_lacunae(words)
        witnesses.append((hand, words))
    witnesses = remove_duplicate_witnesses(witnesses)
    return witnesses
