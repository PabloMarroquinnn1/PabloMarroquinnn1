"""
Genera un SVG pixel-art animado del avatar de GitHub.
El avatar se "dibuja" línea por línea con un efecto de escaneo,
y al final aparece un brillo sutil.

Uso:  python scripts/pixel_avatar.py <usuario_github> <salida.svg>
"""

import sys
import io
import urllib.request

from PIL import Image

GRID = 44          # resolución del pixel-art (44x44 píxeles)
CELL = 10          # tamaño de cada "píxel" en el SVG
GAP = 1            # separación entre píxeles
ROW_DELAY = 0.06   # segundos entre cada línea dibujada
SCAN_COLOR = "#00BFFF"  # color de la línea de escaneo (azul del perfil)


def fetch_avatar(username: str) -> Image.Image:
    url = f"https://github.com/{username}.png?size=256"
    req = urllib.request.Request(url, headers={"User-Agent": "pixel-avatar"})
    with urllib.request.urlopen(req) as r:
        data = r.read()
    return Image.open(io.BytesIO(data)).convert("RGBA")


def to_hex(px) -> str:
    return "#{:02x}{:02x}{:02x}".format(px[0], px[1], px[2])


def build_svg(img: Image.Image) -> str:
    img = img.resize((GRID, GRID), Image.LANCZOS)
    size = GRID * (CELL + GAP) - GAP

    rows_svg = []
    for y in range(GRID):
        delay = round(y * ROW_DELAY, 3)
        rects = []
        x = 0
        while x < GRID:
            px = img.getpixel((x, y))
            if px[3] < 20:  # transparente
                x += 1
                continue
            # comprimir corridas horizontales del mismo color
            run = 1
            color = to_hex(px)
            while x + run < GRID:
                nxt = img.getpixel((x + run, y))
                if nxt[3] < 20 or to_hex(nxt) != color:
                    break
                run += 1
            rx = x * (CELL + GAP)
            w = run * (CELL + GAP) - GAP
            rects.append(
                f'<rect x="{rx}" y="0" width="{w}" height="{CELL}" '
                f'rx="2" fill="{color}"/>'
            )
            x += run
        ry = y * (CELL + GAP)
        rows_svg.append(
            f'<g transform="translate(0,{ry})">'
            f'<g class="row" style="animation-delay:{delay}s">{"".join(rects)}</g>'
            f"</g>"
        )

    total = round(GRID * ROW_DELAY + 0.4, 2)

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="-6 -6 {size + 12} {size + 12}" width="{size + 12}" height="{size + 12}">
<style>
.row {{ opacity: 0; transform: scaleY(0.2); transform-origin: center;
  animation: draw 0.35s ease-out forwards; }}
@keyframes draw {{
  0%   {{ opacity: 0; transform: scaleY(0.2); }}
  100% {{ opacity: 1; transform: scaleY(1); }}
}}
.scan {{
  animation: scan {total}s linear forwards;
}}
@keyframes scan {{
  0%   {{ transform: translateY(0); opacity: 1; }}
  95%  {{ opacity: 1; }}
  100% {{ transform: translateY({size}px); opacity: 0; }}
}}
.frame {{
  fill: none; stroke: {SCAN_COLOR}; stroke-width: 2; rx: 8;
  stroke-dasharray: {size * 4}; stroke-dashoffset: {size * 4};
  animation: trace 1.2s ease-in-out {total}s forwards;
}}
@keyframes trace {{ to {{ stroke-dashoffset: 0; }} }}
</style>
<rect class="frame" x="-5" y="-5" width="{size + 10}" height="{size + 10}" rx="10"/>
{"".join(rows_svg)}
<rect class="scan" x="-5" y="-2" width="{size + 10}" height="3" fill="{SCAN_COLOR}" opacity="0.9"/>
</svg>
"""


def main():
    username = sys.argv[1] if len(sys.argv) > 1 else "PabloMarroquinnn1"
    out = sys.argv[2] if len(sys.argv) > 2 else "pixel-avatar.svg"
    img = fetch_avatar(username)
    svg = build_svg(img)
    with open(out, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"OK -> {out} ({len(svg) // 1024} KB)")


if __name__ == "__main__":
    main()
