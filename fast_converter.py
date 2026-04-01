import sys
import time
import os
import re

_re_k = re.compile(r'ं(\s*[क-ङ])')
_re_c = re.compile(r'ं(\s*[च-ञ])')
_re_t = re.compile(r'ं(\s*[त-न])')
_re_T = re.compile(r'ं(\s*[ट-ण])')
_re_p = re.compile(r'ं(\s*[प-म])')
_re_e = re.compile(r'ं(?=\||$)')

def get_non_anusvaara_variant(in_str):
    out = _re_k.sub(r'ङ्\1', in_str)
    out = _re_c.sub(r'ञ्\1', out)
    out = _re_t.sub(r'न्\1', out)
    out = _re_T.sub(r'ण्\1', out)
    out = _re_p.sub(r'म्\1', out)
    out = _re_e.sub(r'म्', out)
    return out

def convert_babylon(input_path, output_path):
    start_time = time.time()
    
    # Load transliteration
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

    new_lines = []
    
    prev_empty = False
    
    # Aliases for fast loop
    _cache = {}
    def to_optitrans(x):
        if x not in _cache:
            _cache[x] = sanscript.transliterate(x, sanscript.DEVANAGARI, sanscript.OPTITRANS)
        return _cache[x]

    _cache_itrans = {}
    def to_itrans(x):
        if x not in _cache_itrans:
            _cache_itrans[x] = sanscript.transliterate(x, sanscript.DEVANAGARI, sanscript.ITRANS)
        return _cache_itrans[x]
    
    process_start = time.time()
    
    for line in lines:
        if line == '\n' or line == '\r\n':
            prev_empty = True
            new_lines.append(line)
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
                    
                # Convert the entire line string at once to save overhead!
                o_line = to_optitrans(line_str)
                i_line = to_itrans(line_str)
                n_line = get_non_anusvaara_variant(line_str)
                
                # Combine optitrans, itrans, non_anusvaara variant, and original; keep unique, preserve order
                all_members = o_line.split('|') + i_line.split('|') + n_line.split('|') + line_str.split('|')
                unique_members = list(dict.fromkeys(all_members))
                
                new_line = '|'.join(unique_members) + line_endl
                new_lines.append(new_line)
                continue
                
        new_lines.append(line)
        prev_empty = False

    process_time = time.time()
    print(f"Processing completed in {process_time - process_start:.4f} seconds.")

    # Write output
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
        
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
