# This Python file uses the following encoding: utf-8
"""
Usage:
python3 make_babylon.py dictId [0/1]
0 for viewing (\n line break), 1 for production (More HTML like line break)
e.g.
python3 make_babylon.py md 1
"""
from __future__ import print_function
import re
import sys
import os
import datetime
import time
import multiprocessing
from functools import partial
from indic_transliteration.sanscript import transliterate, SchemeMap, SCHEMES
import utils
import params
from parseheadline import parseheadline
from dictdata import dictdata


def log(msg, start_time=None):
    now = time.time()
    if start_time:
        ms = f"{now * 1000:.0f}"[-3:]
        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}.{ms}] {msg}")
    else:
        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}")


def split_into_entries(lines):
    """Split lines into list of entries. Each entry is (L, [lines...])."""
    entries = []
    current_entry = []
    current_l = None
    in_entry = False
    
    for line in lines:
        if line.startswith('<L>'):
            if current_entry and current_l:
                entries.append((current_l, current_entry))
            current_entry = [line]
            current_l = parseheadline(line)['L']
            in_entry = True
        elif line.startswith('<LEND>'):
            if in_entry:
                current_entry.append(line)
                in_entry = False
        elif in_entry:
            current_entry.append(line)
    
    if current_entry and current_l:
        entries.append((current_l, current_entry))
    
    return entries


def partition_entries(entries, num_chunks):
    """Partition entries into chunks for parallel processing."""
    chunk_size = max(1, len(entries) // num_chunks)
    chunks = []
    for i in range(0, len(entries), chunk_size):
        chunks.append(entries[i:i + chunk_size])
    return chunks


def _process_entry_lines(entry_lines, dictId, hwnormlist, altlist, dict_lbody):
    """Process a single entry's lines and return the babylon format."""
    result = ''
    for lin in entry_lines:
        if lin.startswith('<L>'):
            meta = parseheadline(lin)
            key1 = meta['k1']
            l = meta['L']
            pc = meta['pc']
            if l in altlist:
                althws = altlist[l]
            else:
                althws = []
            if (key1, dictId.upper()) in hwnormlist:
                alts = hwnormlist[(key1, dictId.upper())]
                possibleheadings = [key1]
                for a in alts:
                    if a != key1 and a not in possibleheadings:
                        possibleheadings.append(a)
            else:
                possibleheadings = [key1]
            seen = set(possibleheadings)
            for a in althws:
                if a not in seen:
                    possibleheadings.append(a)
                    seen.add(a)
            if dictId not in ['ae', 'mwe', 'bor']:
                scheme_map = SchemeMap(SCHEMES['slp1'], SCHEMES['devanagari'])
                k1s = '|'.join([transliterate(head, scheme_map=scheme_map) for head in possibleheadings])
            else:
                k1s = '|'.join(possibleheadings)
            result += k1s + '\n'
        elif lin.startswith('[Page'):
            pass
        elif lin.startswith('<LEND>'):
            pass
        else:
            if dictId in params.regs:
                for (a, b) in params.regs[dictId]:
                    lin = re.sub(a, b, lin)
            lin = lin.replace('¦', '')
            result += lin + '\n'
    return result


def _extract_lbody(entry, dictId):
    """Extract Lbody references from an entry for pass 1."""
    l = entry[0]
    entry_lines = entry[1]
    result = ''
    for lin in entry_lines:
        if lin.startswith('<L>'):
            pass
        elif lin.startswith('<LEND>'):
            pass
        else:
            if dictId in params.regs:
                for (a, b) in params.regs[dictId]:
                    lin = re.sub(a, b, lin)
            lin = lin.replace('¦', '')
            result += lin + '\n'
    return (l, result)


def _process_entry(entry, dictId, hwnormlist, altlist, dict_lbody):
    """Process a single entry and return output lines."""
    l = entry[0]
    entry_lines = entry[1]
    
    meta = parseheadline(entry_lines[0])
    key1 = meta['k1']
    pc = meta['pc']
    
    if l in altlist:
        althws = altlist[l]
    else:
        althws = []
    if (key1, dictId.upper()) in hwnormlist:
        alts = hwnormlist[(key1, dictId.upper())]
        possibleheadings = [key1]
        for a in alts:
            if a != key1 and a not in possibleheadings:
                possibleheadings.append(a)
    else:
        possibleheadings = [key1]
    seen = set(possibleheadings)
    for a in althws:
        if a not in seen:
            possibleheadings.append(a)
            seen.add(a)
    if dictId not in ['ae', 'mwe', 'bor']:
        scheme_map = SchemeMap(SCHEMES['slp1'], SCHEMES['devanagari'])
        k1s = '|'.join([transliterate(head, scheme_map=scheme_map) for head in possibleheadings])
    else:
        k1s = '|'.join(possibleheadings)
    
    result = k1s + '\n'
    
    for lin in entry_lines:
        if lin.startswith('<L>'):
            pass
        elif lin.startswith('<LEND>'):
            pass
        else:
            if dictId in params.regs:
                for (a, b) in params.regs[dictId]:
                    lin = re.sub(a, b, lin)
            lin = lin.replace('¦', '')
            result += lin + '\n'
    
    while '{{Lbody=' in result:
        match = re.search(r'\{\{Lbody=(.*?)\}\}', result)
        if not match:
            break
        ref_l = match.group(1)
        if ref_l in dict_lbody:
            result = result.replace(match.group(0), dict_lbody[ref_l])
        else:
            print(f"Warning: Lbody reference {ref_l} not found for L={l}")
            break
    
    result = re.sub(r'(\W)oM(\W)', r'\g<1>ॐ\g<2>', result)
    result = utils.devaconvert(result, dictId)
    result = re.sub('<sup>([0-9]+)</sup>', r'^\g<1>', result)
    result = re.sub('<.*?>', '', result)
    result = re.sub(r'\[Page([^\]]+?)(?:\+([^\]]*))?\]', lambda m: f'[<a href="https://dub.sh/cslp?dict={dictId.upper()}&page={m.group(1)}" target="_blank">Page{m.group(1)}{"+" + m.group(2) if m.group(2) else ""}</a>]', result)
    result = re.sub('[ ]+', ' ', result)
    linkurl = utils.scanlink(dictId, pc)
    result += '<a href="' + linkurl + '" target="_blank">PDF</a>\n'
    correctionurl = utils.correctionlink(dictId, l)
    result += '<a href="' + correctionurl + '" target="_blank">Correction</a>\n'
    result = re.sub('[ \t]*\n', '\n', result)
    result = re.sub('[\n]+', '\n', result)
    result = re.sub('\n$', '', result)
    result = re.sub(r'([(ं०१२३४५६७८९ ]+)꣡', r'\g<1>/', result)
    result = result.replace('{%', '<i>')
    result = result.replace('%}', '</i>')
    if dictId == 'ap':
        result = result.replace('∙²', '—')
        result = result.replace('∙³', '——')
    
    return result


def _worker_extract_lbody(chunk_entries, dictId):
    """Worker function for pass 1: extract lbody data from entries."""
    return {_extract_lbody(entry, dictId)[0]: _extract_lbody(entry, dictId)[1] 
            for entry in chunk_entries}


def _worker_process_chunk(chunk_with_index, dictId, hwnormlist, altlist, dict_lbody):
    """Worker function for pass 2: process entries with full dict_lbody."""
    chunk_idx, chunk_entries = chunk_with_index
    outputs = []
    for entry in chunk_entries:
        result = _process_entry(entry, dictId, hwnormlist, altlist, dict_lbody)
        outputs.append(result)
    return (chunk_idx, outputs)


def main(dictId, production):
    inputfile = os.path.join('..', 'csl-orig', 'v02', dictId, dictId + '.txt')
    fin = open(inputfile, 'r', encoding='utf-8')
    if production == '0':
        outputfile = os.path.join('output', dictId + '.babylon')
    elif production == '1':
        outputfile = os.path.join('production', dictId + '.babylon')
    fout = open(outputfile, 'w', encoding='utf-8')
    fout.write('\n#bookname=' + dictdata[dictId][0] + ' (' + dictdata[dictId][1] + ')\n')
    fout.write('#stripmethod=keep\n#sametypesequence=h\n')
    current_date = datetime.date.today()
    fout.write('#description=Data from https://www.sanskrit-lexicon.uni-koeln.de/ as on ' + str(current_date) + '\n\n')
    
    t0 = time.time()
    log("Reading hwnorm1.", t0)
    hwnormlist = utils.readhwnorm1c()
    log("Reading hwextra.", t0)
    altlist = utils.read_hwextra(dictId)
    
    log("Reading input file.", t0)
    data = fin.read()
    lins = data.split('\n')
    fin.close()
    
    t1 = time.time()
    log("Splitting into entries.", t1)
    entries = split_into_entries(lins)
    total_entries = len(entries)
    log(f"Total entries: {total_entries}", t1)
    
    num_cores = multiprocessing.cpu_count()
    log(f"Using {num_cores} cores.", t1)
    
    log("Partitioning entries.", t1)
    chunks = partition_entries(entries, num_cores)
    indexed_chunks = list(enumerate(chunks))
    
    t2 = time.time()
    log("Pass 1: Extracting Lbody data (parallel).", t2)
    with multiprocessing.Pool(processes=num_cores) as pool:
        worker_fn = partial(_worker_extract_lbody, dictId=dictId)
        partial_lbodies = pool.map(worker_fn, chunks)
    
    dict_lbody = {}
    for p in partial_lbodies:
        dict_lbody.update(p)
    log(f"Collected {len(dict_lbody)} Lbody entries.", t2)
    
    t3 = time.time()
    log("Pass 2: Processing entries (parallel).", t3)
    with multiprocessing.Pool(processes=num_cores) as pool:
        worker_fn = partial(_worker_process_chunk, dictId=dictId, 
                          hwnormlist=hwnormlist, altlist=altlist, dict_lbody=dict_lbody)
        results = pool.map(worker_fn, indexed_chunks)
    
    t4 = time.time()
    log("Sorting and writing output.", t4)
    results.sort(key=lambda x: x[0])
    
    for _, outputs in results:
        for result in outputs:
            if production == '1':
                parts = result.split('\n', 1)
                headword = parts[0]
                definition = parts[1].replace('\n', '<BR>') if len(parts) > 1 else ''
                fout.write(headword + '\n')
                fout.write(definition)
            else:
                fout.write(result)
            fout.write('\n\n')
    
    fout.close()
    log(f"Done. Total time: {time.time() - t0:.2f}s", t0)


if __name__ == "__main__":
    dictId = sys.argv[1]
    production = sys.argv[2]
    main(dictId, production)
