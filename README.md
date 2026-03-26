# VoxelText

Convert plain text into Minecraft schematics using a built-in pixel font. Paste your sign, banner, or build label directly into the world with **Litematica** or **WorldEdit**.

---

## Features

- Supports uppercase & lowercase letters, numbers, and common symbols
- Configurable block type, character gap, and line gap
- Outputs a `.schem` file compatible with Litematica and WorldEdit
- Multi-line text support
- Lightweight — no external dependencies beyond `mcschematic`

---

## Requirements

- Python 3.8+
- [mcschematic](https://github.com/Sloimayyy/mcschematic)

```bash
pip install mcschematic
```

---

## Usage

Create an `input.txt` file with the text you want to generate, then run:

```bash
python main.py
```

Or pass a custom file:

```bash
python main.py mytext.txt
```

### All Options

```
usage: main.py [-h] [-o NAME] [-b BLOCK] [-g N] [-l N] [--version VER] [--list-chars] [-v] [input]

positional arguments:
  input                 Path to input text file (default: input.txt)

options:
  -h, --help            Show this help message and exit
  -o, --output NAME     Output schematic name without extension (default: output)
  -b, --block BLOCK     Minecraft block ID for filled pixels (default: minecraft:black_wool)
  -g, --char-gap N      Air gap in blocks between characters (default: 1)
  -l, --line-gap N      Air gap in blocks between lines (default: 1)
  --version VER         Minecraft version for schematic format (default: JE_1_18_2)
  --list-chars          Print all supported characters and exit
  -v, --version-info    Print tool version and exit
```

### Examples

```bash
# Basic usage with defaults
python main.py input.txt

# Custom output name
python main.py input.txt -o my_sign

# Use gold blocks with wider spacing
python main.py input.txt -b minecraft:gold_block -g 2 -l 2

# Target a specific Minecraft version
python main.py input.txt --version JE_1_20_1

# See all supported characters
python main.py --list-chars
```

---

## Supported Characters

| Category   | Characters                                      |
|------------|-------------------------------------------------|
| Uppercase  | A–Z                                             |
| Lowercase  | a–z                                             |
| Numbers    | 0–9                                             |
| Brackets   | `( ) [ ] { }`                                   |
| Math       | `+ - * / ^ < > ! ÷ × ⊕`                        |
| Punctuation| `. , ?`                                         |
| Space      | ` `                                             |

Run `python main.py --list-chars` for the full list.

---

## Using the Output In-Game

**Litematica**
1. Copy `output.schem` into your Litematica schematics folder
2. Load it via the Litematica menu and place as normal

**WorldEdit**
1. Copy `output.schem` into your WorldEdit schematics folder
2. Run `//schem load output` then `//paste`

---

## Supported Minecraft Versions

Any version supported by the `mcschematic` library. Common options:

| Flag          | Version         |
|---------------|-----------------|
| `JE_1_18_2`   | 1.18.2 (default)|
| `JE_1_19_4`   | 1.19.4          |
| `JE_1_20_1`   | 1.20.1          |
| `JE_1_21`     | 1.21            |

---

## License

[MIT](LICENSE)

---

## Contributing

Pull requests are welcome. To add new characters, edit `font.py` and follow the existing 5-row bitmap format. Each character is a flat list of `0`s and `1`s, read left-to-right, top-to-bottom.

```python
"&": [
    0, 1, 1,
    1, 0, 0,
    0, 1, 1,
    1, 0, 1,
    0, 1, 1
]
```

---

*Built with Python & [mcschematic](https://github.com/Sloimayyy/mcschematic)*
