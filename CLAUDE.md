# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**cologne-stardict** converts the Cologne Digital Sanskrit Lexicon (CDSL) XML dictionaries into Babylon/StarDict format for use in offline dictionary applications (GoldenDict, StarDict, etc.).

The pipeline reads XML files from the local `csl-orig` sibling repo and headword normalization data from `hwnorm1`, then produces `.babylon` files that can be compiled into StarDict format.

Assumed local directory layout:
```
cologne/
  csl-orig/           ← source XML files per dictionary
  cologne-stardict/   ← this repo
  hwnorm1/            ← headword normalization tables
```

## Architecture

| File/Directory | Purpose |
|---|---|
| `redo.sh` | Main orchestration: pulls latest hwnorm1 + csl-orig, then runs all dictionaries |
| `make_babylon.py` | Converts a single dictionary XML → `.babylon` format |
| `make_babylon_synonymic.py` | Variant for synonymic dictionaries (ABCH, ACPH, ACSJ) |
| `params.py` | Per-dictionary regex transformations for XML → Babylon display formatting |
| `dictdata.py` | Dictionary metadata (names, filenames, language pairs) |
| `parseheadline.py` | Parses XML headline elements into Babylon entry headers |
| `fast_converter.py` | Optimized XML parsing for large dictionaries (MW) |
| `utils.py` | Shared utilities (encoding, HTML stripping) |
| `input/` | Input files: `hwnorm1c.txt` (copied from hwnorm1 during redo) |
| `output/` | Generated `.babylon` files (one per dictionary) |
| `production/` | Validated production-ready StarDict packages |
| `add_endline.py` | Post-processes babylon files to add required end-of-entry markers |
| `move_to_stardict.sh` | Moves babylon files to StarDict compilation directory |
| `copy_licence.sh` | Copies license files into each StarDict package |

### Dictionary list

Standard dictionaries (processed by `make_babylon.py`):
`acc ae ap ap90 armh ben bhs bop bor bur cae ccs fri gra gst ieg inm krm lan lrv mci md mw mw72 mwe pd pe pgn pui pw pwg sch shs skd snp stc vcp vei wil yat`

Synonymic dictionaries (processed by `make_babylon_synonymic.py`):
`abch acph acsj`

## Common Commands

### Full rebuild of all dictionaries
```bash
sh redo.sh
# With optional target dir argument:
sh redo.sh <target_dir>
```

### Process a single dictionary
```bash
python3 make_babylon.py <dict_code>
# e.g.: python3 make_babylon.py mw
```

### Process a synonymic dictionary
```bash
python3 make_babylon_synonymic.py <dict_code>
# e.g.: python3 make_babylon_synonymic.py abch
```

## Dependencies

- **Python 3**
- **csl-orig** sibling repo — XML source files at `../csl-orig/v02/<dict>/<dict>.xml`
- **hwnorm1** sibling repo — `../hwnorm1/sanhw1/hwnorm1c.txt` (headword normalization)
