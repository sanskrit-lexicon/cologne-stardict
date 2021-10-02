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
from indic_transliteration import sanscript
import utils
import params
from parseheadline import parseheadline


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
    print("Reading hwnorm1.")
    hwnormlist = utils.readhwnorm1c()
    print("Reading hwextra.")
    altlist = utils.read_hwextra(dictId)
    # print(altlist)
    start = False
    end = False
    for lin in fin:
        if lin.startswith('<L>'):
            start = True
            end = False
            result = ''
        if lin.startswith('<LEND>'):
            end = True
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
                if int(l.split('.')[0]) % 1000 == 0:
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
                    k1s = '|'.join([sanscript.transliterate(head, 'slp1', 'devanagari') for head in possibleheadings])
                else:
                    k1s = '|'.join(possibleheadings)
                fout.write(k1s + '\n')
                linkurl = utils.scanlink(dictId, pc)
                fout.write('<a href="' + linkurl + '">' + pc + '</a>\n')
            elif lin.startswith('[Page'):
                pass
            else:
                if dictId in params.regs:
                    for (a, b) in params.regs[dictId]:
                        lin = re.sub(a, b, lin)
                lin = lin.replace('¦', '')
                lin = utils.devaconvert(lin, dictId)
                lin = re.sub('<.*?>', '', lin)
                lin = re.sub('[ ]+', ' ', lin)
                result += lin
    fin.close()
    fout.close()
