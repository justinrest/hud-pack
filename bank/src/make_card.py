"""Draws the bank card item texture (16x16) and a 16x preview.

A plastic card seen flat, like vanilla's flat item icons: a navy body lit
from the top left (highlight rows and a soft diagonal sheen, shadow on the
bottom and right), a dark outline with rounded corners, a gold EMV chip
with contact lines, an embossed number row and a small gold Treasury seal.

    python make_card.py <out_png> [preview_png]
"""
import sys

from PIL import Image

OUTLINE = (24, 30, 52, 255)
EDGE_LIGHT = (112, 146, 214, 255)
BODY_LIGHT = (70, 104, 176, 255)
BODY = (50, 80, 148, 255)
BODY_DARK = (36, 60, 118, 255)
EDGE_DARK = (27, 44, 90, 255)
SHEEN = (84, 120, 194, 255)
CHIP_HI = (250, 228, 150, 255)
CHIP = (226, 186, 84, 255)
CHIP_LINE = (168, 124, 42, 255)
CHIP_EDGE = (120, 84, 28, 255)
DOT = (206, 218, 240, 255)
DOT_SHADOW = (30, 48, 98, 255)
SEAL = (232, 194, 92, 255)
SEAL_DARK = (160, 116, 38, 255)
STRIPE = (96, 128, 196, 255)

# The card: x 1..14, y 3..12 (14 x 10), corners rounded off.
X0, X1, Y0, Y1 = 1, 14, 3, 12


def draw():
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    px = img.load()
    for y in range(Y0, Y1 + 1):
        for x in range(X0, X1 + 1):
            corner = (x in (X0, X1)) and (y in (Y0, Y1))
            if corner:
                continue
            edge = x in (X0, X1) or y in (Y0, Y1)
            if edge:
                px[x, y] = OUTLINE
                continue
            # Light from the top left: rows near the top lighter.
            if y == Y0 + 1:
                c = EDGE_LIGHT if x < X1 - 2 else BODY_LIGHT
            elif x == X0 + 1:
                c = BODY_LIGHT if y < Y1 - 2 else BODY
            elif y == Y1 - 1:
                c = EDGE_DARK
            elif x == X1 - 1:
                c = BODY_DARK
            else:
                c = BODY
                # A soft diagonal sheen across the face.
                d = (x - X0) + (y - Y0)
                if d in (9, 10):
                    c = SHEEN
                elif y >= Y1 - 3 and x >= X1 - 5:
                    c = BODY_DARK
            px[x, y] = c
    # Corner pixels inside the rounded corners keep the outline continuous.
    for (x, y) in ((X0 + 1, Y0 + 1), (X1 - 1, Y0 + 1), (X0 + 1, Y1 - 1), (X1 - 1, Y1 - 1)):
        px[x, y] = OUTLINE
    # A thin light band under the top edge (the card's printed stripe).
    for x in range(X0 + 2, X1 - 1):
        if px[x, Y0 + 2] == BODY:
            px[x, Y0 + 2] = STRIPE
    # The chip: 3 x 3 at x 3..5, y 6..8 with an outline and contact lines.
    for y in range(6, 9):
        for x in range(3, 6):
            px[x, y] = CHIP
    px[3, 6] = CHIP_HI
    px[4, 6] = CHIP_HI
    px[3, 7] = CHIP_LINE
    px[4, 7] = CHIP_HI
    px[5, 7] = CHIP_LINE
    px[5, 6] = CHIP
    px[5, 8] = CHIP_EDGE
    px[4, 8] = CHIP_LINE
    # The seal: a small gold coin at the top right.
    px[11, 5] = SEAL
    px[12, 5] = SEAL_DARK
    px[11, 6] = SEAL_DARK
    px[12, 6] = SEAL_DARK
    # The embossed number row: light dots in groups with a shadow under each.
    for x in (3, 4, 6, 7, 9, 10, 12):
        px[x, 10] = DOT
        if px[x, 11] not in (OUTLINE,):
            px[x, 11] = DOT_SHADOW
    return img


def main():
    out = sys.argv[1]
    img = draw()
    img.save(out)
    if len(sys.argv) > 2:
        big = img.resize((256, 256), Image.NEAREST)
        bg = Image.new("RGBA", (256, 256), (139, 139, 139, 255))
        bg.alpha_composite(big)
        bg.save(sys.argv[2])


if __name__ == "__main__":
    main()
