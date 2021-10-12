import datetime
import codecs
import re
import os
from collections import defaultdict
from indic_transliteration.sanscript import transliterate, SchemeMap, SCHEMES
import params
from parseheadline import parseheadline

slp1_map = SchemeMap(SCHEMES['slp1'], SCHEMES['devanagari'])
iast_map = SchemeMap(SCHEMES['slp1'], SCHEMES['devanagari'])
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
    

def applyaccent(line, dictId):
    if dictId in ['pw', 'pwg']:
        line = re.sub('([^0-9 ])\^', '\g<1>॑', line)
        line = re.sub('([^0-9 ])/', '\g<1>꣫', line)
        line = line.replace("\\", "॒")
    else:
        line = re.sub('([^0-9 ])/', '\g<1>॑', line)
    return line


def scanlink(dictId, pc):
    url = 'https://www.sanskrit-lexicon.uni-koeln.de/scans/csl-apidev/servepdf.php?dict=' + dictId.upper() + '&page=' + pc
    return url


def correctionlink(dictId, lnum):
    url = 'https://github.com/sanskrit-lexicon/csl-ldev/blob/main/v02/' + dictId + '/' + lnum + '.txt'
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
    
