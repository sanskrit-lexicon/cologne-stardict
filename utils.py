import datetime
import codecs
import re
import os
from collections import defaultdict
from indic_transliteration.sanscript import transliterate, SchemeMap, SCHEMES
import params
from parseheadline import parseheadline

slp1_map = SchemeMap(SCHEMES['slp1_accented'], SCHEMES['devanagari'])
iast_map = SchemeMap(SCHEMES['iast'], SCHEMES['devanagari'])
# Function to return timestamp
def timestamp():
    return datetime.datetime.now()


# Function to read normalized headwords (hwnorm1c.txt) into a dict
# Returns a dict with (headword, dict_code) as key and list of alternate headwords as value.
# For each baseword, includes all alternates from all chunks for dictionaries that have the baseword.
def readhwnorm1c():
    fin = codecs.open('input/hwnorm1c.txt', 'r', 'utf-8')
    lines = fin.readlines()
    output = {}
    for line in lines:
        line = line.strip()
        chunks = line.split(';')
        if len(chunks) > 1:
            baseword = chunks[0].split(':')[0]
            base_dicts = chunks[0].split(':')[-1].split(',')
            all_alternates = [baseword]
            for chunk in chunks[1:]:
                word = chunk.split(':')[0]
                if word != baseword:
                    all_alternates.append(word)
            for d in base_dicts:
                output[(baseword, d)] = all_alternates
            for chunk in chunks[1:]:
                alt_word = chunk.split(':')[0]
                alt_dicts = chunk.split(':')[-1].split(',')
                for d in alt_dicts:
                    output[(alt_word, d)] = all_alternates
    return output


def licencetext(dictId):
    fin = codecs.open('../' + dictId + '/pywork/' + dictId + 'header.xml', 'r', 'utf-8')
    data = fin.read()
    fin.close()
    return data


def read_hwextra(dictId):
    filein = os.path.join('..', 'csl-orig', 'v02', dictId, dictId + '_hwextra.txt')
    fin = codecs.open(filein, 'r', 'utf-8')
    result = defaultdict(list)
    for lin in fin:
        meta = parseheadline(lin)
        if 'LP' in meta:
            result[meta['LP']].append(meta['k1'])
    return result
    

def applyaccent(line, dictId):
    if dictId in ['pw', 'pwg']:
        line = re.sub(r'([^0-9 ])\^', r'\g<1>॑', line)
        line = re.sub(r'([^0-9 ])/', r'\g<1>꣫', line)
        line = line.replace("\\", "॒")
    else:
        line = re.sub(r'([^0-9 ])/', r'\g<1>॑', line)
    return line


def scanlink(dictId, pc):
	# https://github.com/sanskrit-lexicon/cologne-stardict/issues/33#issuecomment-1036415566
	# https://yaahi.github.io/?cp=0001-a&d=MW72
    url = 'https://yaahi.github.io/?cp=' + pc + '&d=' + dictId.upper()
    return url


def correctionlink(dictId, lnum):
	# https://github.com/sanskrit-lexicon/cologne-stardict/issues/33#issuecomment-1038606969
	# https://yaahi.github.io/?d=mw&e=2
    url = 'https://yaahi.github.io/?d=' + dictId + '&e=' + lnum
    return url


def devaconvert(line, dictId):
    if dictId in ['armh', 'skd', 'vcp']:
            line = transliterate(line, scheme_map=slp1_map)
    elif dictId not in params.devaparams:
        sanskrittexts = re.findall('{#(.*?)#}', line)
        for san in sanskrittexts:
            sanrep = applyaccent(san, dictId)
            sanrep = transliterate(sanrep, scheme_map=slp1_map)
            line = line.replace('{#' + san + '#}', sanrep)
    else:
        for (startreg, endreg, intran) in params.devaparams[dictId]:
            sanskrittexts = re.findall(startreg + '(.*?)' + endreg, line)
            for san in sanskrittexts:
                if intran == 'iast':
                    san1 = san.lower()
                else:
                    san1 = san
                sanrep = applyaccent(san1, dictId)
                if intran == 'iast':
                    sanrep = transliterate(sanrep, scheme_map=iast_map)
                else:
                    sanrep = transliterate(sanrep, scheme_map=slp1_map)
                line = line.replace(startreg+ san + endreg, sanrep)
    line = line.replace('<div n="1"', '\n<div n="1"')
    line = line.replace('<div n="2"', '\n\t<div n="2"')
    line = line.replace('<div n="3"', '\n\t\t<div n="3"')
    line = line.replace('<div n="4"', '\n\t\t\t<div n="4"')
    return line
    
