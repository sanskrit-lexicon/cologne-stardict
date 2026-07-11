# cologne-stardict

_Created: 04-04-2017 · Last updated: 11-07-2026_

Scripts that convert the [Cologne Digital Sanskrit Lexicon (CDSL)](https://www.sanskrit-lexicon.uni-koeln.de/) dictionary text into [Babylon](https://en.wikipedia.org/wiki/Babylon_(software))-format source files (`*.babylon`), which are then compiled into [StarDict](https://en.wikipedia.org/wiki/StarDict) dictionaries and published in the [indic-dict/stardict-sanskrit](https://github.com/indic-dict/stardict-sanskrit) collection.

This is a **converter / tooling** repository in the [sanskrit-lexicon](https://github.com/sanskrit-lexicon) org — not a dictionary itself. It transforms lexica maintained upstream; it does not author their content.

## Data flow

```
csl-orig (dictionary display text)  ─┐
hwnorm1  (headword normalization) ───┼─▶  make_babylon*.py  ─▶  output/*.babylon
input/hwnorm1c.txt                   ─┘         │                production/*.babylon
                                                ▼
                                     move_to_stardict.sh
                                                │
                                                ▼
                          indic-dict/stardict-sanskrit  ─▶  StarDict / GoldenDict apps
```

- **Inputs** — dictionary source text from [csl-orig](https://github.com/sanskrit-lexicon/csl-orig) and the headword-normalization table [`input/hwnorm1c.txt`](https://github.com/sanskrit-lexicon/cologne-stardict/blob/main/input/hwnorm1c.txt), copied from the [hwnorm1](https://github.com/sanskrit-lexicon/hwnorm1) repo.
- **Outputs** — [`output/`](https://github.com/sanskrit-lexicon/cologne-stardict/tree/main/output) holds development `*.babylon` files (viewing line breaks); `production/` holds production builds (HTML-style line breaks). License headers land in `output/licenses/`.
- **Consumer** — [`move_to_stardict.sh`](https://github.com/sanskrit-lexicon/cologne-stardict/blob/main/move_to_stardict.sh) deploys each production `*.babylon` into the sibling `indic-dict/stardict-sanskrit` working tree, grouped by head/entry language (`sa-head/en-entries`, `german-entries`, `french-entries`, `sa-entries`, `en-head`, …).

The `main` branch is regenerated automatically after upstream `csl-orig` updates (see the commit history — e.g. "Regeneration after csl-orig commit …").

## Dictionaries

40+ CDSL dictionaries are registered in [`dictdata.py`](https://github.com/sanskrit-lexicon/cologne-stardict/blob/main/dictdata.py), each mapped to its published slug and language pair (e.g. `ap` → `apte-1957` / `sa-en`, `pwg` → Böhtlingk-Roth *Großes Petersburger Wörterbuch* / `sa-de`, `gra` → Grassmann / `sa-de`). Standard dictionaries are built with `make_babylon.py`; the four synonymic/thesaurus lexica (`abch`, `acph`, `acsj`, `nmmb`) are built with `make_babylon_synonymic.py`.

## Key scripts

| File | Role |
|---|---|
| [`redo.sh`](https://github.com/sanskrit-lexicon/cologne-stardict/blob/main/redo.sh) | Full-regeneration orchestrator: pull `hwnorm1` + `csl-orig`, refresh `input/hwnorm1c.txt`, run the converter over every registered dictionary. |
| [`make_babylon.py`](https://github.com/sanskrit-lexicon/cologne-stardict/blob/main/make_babylon.py) | Main converter (CDSL text → Babylon). Usage: `python3 make_babylon.py <dictId> <0|1>` — `0` = viewing (`\n` breaks), `1` = production (HTML-like breaks). |
| [`make_babylon_synonymic.py`](https://github.com/sanskrit-lexicon/cologne-stardict/blob/main/make_babylon_synonymic.py) | Converter variant for synonymic / thesaurus dictionaries. |
| [`dictdata.py`](https://github.com/sanskrit-lexicon/cologne-stardict/blob/main/dictdata.py) | Registry mapping each dictionary code → `[slug, language-pair]`. |
| [`params.py`](https://github.com/sanskrit-lexicon/cologne-stardict/blob/main/params.py) | Per-dictionary regex cleanup rules applied during conversion. |
| [`fast_converter.py`](https://github.com/sanskrit-lexicon/cologne-stardict/blob/main/fast_converter.py) | Optimized Devanagari transliteration (anusvāra → nasal-consonant variants). |
| [`parseheadline.py`](https://github.com/sanskrit-lexicon/cologne-stardict/blob/main/parseheadline.py) · [`utils.py`](https://github.com/sanskrit-lexicon/cologne-stardict/blob/main/utils.py) · [`add_endline.py`](https://github.com/sanskrit-lexicon/cologne-stardict/blob/main/add_endline.py) | Parsing and formatting helpers. |
| [`copy_licence.sh`](https://github.com/sanskrit-lexicon/cologne-stardict/blob/main/copy_licence.sh) | Copies each dictionary's license header from the Cologne `pywork` build into `output/licenses/` and `production/licenses/`. |
| [`move_to_stardict.sh`](https://github.com/sanskrit-lexicon/cologne-stardict/blob/main/move_to_stardict.sh) | Deploys production `*.babylon` files into the `indic-dict/stardict-sanskrit` tree. |

`make_babylon_from_xml_unused.py` is a retired XML-based variant, kept for reference only.

## Requirements

- Python 3
- [`indic_transliteration`](https://pypi.org/project/indic-transliteration/) (the `sanscript` module)
- the [`regex`](https://pypi.org/project/regex/) module

The regeneration scripts assume sibling clones of `csl-orig`, `hwnorm1`, and `indic-dict/stardict-sanskrit` next to this repository.

## GitHub issue conventions

This repository follows the [Cologne tooling-repo taxonomy](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/runbook/cologne-tooling-runbook.md) — exactly one **type** label (bug, feature, enhancement, performance, tech-debt, security, documentation, infrastructure, question), one **severity** (trivial, minor, major, critical), and one milestone; tracked in the org [Tooling Roadmap](https://github.com/orgs/sanskrit-lexicon/projects/9). Full definitions are in [`CLAUDE.md`](https://github.com/sanskrit-lexicon/cologne-stardict/blob/main/CLAUDE.md). See the [issue tracker](https://github.com/sanskrit-lexicon/cologne-stardict/issues) for current open items.

## License

MIT — see [`LICENSE`](https://github.com/sanskrit-lexicon/cologne-stardict/blob/main/LICENSE) (© 2017 Sanskrit Lexicon). The underlying dictionary content carries the license of each source dictionary (headers preserved under `output/licenses/`).

_Dr. Mārcis Gasūns_
