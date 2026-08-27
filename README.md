# python-xiso-repacker

[![PyPI - Version](https://img.shields.io/pypi/v/python-xiso-repacker.svg)](https://pypi.org/project/python-xiso-repacker)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/python-xiso-repacker.svg)](https://pypi.org/project/python-xiso-repacker)

-----

## Purpose

A simple tool to reconfigure xiso files used by various test programs for the
original Microsoft Xbox, suitable for use in automated testing.

## Installation

```console
pip install python-xiso-repacker
```

## Usage

```console
python -m python_xiso_repacker -h
```

### Replace a file inside an ISO

To replace a file `path/in/iso/config.json` inside `game.iso` with `new_config.json` and save to `game-updated.iso`:

```console
python -m python_xiso_repacker game.iso path/in/iso/config.json --replace new_config.json -o game-updated.iso
```

### Extract a file from an ISO

To extract `path/in/iso/default.xbe` from `game.iso` and save it to `extracted_default.xbe`:

```console
python -m python_xiso_repacker game.iso path/in/iso/default.xbe --extract extracted_default.xbe
```

### Python Library Usage

```python
from python_xiso_repacker import ensure_extract_xiso, extract_file, replace_file

# Automatically finds or downloads extract-xiso
extract_xiso = ensure_extract_xiso()

# Replace a file inside an ISO
replace_file("game.iso", "output.iso", "path/in/iso/config.json", "new_config.json", extract_xiso)

# Extract a file from an ISO
extract_file("game.iso", "path/in/iso/config.json", "extracted_config.json", extract_xiso)
```


## License

`python-xiso-repacker` is distributed under the terms of
the [MIT](https://spdx.org/licenses/MIT.html) license.
