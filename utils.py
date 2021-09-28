import datetime
import codecs
import re
import os
from collections import defaultdict
from indic_transliteration import sanscript
import params
from parseheadline import parseheadline

# Function to return timestamp
def timestamp():
    return datetime.datetime.now()


# Function to read normalized headwords (hwnorm1c.txt) into a dict
# Returns a dict with headword as key and the list of associated headwords as value.
def readhwnorm1c():
    fin = codecs.open('input/hwnorm1c.txt', 'r', 'utf-8')
    lines = fin.readlines()
    output = {}
    for line in lines:
        line = line.strip()
        chunks = line.split(';')
        words = []
        if len(chunks) > 1:
            baseword = chunks[0].split(':')[0]
            for chunk in chunks[1:]:
                worddictsep = chunk.split(':')
                word = worddictsep[0]
                dicts = worddictsep[-1].split(',')
                if not baseword == word:
                    result = [baseword, word]
                    output[word] = (result, dicts)
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
    

def devaconvert(line, dictId):
    if dictId in ['armh', 'skd', 'vcp']:
            line = sanscript.transliterate(line, 'slp1', 'devanagari')
            print(line)
    elif dictId not in params.devaparams:
        sanskrittexts = re.findall('{#(.*?)#}', line)
        for san in sanskrittexts:
            sanrep = sanscript.transliterate(san, 'slp1', 'devanagari')
            line = line.replace('{#' + san + '#}', sanrep)
    else:
        for (startreg, endreg, intran) in params.devaparams[dictId]:
            sanskrittexts = re.findall(startreg + '(.*?)' + endreg, line)
            for san in sanskrittexts:
                sanrep = sanscript.transliterate(san, intran, 'devanagari')
                line = line.replace('{%' + san + '%}', sanrep)
    line = line.replace('<div n="1"', '\n<div n="1"')
    line = line.replace('<div n="2"', '\n\t<div n="2"')
    line = line.replace('<div n="3"', '\n\t\t<div n="3"')
    line = line.replace('<div n="4"', '\n\t\t\t<div n="4"')
    return line
    
