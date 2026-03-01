# This Python file uses the following encoding: utf-8
"""
Usage:
python3 make_babylon_synonymic.py dictId [0/1]
0 for viewing (\n line break), 1 for production (More HTML like line break)
e.g.
python3 make_babylon_synonymic.py abch 1
"""
from __future__ import print_function
import re
import codecs
import sys
import os
import datetime
from indic_transliteration.sanscript import transliterate, SchemeMap, SCHEMES
import utils
import params
from parseheadline import parseheadline
from dictdata import dictdata

scheme_map = SchemeMap(SCHEMES['slp1'], SCHEMES['devanagari'])

def to_deva(text):
    deva_text = transliterate(text, scheme_map=scheme_map)
    deva_text = deva_text.translate(str.maketrans('0123456789', '०१२३४५६७८९'))
    return deva_text

def process_block(block_lines, dictId, production):
    headwords = []
    syns_lines = []
    other_lines = []
    info_text = ""
    L = ""
    pc = ""
    
    for lin in block_lines:
        lin = lin.strip()
        if not lin:
            continue
            
        if lin.startswith('<L>'):
            l_match = re.search(r'<L>([^<]+)', lin)
            pc_match = re.search(r'<pc>([^<]+)', lin)
            if l_match: L = l_match.group(1)
            if pc_match: pc = pc_match.group(1)
            
        elif lin.startswith('<info'):
            info_match = re.search(r'<info kvvv="<s>([^<]+)</s>"/>', lin)
            if info_match:
                info_text = to_deva(info_match.group(1))
                
        elif lin.startswith('<eid>'):
            ext_match = re.search(r'<eid>([^<]+)<syns><s>([^<]+)</s>', lin)
            if ext_match:
                eid = ext_match.group(1)
                synwords = ext_match.group(2)
                syns_split = synwords.split(',')
                for w in syns_split:
                    word_no_gender = w.split('-')[0]
                    headwords.append(word_no_gender)
                syns_deva = [to_deva(w) for w in syns_split]
                eid_deva = to_deva(eid)
                syns_lines.append(", ".join(syns_deva) + f" ({eid_deva})")
                
        elif lin.startswith('<s>'):
            s_match = re.search(r'^<s>(.*)</s>$', lin)
            if s_match:
                text = s_match.group(1)
                text = text.replace('..', '॥')
                text = re.sub(r'\s*\.\s*$', ' ।', text) # Replace trailing dot with danda
                other_lines.append(to_deva(text))
                
    if not headwords:
        return ""
        
    out_lines = []
    out_lines.append("|".join(to_deva(w) for w in headwords))
    out_lines.extend(syns_lines)
    out_lines.extend(other_lines)
    if info_text:
        out_lines.append(info_text)
        
    # Link URLs
    linkurl = utils.scanlink(dictId, pc)
    correctionurl = utils.correctionlink(dictId, L)
    
    out_lines.append(f'<a href="{linkurl}" target="_blank">PDF</a>')
    out_lines.append(f'<a href="{correctionurl}" target="_blank">Correction</a>')
    
    result = "\n".join(out_lines)
    if production == '1':
        result = result.replace('\n', '<BR>')
    return result + "\n\n"


if __name__ == "__main__":
    dictId = sys.argv[1]
    production = sys.argv[2]
    inputfile = os.path.join('..', 'csl-orig', 'v02', dictId, dictId + '.txt')
    fin = codecs.open(inputfile, 'r', 'utf-8')
    if production == '0':
        outputfile = os.path.join('output', dictId + '.babylon')
    elif production == '1':
        outputfile = os.path.join('production', dictId + '.babylon')
    fout = codecs.open(outputfile, 'w', 'utf-8')
    fout.write('\n#bookname=' + dictdata[dictId][0] + ' (' + dictdata[dictId][1] + ')\n')
    fout.write('#stripmethod=keep\n#sametypesequence=h\n')
    current_date = datetime.date.today()
    fout.write('#description=Data from https://www.sanskrit-lexicon.uni-koeln.de/ as on ' + str(current_date) + '\n\n')

    data = fin.read()
    lins = data.split('\n')
    
    current_block = []
    in_entry = False
    
    for lin in lins:
        if lin.startswith('<L>'):
            in_entry = True
            current_block = [lin]
        elif lin.startswith('<LEND>'):
            in_entry = False
            current_block.append(lin)
            result = process_block(current_block, dictId, production)
            if result:
                fout.write(result)
            current_block = []
        elif in_entry:
            current_block.append(lin)

    fin.close()
    fout.close()
