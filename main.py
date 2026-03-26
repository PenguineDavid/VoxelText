import sys
import argparse
import mcschematic
from mcschematic import Version
from font import font

# ------------------------------
# Tool Info
# ------------------------------
TOOL_NAME    = "VoxelText © 2026 PenguineDavid All Rights Reserved"
TOOL_VERSION = "1.0.0"
GITHUB_URL   = "https://github.com/PenguineDavid/VoxelText"
LICENSE_URL  = "https://github.com/PenguineDavid/VoxelText/blob/main/LICENSE.md"

def print_banner():
    print("=" * 60)
    print(f"  {TOOL_NAME} v{TOOL_VERSION}")
    print(f"  GitHub  : {GITHUB_URL}")
    print(f"  License : {LICENSE_URL}")
    print("=" * 60)
    print()

# ------------------------------
# Argument Parsing
# ------------------------------
def parse_args():
    parser = argparse.ArgumentParser(
        prog="main.py",
        description=f"{TOOL_NAME} — Converts text into a Minecraft .schem file using a pixel font.",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python main.py input.txt\n"
            "  python main.py input.txt -o my_sign\n"
            "  python main.py input.txt -b minecraft:gold_block -g 2 -l 2\n"
            "  python main.py input.txt --block minecraft:stone --char-gap 1 --line-gap 2 --version JE_1_20_1\n"
        )
    )

    parser.add_argument(
        "input",
        nargs="?",
        default="input.txt",
        help="Path to the input text file (default: input.txt)"
    )
    parser.add_argument(
        "-o", "--output",
        default="output",
        metavar="NAME",
        help="Output schematic name without extension (default: output)"
    )
    parser.add_argument(
        "-b", "--block",
        default="minecraft:black_wool",
        metavar="BLOCK",
        help="Minecraft block ID to use for filled pixels\n(default: minecraft:black_wool)"
    )
    parser.add_argument(
        "-g", "--char-gap",
        type=int,
        default=1,
        metavar="N",
        help="Air gap in blocks between characters (default: 1)"
    )
    parser.add_argument(
        "-l", "--line-gap",
        type=int,
        default=1,
        metavar="N",
        help="Air gap in blocks between lines (default: 1)"
    )
    parser.add_argument(
        "--version",
        default="JE_1_18_2",
        metavar="VER",
        help=(
            "Minecraft version for the schematic format.\n"
            "Common options: JE_1_18_2, JE_1_19_4, JE_1_20_1, JE_1_21\n"
            "(default: JE_1_18_2)"
        )
    )
    parser.add_argument(
        "--list-chars",
        action="store_true",
        help="Print all supported characters and exit"
    )
    parser.add_argument(
        "-v", "--version-info",
        action="store_true",
        help="Print tool version and exit"
    )

    return parser.parse_args()

# ------------------------------
# Build a unified character map from the font dictionary
# ------------------------------
def build_char_map():
    char_map = {}
    char_map.update(font["letter"])
    char_map.update(font["numbers"])
    char_map.update(font["math"]["brackets"])
    char_map.update(font["math"]["operations"])
    char_map.update(font["punctuation"])
    char_map[' '] = [0] * 5  # space: 1 column wide, all air
    return char_map

# ------------------------------
# Main
# ------------------------------
def main():
    print_banner()
    args = parse_args()

    # Version flag
    if args.version_info:
        print(f"{TOOL_NAME} v{TOOL_VERSION}")
        sys.exit(0)

    char_map = build_char_map()

    # List supported characters
    if args.list_chars:
        print("Supported characters:")
        print("  Letters   :", " ".join(sorted(k for k in char_map if k.isalpha())))
        print("  Numbers   :", " ".join(sorted(k for k in char_map if k.isdigit())))
        print("  Symbols   :", " ".join(sorted(k for k in char_map if not k.isalnum())))
        sys.exit(0)

    # Resolve Minecraft version
    try:
        minecraft_version = Version[args.version]
    except KeyError:
        print(f"Error: Unknown version '{args.version}'.")
        print("Run with --help to see common version options.")
        sys.exit(1)

    GAP_BETWEEN_CHARS = args.char_gap
    GAP_BETWEEN_LINES = args.line_gap
    BLOCK_NAME        = args.block
    output_name       = args.output
    filename          = args.input

    print(f"  Input file  : {filename}")
    print(f"  Output name : {output_name}.schem")
    print(f"  Block       : {BLOCK_NAME}")
    print(f"  Char gap    : {GAP_BETWEEN_CHARS}")
    print(f"  Line gap    : {GAP_BETWEEN_LINES}")
    print(f"  MC version  : {minecraft_version.name} (DataVersion {minecraft_version.value})")
    print()

    # ------------------------------
    # Read input text file
    # ------------------------------
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            lines = [line.rstrip('\n') for line in f]
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        sys.exit(1)

    # ------------------------------
    # Process each line
    # ------------------------------
    line_data = []
    for line in lines:
        if not line:
            continue
        chars = []
        total_width = 0
        for ch in line:
            if ch in char_map:
                bitmap = char_map[ch]
                width = len(bitmap) // 5
                chars.append((total_width, bitmap, width))
                total_width += width + GAP_BETWEEN_CHARS
            else:
                print(f"  Warning: Character '{ch}' not found, skipping.")
        if chars:
            total_width -= GAP_BETWEEN_CHARS
            line_data.append((total_width, chars))

    if not line_data:
        print("Error: No printable characters found in input.")
        sys.exit(0)

    # ------------------------------
    # Debug: character placement
    # ------------------------------
    print("Character placement:")
    for line_idx, (line_width, chars) in enumerate(line_data):
        print(f"  Line {line_idx}: total width = {line_width} blocks, {len(chars)} characters")

    # ------------------------------
    # Calculate overall dimensions
    # ------------------------------
    max_line_width = max(w for w, _ in line_data)
    total_lines    = len(line_data)
    total_z        = total_lines * 5 + (total_lines - 1) * GAP_BETWEEN_LINES
    total_x        = max_line_width
    total_y        = 1

    print(f"\n  Schematic dimensions: {total_x}W x {total_y}H x {total_z}L blocks")

    # ------------------------------
    # Create the schematic and place blocks
    # ------------------------------
    schem = mcschematic.MCSchematic()
    block_count = 0
    min_x, max_x = float('inf'), float('-inf')
    min_z, max_z = float('inf'), float('-inf')

    for line_idx, (line_width, chars) in enumerate(line_data):
        line_z_start = line_idx * (5 + GAP_BETWEEN_LINES)
        for (char_x_start, bitmap, char_width) in chars:
            for row in range(5):
                z = line_z_start + row
                for col in range(char_width):
                    if bitmap[row * char_width + col] == 1:
                        x = char_x_start + col
                        schem.setBlock((x, 0, z), BLOCK_NAME)
                        block_count += 1
                        if x < min_x: min_x = x
                        if x > max_x: max_x = x
                        if z < min_z: min_z = z
                        if z > max_z: max_z = z

    print(f"  Blocks placed : {block_count}")
    print(f"  X range       : {min_x} → {max_x}")
    print(f"  Z range       : {min_z} → {max_z}")

    # ------------------------------
    # Save the schematic
    # ------------------------------
    schem.save(".", output_name, version=minecraft_version)

    print()
    print("=" * 60)
    print(f"  Saved: {output_name}.schem")
    print(f"  Compatible with Minecraft {minecraft_version.name}")
    print()
    print("  Usage in-game:")
    print("    • Litematica : load the .schem file directly")
    print("    • WorldEdit  : //schem load <name>  then  //paste")
    print()
    print(f"  {GITHUB_URL}")
    print("=" * 60)

if __name__ == "__main__":
    main()