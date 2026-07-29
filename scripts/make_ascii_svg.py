"""
make_ascii_svg.py — Convert source-prepped.png into a monochrome ASCII art SVG
with a row-by-row typing animation (SMIL).

Each row is clipped by a rect that wipes left-to-right, staggered top to bottom.
A small cursor block rides the wipe edge. Plays once, then freezes.
"""
from PIL import Image
from pathlib import Path
import sys

# Density ramp: bright (sparse) → dark (dense)
RAMP = " .`:-=+*cs#%@"

# Output dimensions
COLS = 100
ROWS = 53

# SVG styling
FONT_SIZE = 10
CHAR_W = 6.02   # monospace char width at 10px
CHAR_H = 11     # line height
FG_COLOR = "#b0b8c4"  # single light-gray fill

# Animation timing
ROW_DELAY = 0.06  # seconds between each row starting
WIPE_DUR  = 0.7   # seconds for each row to fully reveal


def brightness_to_char(b: float) -> str:
    """Map a 0-255 brightness value to an ASCII glyph."""
    idx = int(b / 255 * (len(RAMP) - 1))
    idx = max(0, min(idx, len(RAMP) - 1))
    return RAMP[idx]


def main():
    root = Path(__file__).resolve().parent.parent
    src = root / "source-prepped.png"
    if not src.exists():
        print(f"Error: {src} not found. Run prep_photo.py first.")
        sys.exit(1)

    print(f"Loading {src}...")
    img = Image.open(src).convert("L")
    img = img.resize((COLS, ROWS), resample=Image.LANCZOS)
    px = img.load()

    # Build character grid
    grid = []
    for y in range(ROWS):
        row = ""
        for x in range(COLS):
            row += brightness_to_char(px[x, y])
        grid.append(row)

    svg_w = COLS * CHAR_W + 20
    svg_h = ROWS * CHAR_H + 20

    lines = []
    lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{svg_w:.0f}" height="{svg_h:.0f}" viewBox="0 0 {svg_w:.0f} {svg_h:.0f}">')
    lines.append('  <defs>')

    # One clipPath per row
    for r in range(ROWS):
        clip_id = f"clip-r{r}"
        delay = r * ROW_DELAY
        rect_id = f"wr{r}"
        lines.append(f'    <clipPath id="{clip_id}">')
        lines.append(f'      <rect id="{rect_id}" x="0" y="0" width="0" height="{CHAR_H + 2}">')
        lines.append(f'        <animate attributeName="width" from="0" to="{svg_w:.0f}" dur="{WIPE_DUR}s" begin="{delay:.2f}s" fill="freeze"/>')
        lines.append(f'      </rect>')
        lines.append(f'    </clipPath>')

    lines.append('  </defs>')

    # Background
    lines.append(f'  <rect width="{svg_w:.0f}" height="{svg_h:.0f}" fill="#0d1117"/>')

    # ASCII rows
    lines.append(f'  <g font-family="Consolas,\'Courier New\',monospace" font-size="{FONT_SIZE}" fill="{FG_COLOR}">')
    for r, row_text in enumerate(grid):
        ty = 10 + r * CHAR_H + FONT_SIZE  # baseline
        clip_id = f"clip-r{r}"
        # Escape XML special chars
        escaped = row_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
        lines.append(f'    <g clip-path="url(#{clip_id})" transform="translate(10, {10 + r * CHAR_H})">')
        lines.append(f'      <text y="{FONT_SIZE}" xml:space="preserve">{escaped}</text>')
        # Cursor block that rides the wipe edge
        delay = r * ROW_DELAY
        cursor_start_x = 0
        cursor_end_x = svg_w
        lines.append(f'      <rect y="0" width="6" height="{CHAR_H}" fill="#58a6ff" opacity="0.8">')
        lines.append(f'        <animate attributeName="x" from="{cursor_start_x}" to="{cursor_end_x:.0f}" dur="{WIPE_DUR}s" begin="{delay:.2f}s" fill="freeze"/>')
        lines.append(f'        <animate attributeName="opacity" from="0.8" to="0" dur="0.01s" begin="{delay + WIPE_DUR:.2f}s" fill="freeze"/>')
        lines.append(f'      </rect>')
        lines.append(f'    </g>')

    lines.append('  </g>')
    lines.append('</svg>')

    out = root / "alok-ascii.svg"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved {out} ({svg_w:.0f}x{svg_h:.0f})")


if __name__ == "__main__":
    main()
