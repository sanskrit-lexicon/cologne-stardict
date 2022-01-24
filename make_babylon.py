# This Python file uses the following encoding: utf-8
"""
Usage:
python make_babylon_from_txt.py dictId [0/1]
0 for viewing (\n line break), 1 for production (More HTML like line break)
e.g.
python make_babylon_from_txt.py md 1
"""
from __future__ import print_function
import re
import codecs
import sys
import os
from indic_transliteration.sanscript import transliterate, SchemeMap, SCHEMES
import utils
import params
from parseheadline import parseheadline
from dictdata import dictdata


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
    fout.write('#stripmethod=keep\n#sametypesequence=h\n\n')
    scheme_map = SchemeMap(SCHEMES['slp1'], SCHEMES['devanagari'])

    print("Reading hwnorm1.")
    hwnormlist = utils.readhwnorm1c()
    print("Reading hwextra.")
    altlist = utils.read_hwextra(dictId)
    start = False
    end = False
    data = fin.read()
    lins = data.split('\n')
    for lin in lins:
        if lin.startswith('<L>'):
            start = True
            end = False
            result = ''
        if lin.startswith('<LEND>'):
            end = True
            result = utils.devaconvert(result, dictId)
            result = re.sub('<.*?>', '', result)
            result = re.sub('[ ]+', ' ', result)
            linkurl = utils.scanlink(dictId, pc)
            result += '<a href="' + linkurl + '" target="_blank">Scan page : ' + pc + '</a>\n'
            correctionurl = utils.correctionlink(dictId, l)
            result += '<a href="' + correctionurl + '" target="_blank">Correction submission : ' + key1 + ', ' + l + '</a>\n'
            result = re.sub('[ \t]*\n', '\n', result)
            result = re.sub('[\n]+', '\n', result)
            result = re.sub('\n$', '', result)
            if production == '1':
                result = result.replace('\n', '<BR>')
            fout.write(result)
            fout.write('\n\n')
        if start and (not end):
            if lin.startswith('<L>'):
                meta = parseheadline(lin)
                key1 = meta['k1']
                l = meta['L']
                pc = meta['pc']
                if int(l.split('.')[0]) % 10000 == 0:
                    print(l)
                if l in altlist:
                    # print(altlist[l])
                    althws = altlist[l]
                else:
                    althws = []
                if key1 in hwnormlist and (dictId.upper() in hwnormlist[key1][1]):
                    possibleheadings = hwnormlist[key1][0]
                else:
                    possibleheadings = [key1]
                possibleheadings += althws
                if dictId not in ['ae', 'mwe', 'bor']:
                    k1s = '|'.join([transliterate(head, scheme_map=scheme_map) for head in possibleheadings])
                else:
                    k1s = '|'.join(possibleheadings)
                fout.write(k1s + '\n')
            elif lin.startswith('[Page'):
                pass
            else:
                if dictId in params.regs:
                    for (a, b) in params.regs[dictId]:
                        lin = re.sub(a, b, lin)
                lin = lin.replace('¦', '')
                result += lin + '\n'
    fin.close()
    fout.close()
