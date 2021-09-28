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
    hwnormlist = utils.readhwnorm1c()
    start = False
    end = False
    for lin in fin:
        if lin.startswith('<L>'):
            start = True
            end = False
            result = ''
        if lin.startswith('<LEND>'):
            end = True
            fout.write(result)
            fout.write('\n')
        if start and (not end):
            if lin.startswith('<L>'):
                meta = parseheadline(lin)
                print(meta)
                key1 = meta['k1']
                if key1 in hwnormlist and (dictId.upper() in hwnormlist[key1][1]) and (dictId not in ['ae', 'mwe', 'bor']):
                    possibleheadings = hwnormlist[key1][0]
                    k1s = '|'.join([sanscript.transliterate(head, 'slp1', 'devanagari') for head in possibleheadings])
                else:
                    k1s = sanscript.transliterate(key1, 'slp1', 'devanagari')
                result += k1s + '\n'
            elif lin.startswith('[Page'):
                pass
            else:
                if dictId in params.regs:
                    for (a, b) in params.regs[dictId]:
                        lin = re.sub(a, b, lin)
                lin = lin.replace('¦', '')
                lin = re.sub('<.*?>', '', lin)
                lin = utils.devaconvert(lin, dictId)
                result += lin
    fin.close()
    fout.close()
    exit()

    # Read a list of normalized headwords. See https://github.com/sanskrit-coders/stardict-sanskrit/issues/66.
    hwnormlist = utils.readhwnorm1c()
    lnumEntryDict = {}
    ms = params.meaningseparator
    if dictId in ms:
        instr = ms[dictId][0]
        outstr = ms[dictId][1]
    print(instr)
    print(outstr)
    exit()
    inputfile = os.path.join('..', dictId, 'pywork', dictId + '.xml')
    tree = ET.parse(inputfile)
    
    hw = tree.findall("./*/h/key1")
    key2s = tree.findall("./*/h/key2")
    lnum = tree.findall("./*/tail/L")
    entry = tree.findall("./*/body")

    if production == '0':
        outputfile = codecs.open('output/' + dictId + '.babylon', 'w', 'utf-8')
    elif production == '1':
        outputfile = codecs.open('production/' + dictId + '.babylon', 'w', 'utf-8')

    # Write licence text
    # outputfile.write('LICENCE.xml\n')
    # outputfile.write(unicode(licence)+u'\n\n')

    counter = 0
    for x in range(len(hw)):
        heading1 = ET.tostring(hw[x], method='text', encoding='utf-8')
        key2 = ET.tostring(key2s[x], method='text', encoding='utf-8')
        key2 = key2.decode('utf-8')
        ln = ET.tostring(lnum[x], method='text', encoding='utf-8')
        lnumEntryDict[ln] = ET.tostring(entry[x], method='html', encoding='utf-8')

        if counter % 1000 == 0:
            print(counter)
        counter += 1
        if heading1 in hwnormlist and dictId.upper() in hwnormlist[heading1][1]:
            possibleheadings = hwnormlist[heading1][0]
            # print(possibleheadings)
        else:
            possibleheadings = [heading1]
        if dictId not in ['ae', 'mwe', 'bor']:
            heading = '|'.join([transcoder.transcoder_processString(head, 'slp1', 'deva') for head in possibleheadings])
        else:
            heading = heading1

        html = lnumEntryDict[ln]
        html = re.sub(r'\[Page[0-9+ abc.-]+\]', '', html)
        if dictId in ['ben']:
            html = html.replace('-</i> <lb></lb><i>', '')
        if dictId in ['mwe', 'skd', 'vcp']:
            html = html.replace('<lb></lb>', ' ')
        elif dictId in ['ap']:
            html = re.sub('<lb></lb>[.]<b>', 'BREAK<b>', html)
            html = html.replace('<lb></lb>', ' ')
        elif dictId in ['sch']:
            html = html.replace('<div>', 'BREAK<div>')
        else:
            html = html.replace('<lb></lb>', '')
        # If there are built in divs signifying breaks, add breaks there.
        html = html.replace('<hom>', ' <hom>')
        # html = html.replace('  ', 'BREAK')
        # html = html.replace(' , ', 'BREAK')
        html = html.replace('<div n="P">', 'BREAK<div n="P">')
        html = html.replace('<div n="P1">', 'BREAK<div n="P1">')
        html = html.replace('<div n="E">', 'BREAK<div n="E">')
        html = re.sub(' <gram', 'BREAK<gram', html)
        html = re.sub('([^(])<divm', r'BREAK\g<1><divm', html)
        html = re.sub('<div n="I"', 'BREAK<div n="I"', html)
        html = re.sub('<div n="NI"', 'BREAK<div n="NI"', html)
        html = re.sub('<div n="p"', 'BREAK<div n="p"', html)
        html = re.sub('<div n="1"', 'BREAK<div n="1"', html)
        html = re.sub('<div n="2"', 'BREAK\t<div n="2"', html)
        html = re.sub('<div n="3"', 'BREAK\t\t<div n="3"', html)
        html = re.sub('<div n="4"', 'BREAK\t\t\t<div n="4"', html)
        html = html.replace('<div n="lb">', 'BREAK<div n="lb">')
        html = re.sub('¦[,. ]*', 'BREAK', html)
        html = html.replace('¦,', 'BREAK')
        html = html.replace('¦', 'BREAK')
        if dictId in ['ccs']:
            html = html.replace('<s>°', 'BREAK<s>°')
        if dictId in ['gst', 'vei']:
            html = html.replace('<sup>', 'BREAK\t<sup>')
        if dictId in ['pd']:
            html = html.replace('<br>', '')
        if dictId in ['sch']:
            html = re.sub(r'\[Schµ[0-9]+\]', '', html)
            html = re.sub('€[0-9]+', '', html)
            html = html.replace(' -- ', 'BREAK -- ')
        if dictId in ['krm']:
            html = html.replace('<div n=', 'BREAK<div n=')
        if dictId in ['ben']:
            html = html.replace('-- Cf', 'BREAK-- Cf')
        html = html.replace('<b>--Comp.</b>', 'BREAK<b>--Comp.</b>BREAK') # ap90
        if dictId in ['wil']:
            html = html.replace('¦ ', 'BREAK')
            html = html.replace('<body>.<s>', '<body><s>')
            html = html.replace('.E.', 'BREAK.E.')
            html = html.replace('<br>', 'BREAK')
        html = html.decode('utf-8')
        if dictId in ['wil']:
            html = html.replace(u'²', r'\t')
        if dictId in ['ap']:
            html = html.replace(u'(-<i>', '-(<i>')
            html = html.replace(u'<i>', 'BREAK<i>')
            html = html.replace('<b>', 'BREAK<b>')
        html = html.replace(u'<b><s>º', u'BREAK<b><s>º')  # ap90
        if dictId in ['pd']:
            html = html.replace('<b>', 'BREAK<b>')
        if dictId in ['mw72']:
            html = html.replace(u'<i>—', u'BREAK<i>—')
        if dictId in meaningseparator and re.search(instr, html):
            html = re.sub(instr, outstr, html)
        html = re.sub(u'[(](<b><s>--[a-zA-Z]+</s>)', r'BREAK\g<1>', html)  # ap90
        if dictId in ['ben']:
            html = html.replace(u'¤10', u'')  # BEN usually has dIrga mentioned and hrasva being mentioned by breve.
        if dictId in ['cae', 'ccs']:
            html = html.replace(u'BREAK</s>', u'</s>BREAK')  # https://github.com/sanskrit-lexicon/cologne-stardict/issues/3#issuecomment-455857610
        if dictId in ['pwg']:
            html = html.replace('^', '/')
        sanskrittext = re.findall('<s>([^<]*)</s>', html)
        html = re.sub(u'(<s>--[a-zA-Z]+</s>)', r'BREAK\g<1>', html)  # ap90
        for sans in sanskrittext:
            html = html.replace('<s>' + sans + '</s>', '<s>' + transcoder.transcoder_processString(sans, 'slp1', 'deva') + '</s>')
        if dictId in ['ben']:
            html = re.sub('<i>([^<]*[-][,])</i>', r'BREAK<i>\g<1></i>', html)
            html = html.replace('i. e.BREAK <i>', 'i.e. <i>')
        if dictId in ['ae']:
            html = re.sub('<i>-(.*)</i>', r'BREAK\t<i>\g<1></i>', html)
            html = re.sub('<b>([0-9]+)</b>', r'BREAK\t\t<b>\g<1></b>', html)
        if dictId in ['ben', 'bur', 'snp', 'stc', 'mci', 'mw72', 'sch']:
            italictext = re.findall('<i>([^<]*)</i>', html)
            for ital in italictext:
                rep = ital.lower()
                rep = rep.replace('ch', 'c')
                rep = rep.replace('sh', 'z')
                rep = transcoder.transcoder_processString(rep, 'roman', 'slp1')
                rep = transcoder.transcoder_processString(rep, 'slp1', 'deva')
                html = html.replace('<i>' + ital + '</i>', '<i>' + rep + '</i>')
        if dictId in ['stc','vei']:
            italictext = re.findall('<body><b>([^<]*)</b>', html)
            for ital in italictext:
                rep = ital.lower()
                rep = transcoder.transcoder_processString(rep, 'roman', 'slp1')
                rep = transcoder.transcoder_processString(rep, 'slp1', 'deva')
                html = html.replace('<body><b>' + ital + '</b>', '<body><b>' + rep + '</b>BREAK')
                html = re.sub(u'<body><b>([^<]*)।</b>', r'<body><b>\g<1></b>', html)  # vei
        if dictId in ['bur']:
            html = html.replace(u'|', u'')
        if dictId in ['stc']:
            html = transcoder.transcoder_processString(html, 'as', 'roman')
            html = html.replace('|', '')
        if dictId in ['cae']:
            html = html.replace(u'·', u'')
        if dictId in ['gst']:
            html = html.replace(' ^', 'BREAK ^')
        if dictId in ['mwe']:
            html = re.sub(u'[)]([^ ,.;\n])', r') \g<1>', html)
        html = html.replace('- ', '')
        html = re.sub('[ ]+' ,' ', html)
        html = html.replace('&amp;', '&')
        html = html.replace(u'î', u'ī')
        html = html.replace(u'â', u'ā')
        html = re.sub('[<][^>]*[>]', '', html)
        if dictId in ['ap']:
            html = html.replace('- -', '-')
        if dictId in ['pd']:
            html = re.sub('^[.]', '', html)
        if dictId in ['ae']:
            html = html.replace('- -', '')  # अंगीकार- -द्योतक
        if dictId in ['mwe']:
            html = html.replace(u'. — ', u'. BREAK — ')
        html = html.replace('BREAK', '<BR>')
        if dictId in ['gra']:
            html = transcoder.transcoder_processString(key2, 'slp1', 'deva') + '<BR>' + html
        html = html.replace('<BR><BR>', '<BR>')
        if production == '0':
            html = html.replace('<BR>', '\n')
        outputfile.write(heading + '\n')
        html = html.lstrip('\n')
        outputfile.write(html + '\n\n')
    outputfile.close()

