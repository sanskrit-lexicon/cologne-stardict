import datetime
import re
import os
from collections import defaultdict
from functools import lru_cache
from indic_transliteration.sanscript import transliterate, SchemeMap, SCHEMES, _get_scheme_map
import params
from parseheadline import parseheadline

slp1_map = SchemeMap(SCHEMES['slp1_accented'], SCHEMES['devanagari'])
iast_map = SchemeMap(SCHEMES['iast'], SCHEMES['devanagari'])

ACCENT_CARET_PATTERN = re.compile(r'([^0-9 ])\^')
ACCENT_SLASH_PATTERN = re.compile(r'([^0-9 ])/')
BACKSLASH_PATTERN = re.compile(r'\\')

DEVANAGARI_TEXT_PATTERN = re.compile(r'{#(.*?)#}')
DEVANAGARI_PATTERN_CACHE = {}

devaconvert_cache = {}
_slp1_transliterate_cache = {}
_iast_transliterate_cache = {}


def _cached_transliterate(text, scheme_map):
    if scheme_map is slp1_map:
        if text not in _slp1_transliterate_cache:
            _slp1_transliterate_cache[text] = transliterate(text, scheme_map=slp1_map)
        return _slp1_transliterate_cache[text]
    elif scheme_map is iast_map:
        if text not in _iast_transliterate_cache:
            _iast_transliterate_cache[text] = transliterate(text, scheme_map=iast_map)
        return _iast_transliterate_cache[text]
    return transliterate(text, scheme_map=scheme_map)


def applyaccent(line, dictId):
    if dictId in ['pw', 'pwg']:
        line = ACCENT_CARET_PATTERN.sub(r'\g<1>॑', line)
        line = ACCENT_SLASH_PATTERN.sub(r'\g<1>꣫', line)
        line = BACKSLASH_PATTERN.sub("॒", line)
    else:
        line = ACCENT_SLASH_PATTERN.sub(r'\g<1>॑', line)
    return line


def scanlink(dictId, pc):
    url = 'https://dub.sh/cslp?dict=' + dictId.upper() + '&page=' + pc
    return url


def correctionlink(dictId, lnum):
    url = 'https://dub.sh/cslc?dict=' + dictId
    return url


def devaconvert(line, dictId):
    cache_key = (line, dictId)
    if cache_key in devaconvert_cache:
        return devaconvert_cache[cache_key]
    
    result = line
    
    if dictId in ['armh', 'skd', 'vcp']:
        result = result.replace('|', '\x00')
        result = _cached_transliterate(result, slp1_map)
        result = result.replace('\x00', '|')
    elif dictId not in params.devaparams:
        sanskrittexts = DEVANAGARI_TEXT_PATTERN.findall(result)
        for san in sanskrittexts:
            sanrep = applyaccent(san, dictId)
            sanrep = _cached_transliterate(sanrep, slp1_map)
            result = result.replace('{#' + san + '#}', sanrep)
    else:
        for (startreg, endreg, intran) in params.devaparams[dictId]:
            if (startreg, endreg) not in DEVANAGARI_PATTERN_CACHE:
                DEVANAGARI_PATTERN_CACHE[(startreg, endreg)] = re.compile(startreg + '(.*?)' + endreg)
            pattern = DEVANAGARI_PATTERN_CACHE[(startreg, endreg)]
            sanskrittexts = pattern.findall(result)
            for san in sanskrittexts:
                if intran == 'iast':
                    san1 = san.lower()
                else:
                    san1 = san
                sanrep = applyaccent(san1, dictId)
                if intran == 'iast':
                    sanrep = _cached_transliterate(sanrep, iast_map)
                else:
                    sanrep = _cached_transliterate(sanrep, slp1_map)
                result = result.replace(startreg+ san + endreg, sanrep)
    result = result.replace('<div n="1"', '\n<div n="1"')
    result = result.replace('<div n="2"', '\n\t<div n="2"')
    result = result.replace('<div n="3"', '\n\t\t<div n="3"')
    result = result.replace('<div n="4"', '\n\t\t\t<div n="4"')
    
    devaconvert_cache[cache_key] = result
    return result


def readhwnorm1c():
    fin = open('input/hwnorm1c.txt', 'r', encoding='utf-8')
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
    fin.close()
    return output


def read_hwextra(dictId):
    filein = os.path.join('..', 'csl-orig', 'v02', dictId, dictId + '_hwextra.txt')
    fin = open(filein, 'r', encoding='utf-8')
    result = defaultdict(list)
    for lin in fin:
        meta = parseheadline(lin)
        if 'LP' in meta:
            result[meta['LP']].append(meta['k1'])
    fin.close()
    return result