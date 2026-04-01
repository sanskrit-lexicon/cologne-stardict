import sys
import time
import os
import re
import regex

_re_k = re.compile(r'ं(\s*[क-ङ])')
_re_c = re.compile(r'ं(\s*[च-ञ])')
_re_t = re.compile(r'ं(\s*[त-न])')
_re_T = re.compile(r'ं(\s*[ट-ण])')
_re_p = re.compile(r'ं(\s*[प-म])')
_re_e = re.compile(r'ं(?=\||\n|$)')

def get_non_anusvaara_variant(in_str):
    out = _re_k.sub(r'ङ्\1', in_str)
    out = _re_c.sub(r'ञ्\1', out)
    out = _re_t.sub(r'न्\1', out)
    out = _re_T.sub(r'ण्\1', out)
    out = _re_p.sub(r'म्\1', out)
    out = _re_e.sub(r'म्', out)
    return out

def make_fast_transliterate(to_scheme_name):
    from indic_transliteration import sanscript
    scheme_map = sanscript._get_scheme_map(sanscript.DEVANAGARI, to_scheme_name)
    
    vowel_marks = scheme_map.vowel_marks
    virama = scheme_map.virama
    consonants = scheme_map.consonants
    non_marks_viraama = scheme_map.non_marks_viraama
    to_roman = scheme_map.to_scheme.is_roman
    max_key_length = scheme_map.max_key_length_from_scheme
    virama_value = next(iter(virama.values())) if virama else ''
    
    compiled_pattern = None
    if to_roman and len(scheme_map.accents) > 0:
        pattern = "([%s])([%s])" % ("".join(scheme_map.from_scheme['yogavaahas']), "".join(scheme_map.accents.keys()))
        compiled_pattern = regex.compile(pattern)
        
    def _transliterate(data):
        if not data: return data
        data = scheme_map.from_scheme.unapply_shortcuts(data_in=data)
        
        if compiled_pattern:
            data = compiled_pattern.sub(r"\2\1", data)
            
        buf = []
        i = 0
        to_roman_had_consonant = False
        append = buf.append
        length = len(data)
        
        while i < length:
            token = data[i:i + max_key_length]
            found = False
            
            while token:
                if len(token) == 1:
                    if token in vowel_marks:
                        append(vowel_marks[token])
                        found = True
                    elif token in virama:
                        append(virama[token])
                        found = True
                    else:
                        if to_roman_had_consonant:
                            append('a')
                        append(non_marks_viraama.get(token, token))
                        found = True
                else:
                    if token in non_marks_viraama:
                        if to_roman_had_consonant:
                            append('a')
                        append(non_marks_viraama.get(token))
                        found = True

                if found:
                    to_roman_had_consonant = to_roman and token in consonants
                    i += len(token)
                    break        
                else:
                    token = token[:-1]

            if not found:
                if to_roman_had_consonant:
                    append(virama_value)
                append(data[i])
                to_roman_had_consonant = False
                i += 1

        if to_roman_had_consonant:
            append('a')
            
        res = ''.join(buf)
        return scheme_map.to_scheme.apply_shortcuts(data_in=res)
        
    # Apply our memoization cache wrapping the compiler
    _cache = {}
    def cached_transliterate(x):
        if x not in _cache:
            _cache[x] = _transliterate(x)
        return _cache[x]
        
    return cached_transliterate

import multiprocessing
from concurrent.futures import ProcessPoolExecutor

_worker_to_optitrans = None
_worker_to_itrans = None
_worker_to_iast = None

def _init_worker():
    global _worker_to_optitrans, _worker_to_itrans, _worker_to_iast
    from indic_transliteration import sanscript
    _worker_to_optitrans = make_fast_transliterate(sanscript.OPTITRANS)
    _worker_to_itrans = make_fast_transliterate(sanscript.ITRANS)
    _worker_to_iast = make_fast_transliterate(sanscript.IAST)

def _process_chunk(chunk):
    results = []
    for orig_i, line_str, line_endl in chunk:
        o_line = _worker_to_optitrans(line_str)
        i_line = _worker_to_itrans(line_str)
        a_line = _worker_to_iast(line_str)
        n_line = get_non_anusvaara_variant(line_str)
        
        all_members = i_line.split('|') + o_line.split('|') + a_line.split('|') + n_line.split('|') + line_str.split('|')
        unique_members = list(dict.fromkeys(all_members))
        
        new_line = '|'.join(unique_members) + line_endl
        results.append((orig_i, new_line))
    return results

def convert_babylon(input_path, output_path):
    start_time = time.time()
    
    # Load transliteration check
    try:
        from indic_transliteration import sanscript
    except ImportError:
        print("Error: indic_transliteration not found. Run python in environment with the package.")
        return

    # Check if input exists
    if not os.path.exists(input_path):
        print(f"Error: {input_path} not found.")
        return

    print(f"Reading from {input_path}...")
    with open(input_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    read_time = time.time()
    print(f"File loaded in memory in {read_time - start_time:.4f} seconds.")

    prev_empty = False
    headwords_to_process = []
    
    process_start = time.time()
    
    for i, line in enumerate(lines):
        if line == '\n' or line == '\r\n':
            prev_empty = True
            continue
            
        if prev_empty:
            prev_empty = False
            if not line.startswith('#'):
                # Line ending extraction
                if line.endswith('\r\n'):
                    line_endl = '\r\n'
                    line_str = line[:-2]
                elif line.endswith('\n'):
                    line_endl = '\n'
                    line_str = line[:-1]
                else:
                    line_endl = ''
                    line_str = line
                    
                headwords_to_process.append((i, line_str, line_endl))
                continue
                
        prev_empty = False

    # Parallel Processing Segment
    workers = min(os.cpu_count() or 4, 8)  # Keep reasonable worker count
    if not headwords_to_process:
        chunk_size = 1
    else:
        chunk_size = max(1, len(headwords_to_process) // workers)
        
    chunks = [headwords_to_process[i:i + chunk_size] for i in range(0, len(headwords_to_process), chunk_size)]
    
    with ProcessPoolExecutor(max_workers=workers, initializer=_init_worker) as executor:
        for chunk_result in executor.map(_process_chunk, chunks):
            for orig_i, new_line in chunk_result:
                lines[orig_i] = new_line

    process_time = time.time()
    print(f"Processing completed in {process_time - process_start:.4f} seconds.")

    # Write output
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
        
    write_time = time.time()
    print(f"Output saved to {output_path} in {write_time - process_time:.4f} seconds.")
    print(f"Total loop time: {write_time - start_time:.4f} seconds.")

if __name__ == '__main__':
    # Default Paths
    input_file = "production/mw.babylon"
    output_file = "babylon_final/mw.babylon"
    
    if len(sys.argv) == 3:
        input_file = sys.argv[1]
        output_file = sys.argv[2]
        
    convert_babylon(input_file, output_file)
