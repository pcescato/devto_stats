#!/usr/bin/env python3
import sys
import html

# --- paramètres ajustables ---
WIDTH = 920
LINE_HEIGHT = 20
FONT_SIZE = 14
PADDING_X = 20
PADDING_Y = 30
BG_COLOR = "#0f111a"
FG_COLOR = "#c9d1d9"
ACCENT_COLOR = "#ff5555"
FONT_FAMILY = "JetBrains Mono, Menlo, Consolas, monospace"

# --- lecture stdin ---
lines = [line.rstrip("\n") for line in sys.stdin]
height = PADDING_Y * 2 + LINE_HEIGHT * len(lines)

def classify(line: str) -> str:
    """Coloration très simple, améliorable plus tard"""
    if line.startswith("📊") or line.startswith("📝"):
        return ACCENT_COLOR
    if line.strip().endswith(":"):
        return ACCENT_COLOR
    return FG_COLOR

# --- SVG ---
print(f'''<svg xmlns="http://www.w3.org/2000/svg"
     width="{WIDTH}"
     height="{height}"
     viewBox="0 0 {WIDTH} {height}">
  <style>
    text {{
      font-family: {FONT_FAMILY};
      font-size: {FONT_SIZE}px;
      white-space: pre;
    }}
  </style>

  <rect x="0" y="0" width="100%" height="100%" fill="{BG_COLOR}"/>
''')

y = PADDING_Y
for line in lines:
    color = classify(line)
    escaped = html.escape(line)
    print(
        f'  <text x="{PADDING_X}" y="{y}" fill="{color}">{escaped}</text>'
    )
    y += LINE_HEIGHT

print("</svg>")

