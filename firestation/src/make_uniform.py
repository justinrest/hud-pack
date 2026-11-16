# Draws the firefighter turnout uniform: the worn layers (vanilla humanoid
# and humanoid_leggings layouts, 64 x 32) and the four item icons.
#
# Usage: python -I make_uniform.py <vanilla assets/minecraft/textures> <assets/firestation>
#
# The vanilla leather layers and leather item icons are used only for their
# shapes (which pixels exist) and their light/dark pattern; every colour,
# band, seam and detail is painted here.
import os
import sys

from PIL import Image

VT, OUT = sys.argv[1], sys.argv[2]
CLEAR = (0, 0, 0, 0)


def rgb(*c):
    return tuple(c) + (255,)


# Turnout fabric (tan Nomex), five tones from light to dark.
TAN = [rgb(214, 192, 136), rgb(192, 168, 112), rgb(174, 150, 96), rgb(150, 126, 78), rgb(112, 90, 54)]
# Reflective trim: lime-yellow edges, silver middle.
LIME = [rgb(226, 240, 84), rgb(198, 214, 52)]
SILVER = [rgb(236, 238, 242), rgb(198, 202, 210)]
# Cuffs and wristlets.
CUFF = [rgb(96, 90, 84), rgb(70, 66, 62), rgb(50, 47, 44)]
# Helmet.
RED = [rgb(226, 74, 60), rgb(196, 40, 32), rgb(168, 28, 22), rgb(132, 18, 14), rgb(92, 10, 8)]
GOLD = [rgb(252, 222, 110), rgb(232, 186, 56), rgb(176, 126, 26)]
VISOR = [rgb(118, 128, 146), rgb(46, 50, 60), rgb(24, 26, 32)]
# Boots.
BOOT = [rgb(86, 86, 94), rgb(56, 56, 62), rgb(40, 40, 45), rgb(26, 26, 30)]
SOLE = [rgb(132, 120, 104), rgb(30, 26, 24)]


def noise(x, y, salt=0):
    """A fixed pseudo-random value in [0, 1) per pixel (fabric grain)."""
    h = (x * 374761393 + y * 668265263 + salt * 2246822519) & 0xFFFFFFFF
    h = ((h ^ (h >> 13)) * 1274126177) & 0xFFFFFFFF
    return ((h ^ (h >> 16)) & 0xFFFF) / 65536.0


def faces(u, v, w, h, d):
    """Vanilla box UV: face name -> (x, y, width, height)."""
    return {
        "top": (u + d, v, w, d),
        "bottom": (u + d + w, v, w, d),
        "right": (u, v + d, d, h),
        "front": (u + d, v + d, w, h),
        "left": (u + d + w, v + d, d, h),
        "back": (u + 2 * d + w, v + d, w, h),
    }


SIDES = ("right", "front", "left", "back")
HEAD = faces(0, 0, 8, 8, 8)
BODY = faces(16, 16, 8, 12, 4)
ARM = faces(40, 16, 4, 12, 4)
LEG = faces(0, 16, 4, 12, 4)


def cloth(img, rect, tones, salt, rows=None):
    """Fills a face with fabric: base tone, grain, a light top-left and a
    dark bottom-right bevel. `rows` limits it to face rows [a, b)."""
    x0, y0, w, h = rect
    a, b = rows or (0, h)
    for j in range(a, b):
        for i in range(w):
            n = noise(x0 + i, y0 + j, salt)
            t = 2
            if n < 0.16:
                t = 3
            elif n > 0.86:
                t = 1
            if j == a or i == 0:
                t = min(t, 1)
            if j == b - 1 or i == w - 1:
                t = max(t, 3)
            img.putpixel((x0 + i, y0 + j), tones[t])


def row_band(img, rect, k, kind):
    """Paints face row k of a side face as trim: 'lime' or 'silver'."""
    x0, y0, w, _ = rect
    for i in range(w):
        if img.getpixel((x0 + i, y0 + k))[3] == 0:
            continue
        tones = LIME if kind == "lime" else SILVER
        t = 1 if noise(x0 + i, y0 + k, 9) < 0.2 or i == w - 1 else 0
        img.putpixel((x0 + i, y0 + k), tones[t])


def trim(img, box, top_row):
    """A three-row reflective band (lime, silver, lime) starting at side-face
    row `top_row`, the same rows on all four sides so it wraps."""
    for f in SIDES:
        row_band(img, box[f], top_row, "lime")
        row_band(img, box[f], top_row + 1, "silver")
        row_band(img, box[f], top_row + 2, "lime")


def set_px(img, x, y, c):
    if img.getpixel((x, y))[3]:
        img.putpixel((x, y), c)


def mask(path):
    im = Image.open(path).convert("RGBA")
    return im.getchannel("A")


# ---------------------------------------------------------------- humanoid
def humanoid():
    img = Image.new("RGBA", (64, 32), CLEAR)
    vanilla = mask(f"{VT}/entity/equipment/humanoid/leather.png")

    # Helmet: vanilla leather helmet's shape (open face), painted red.
    for f, (x0, y0, w, h) in HEAD.items():
        for j in range(h):
            for i in range(w):
                if vanilla.getpixel((x0 + i, y0 + j)):
                    img.putpixel((x0 + i, y0 + j), CLEAR)
        tmp = Image.new("RGBA", (64, 32), CLEAR)
        cloth(tmp, (x0, y0, w, h), RED, 3)
        for j in range(h):
            for i in range(w):
                if vanilla.getpixel((x0 + i, y0 + j)):
                    img.putpixel((x0 + i, y0 + j), tmp.getpixel((x0 + i, y0 + j)))
    # Crown ridge front to back on the top face, and the brim: the lowest
    # covered row of each side face, darker, a lighter lip above it.
    tx, ty, tw, th = HEAD["top"]
    for j in range(th):
        set_px(img, tx + 3, ty + j, RED[0])
        set_px(img, tx + 4, ty + j, RED[1])
    for f in SIDES:
        x0, y0, w, h = HEAD[f]
        for i in range(w):
            col = [j for j in range(h) if img.getpixel((x0 + i, y0 + j))[3]]
            if not col:
                continue
            low = max(col)
            set_px(img, x0 + i, y0 + low, RED[4])
            if low - 1 in col and f != "front":
                set_px(img, x0 + i, y0 + low - 1, RED[3])
    # Back brim: the long tail of a fire helmet, two dark rows.
    bx, by, bw, bh = HEAD["back"]
    for i in range(bw):
        set_px(img, bx + i, by + bh - 2, RED[4])
    # Front: a gold shield (frontpiece) over a dark face-shield edge, the
    # sides of the face framed by the brim.
    fx, fy, fw, fh = HEAD["front"]
    for i in range(fw):
        set_px(img, fx + i, fy + 2, VISOR[2])
        set_px(img, fx + i, fy + 3, RED[4])
    set_px(img, fx + 1, fy + 2, VISOR[0])
    set_px(img, fx + 2, fy + 2, VISOR[1])
    shield = {(3, 0): 0, (4, 0): 1, (3, 1): 1, (4, 1): 2}
    for (i, j), t in shield.items():
        set_px(img, fx + i, fy + j, GOLD[t])
    for i, j in ((2, 0), (5, 0), (2, 1), (5, 1)):
        set_px(img, fx + i, fy + j, RED[3])

    # Coat: full body and full-length sleeves.
    for f, r in BODY.items():
        cloth(img, r, TAN, 1)
    for f, r in ARM.items():
        cloth(img, r, TAN, 2)
    # Collar: the top face dark, the first row of the side faces a raised
    # collar band, open at the front.
    cloth(img, BODY["top"], [TAN[2], TAN[3], TAN[3], TAN[4], TAN[4]], 4)
    for f in SIDES:
        x0, y0, w, _ = BODY[f]
        for i in range(w):
            img.putpixel((x0 + i, y0), TAN[3] if f != "front" else TAN[4])
    fx, fy, fw, fh = BODY["front"]
    for i in (3, 4):
        img.putpixel((fx + i, fy), CLEAR)  # neck opening
        img.putpixel((fx + i, fy + 1), TAN[4])
    # Reflective trim: chest and hem, wrapping all four sides.
    trim(img, BODY, 4)
    trim(img, BODY, 9)
    # Front closure: a storm flap down the middle with clasps, over the trim.
    for j in range(1, fh):
        img.putpixel((fx + 3, fy + j), TAN[3])
        img.putpixel((fx + 4, fy + j), TAN[2] if j not in (4, 5, 6, 9, 10, 11) else TAN[3])
    for j in (2, 7):
        img.putpixel((fx + 4, fy + j), SILVER[1])
    # Pocket flaps below the chest band, either side of the closure.
    for i in (1, 2):
        img.putpixel((fx + i, fy + 7), TAN[4])
        img.putpixel((fx + i, fy + 8), TAN[3])
    for i in (5, 6):
        img.putpixel((fx + i, fy + 7), TAN[4])
        img.putpixel((fx + i, fy + 8), TAN[3])
    # Sleeves: trim on the forearm, dark wristlets at the cuff, shoulder seam.
    trim(img, ARM, 6)
    for f in SIDES:
        x0, y0, w, h = ARM[f]
        for i in range(w):
            img.putpixel((x0 + i, y0 + 10), CUFF[1] if noise(x0 + i, y0, 5) < 0.5 else CUFF[0])
            img.putpixel((x0 + i, y0 + 11), CUFF[2])
            img.putpixel((x0 + i, y0), TAN[3])
    cloth(img, ARM["bottom"], CUFF + [CUFF[2], CUFF[2]], 6)

    # Boots: the vanilla boot shape (lower legs and sole), black leather.
    for f in SIDES:
        x0, y0, w, h = LEG[f]
        cloth(img, (x0, y0, w, h), BOOT + [BOOT[3]], 7, rows=(6, 12))
        # A trim band round the boot top, a toe cap and a sole line.
        for i in range(w):
            img.putpixel((x0 + i, y0 + 6), BOOT[1])
            img.putpixel((x0 + i, y0 + 11), SOLE[1])
            img.putpixel((x0 + i, y0 + 10), SOLE[0] if f == "front" else BOOT[3])
    tx, ty, tw, th = LEG["front"]
    for i in range(tw):
        img.putpixel((tx + i, ty + 9), BOOT[0])
    cloth(img, LEG["bottom"], [SOLE[1]] * 5, 8)
    return img


# --------------------------------------------------------- humanoid_leggings
def leggings():
    img = Image.new("RGBA", (64, 32), CLEAR)
    # Trousers down to the boot tops (side rows 0-7) and their top faces.
    for f in SIDES:
        cloth(img, LEG[f], TAN, 11, rows=(0, 8))
    cloth(img, LEG["top"], TAN, 12)
    # Knee patches and the trim band just above the boots.
    fx, fy, fw, fh = LEG["front"]
    for i in range(fw):
        img.putpixel((fx + i, fy + 2), TAN[3])
    for i in (1, 2):
        img.putpixel((fx + i, fy + 1), TAN[1])
    for f in SIDES:
        row_band(img, LEG[f], 4, "lime")
        row_band(img, LEG[f], 5, "silver")
        row_band(img, LEG[f], 6, "lime")
    # Waist: the lower body (side rows 7-11) with a belt line and suspender
    # straps front and back.
    for f in SIDES:
        cloth(img, BODY[f], TAN, 13, rows=(7, 12))
        x0, y0, w, _ = BODY[f]
        for i in range(w):
            img.putpixel((x0 + i, y0 + 7), TAN[4])
    for f in ("front", "back"):
        x0, y0, w, _ = BODY[f]
        for j in range(7, 12):
            img.putpixel((x0 + 1, y0 + j), CUFF[1])
            img.putpixel((x0 + w - 2, y0 + j), CUFF[1])
    return img


# ---------------------------------------------------------------- item icons
def recolour(path, tones, salt):
    """The vanilla leather icon's shape and light pattern in `tones`."""
    src = Image.open(path).convert("RGBA")
    out = Image.new("RGBA", src.size, CLEAR)
    lum = sorted({sum(src.getpixel((x, y))[:3]) for x in range(16) for y in range(16)
                  if src.getpixel((x, y))[3]})
    for y in range(16):
        for x in range(16):
            r, g, b, a = src.getpixel((x, y))
            if not a:
                continue
            rank = lum.index(r + g + b) / max(1, len(lum) - 1)
            t = 4 - min(4, int(rank * 5))
            if t == 2 and noise(x, y, salt) < 0.2:
                t = 3
            out.putpixel((x, y), tones[t])
    return out


def icon_rows(img, rows, x0=0, x1=16):
    for k, y in enumerate(rows):
        for x in range(x0, x1):
            if img.getpixel((x, y))[3]:
                img.putpixel((x, y), (LIME if k % 2 == 0 else SILVER)[0 if x % 5 else 1])


def icons():
    it = f"{VT}/item"
    helmet = Image.new("RGBA", (16, 16), CLEAR)
    key = {"h": RED[0], "R": RED[1], "m": RED[2], "r": RED[3], "d": RED[4],
           "H": GOLD[0], "G": GOLD[1], "g": GOLD[2], "v": VISOR[2], "s": VISOR[0]}
    rows = [
        "................",
        "................",
        "................",
        "......hhRRR.....",
        "....hhRRRRRmm...",
        "...hRRRRHGRRmr..",
        "...hRRRHGGgRmr..",
        "..hRRRRHGGgRmmr.",
        "..RRRRRRggRRmmr.",
        "..RRmRRRRRRmmrr.",
        ".svvvvvvvvvvvrrd",
        "dddddddddddddddd",
        ".rrr.......rdddd",
        "................",
        "................",
        "................",
    ]
    for y, line in enumerate(rows):
        for x, ch in enumerate(line):
            if ch in key:
                helmet.putpixel((x, y), key[ch])
    coat = recolour(f"{it}/leather_chestplate.png", TAN, 22)
    icon_rows(coat, [8, 9, 10])
    for y in range(3, 15):
        if coat.getpixel((7, y))[3]:
            coat.putpixel((7, y), TAN[4])
    trousers = recolour(f"{it}/leather_leggings.png", TAN, 23)
    icon_rows(trousers, [10, 11, 12])
    boots = recolour(f"{it}/leather_boots.png", BOOT + [BOOT[3]], 24)
    bottom = {}
    for x in range(16):
        ys = [y for y in range(16) if boots.getpixel((x, y))[3]]
        if ys:
            bottom[x] = max(ys)
    for x, y in bottom.items():
        boots.putpixel((x, y), SOLE[0])
    for x in range(16):
        ys = [y for y in range(16) if boots.getpixel((x, y))[3]]
        if ys and min(ys) + 1 < 16 and boots.getpixel((x, min(ys) + 1))[3]:
            boots.putpixel((x, min(ys) + 1), LIME[0])
    return {"fire_helmet": helmet, "fire_turnout_coat": coat,
            "fire_turnout_trousers": trousers, "fire_boots": boots}


os.makedirs(f"{OUT}/textures/item", exist_ok=True)
os.makedirs(f"{OUT}/textures/entity/equipment/humanoid", exist_ok=True)
os.makedirs(f"{OUT}/textures/entity/equipment/humanoid_leggings", exist_ok=True)
humanoid().save(f"{OUT}/textures/entity/equipment/humanoid/turnout.png")
leggings().save(f"{OUT}/textures/entity/equipment/humanoid_leggings/turnout.png")
for name, im in icons().items():
    im.save(f"{OUT}/textures/item/{name}.png")
