"""Draws lookout's security cameras: textures, item models and item definitions.

Three tiers (basic, standard, advanced), each a bullet camera that hangs
under a swivel (wall and ceiling mounts) or stands on one (floor mounts),
plus one set of galvanised steel brackets. Every texture is a 32x32 sheet
at one texel per model unit (UV = texel / 2), shaded like vanilla: lit from
the top, a highlight row on top edges, a shadow row at the bottom, dark
outlines where parts meet, plastic speckle or brushed-metal grain.

Placed parts are shown on item_display entities in "fixed" mode at scale
0.5 with the pivot at model (8, 8, 8): the lens faces -z, the wall is at
z = 16.64, the ceiling at y = 16.64 and the floor at y = -0.64.

    python -I make_cameras.py [assets_dir]

assets_dir defaults to ../assets/lookout next to this script.
"""
import json
import os
import random
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "assets", "lookout")

TIERS = {
    "basic": {
        # cream plastic
        "base": (220, 214, 194), "light": (240, 236, 222), "dark": (186, 178, 156),
        "outline": (128, 120, 100), "grain": "speckle",
        "band": None, "led": ((70, 230, 90), (180, 255, 190)),
        "lens": 3, "lens_z": (1, 2), "hood": None, "ir": False, "vents": False,
    },
    "standard": {
        # graphite brushed metal
        "base": (112, 117, 124), "light": (146, 151, 159), "dark": (84, 88, 95),
        "outline": (50, 53, 58), "grain": "brushed",
        "band": ((56, 104, 196), (100, 150, 236), (36, 70, 146)),
        "led": ((70, 140, 255), (190, 220, 255)),
        "lens": 5, "lens_z": (1, 2), "hood": 0.5, "ir": False, "vents": False,
    },
    "advanced": {
        # black powder-coated metal
        "base": (48, 48, 53), "light": (76, 76, 83), "dark": (32, 32, 36),
        "outline": (14, 14, 16), "grain": "brushed",
        "band": ((214, 162, 52), (250, 210, 112), (150, 104, 26)),
        "led": ((235, 40, 40), (255, 160, 150)),
        "lens": 5, "lens_z": (0, 2), "hood": -0.5, "ir": True, "vents": True,
    },
}

STEEL = {"base": (166, 170, 175), "light": (200, 204, 209), "dark": (126, 130, 137),
         "outline": (82, 86, 93), "grain": "brushed"}

LENS_RIM = (26, 27, 30)
GLASS = [(12, 14, 20), (22, 28, 44), (36, 48, 78)]
GLINT = (210, 228, 250)


def clamp(c):
    return tuple(max(0, min(255, int(round(v)))) for v in c)


def mix(a, b, t):
    return clamp(a[i] + (b[i] - a[i]) * t for i in range(3))


class Sheet:
    def __init__(self, seed):
        self.img = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
        self.px = self.img.load()
        self.rnd = random.Random(seed)

    def set(self, x, y, c):
        if 0 <= x < 32 and 0 <= y < 32:
            self.px[x, y] = clamp(c) + (255,)

    def get(self, x, y):
        return self.px[x, y][:3]

    def panel(self, r, m, top=True, bottom=True, left=False, right=False, along="u"):
        """A shaded panel on region r = (x, y, w, h) in texels."""
        x0, y0, w, h = r
        X0, Y0 = int(x0), int(y0)
        W, H = max(1, int(round(x0 + w)) - X0), max(1, int(round(y0 + h)) - Y0)
        streak = [self.rnd.uniform(-7, 7) for _ in range(max(W, H))]
        for j in range(H):
            for i in range(W):
                t = j / max(1, H - 1)
                c = mix(m["light"], m["dark"], 0.15 + 0.7 * t) if H > 2 else m["base"]
                c = mix(c, m["base"], 0.45)
                if m["grain"] == "speckle":
                    n = self.rnd.uniform(-6, 6)
                else:
                    n = (streak[j] if along == "u" else streak[i]) + self.rnd.uniform(-3, 3)
                c = clamp(v + n for v in c)
                if top and j == 0 and H > 1:
                    c = mix(c, m["light"], 0.75)
                if bottom and j == H - 1 and H > 1:
                    c = mix(c, m["dark"], 0.8)
                if left and i == 0 and W > 1:
                    c = mix(c, m["outline"], 0.6)
                if right and i == W - 1 and W > 1:
                    c = mix(c, m["outline"], 0.6)
                self.set(X0 + i, Y0 + j, c)

    def fill(self, r, c, jitter=0):
        x0, y0, w, h = r
        for j in range(int(y0), max(int(y0) + 1, int(round(y0 + h)))):
            for i in range(int(x0), max(int(x0) + 1, int(round(x0 + w)))):
                self.set(i, j, tuple(v + self.rnd.uniform(-jitter, jitter) for v in c))


# ---- regions (texels) ----

H = {  # head sheet
    "side": (0, 0, 11, 7), "top": (13, 0, 7, 11), "bottom": (20, 0, 7, 11),
    "front": (0, 8, 7, 7), "back": (0, 25, 7, 7),
    "lens": (8, 12, 5, 5), "ring": (14, 12, 1, 5),
    "hood_side": (16, 12, 14.5, 0.75), "hood_front": (16, 14, 8, 0.75),
    "stub": (16, 16, 2, 2), "hood_top": (24, 16, 8, 14.5), "hood_under": (8, 17, 8, 14.5),
    "cap": (16, 19, 6, 5), "cap_edge": (16, 25, 6, 0.5), "cap_side": (22, 19, 0.5, 5),
}
B = {  # bracket sheet
    "plate": (0, 0, 6, 7), "edge": (0, 8, 7, 1), "bolt": (8, 0, 1, 1),
    "arm_top": (10, 0, 1.5, 7.64), "arm_side": (0, 10, 7.64, 1.5), "arm_end": (12, 0, 1.5, 1.5),
    "elbow": (14, 0, 2.5, 3), "elbow_end": (14, 4, 2.5, 2.5), "gusset": (18, 0, 2.14, 1.5),
    "rod": (20, 0, 1.5, 6.14), "post": (22, 0, 1.5, 6.14),
    "collar": (24, 0, 2.5, 1.25), "collar_end": (24, 2, 2.5, 2.5),
}


def draw_head(name, t):
    s = Sheet(sum(map(ord, name)))
    m = t
    out = {"base": m["base"], "light": m["light"], "dark": m["dark"], "outline": m["outline"], "grain": m["grain"]}
    # body sides: front at u = 0
    s.panel(H["side"], out, left=True, right=True)
    sx, sy, _, _ = H["side"]
    # seam where the front bezel meets the housing
    for j in range(7):
        s.set(sx + 1, sy + j, mix(s.get(sx + 1, sy + j), m["outline"], 0.35))
    if m["band"]:
        b, bl, bd = m["band"]
        for j in range(7):
            for i in (3, 4):
                c = mix(bl, bd, j / 6) if j not in (0, 6) else (bl if j == 0 else bd)
                s.set(sx + i, sy + j, mix(c, b, 0.3))
    else:
        # basic: a moulding line splitting the shell
        for j in range(1, 6):
            s.set(sx + 7, sy + j, mix(s.get(sx + 7, sy + j), m["outline"], 0.45))
            s.set(sx + 8, sy + j, mix(s.get(sx + 8, sy + j), m["light"], 0.4))
    if m["vents"]:
        for row in (2, 4):
            for i in range(6, 10):
                s.set(sx + i, sy + row, (10, 10, 12))
                s.set(sx + i, sy + row + 1, mix(s.get(sx + i, sy + row + 1), m["light"], 0.5))
    # top: x across, z down (front first)
    s.panel(H["top"], {**out, "dark": out["base"]}, top=True, bottom=True, left=True, right=True, along="v")
    tx, ty, _, _ = H["top"]
    if m["band"]:
        b, bl, bd = m["band"]
        for i in range(7):
            for j in (3, 4):
                s.set(tx + i, ty + j, bl if j == 3 else b)
    s.panel(H["bottom"], {**out, "light": out["base"], "base": out["dark"]}, left=True, right=True)
    bx, by, _, _ = H["bottom"]
    for (i, j) in ((3, 4), (3, 7)):  # mounting screws
        s.set(bx + i, by + j, m["outline"])
    # front bezel (north face, u = 16 - x: the viewer's right is u up)
    s.panel(H["front"], {**out, "base": mix(m["base"], m["dark"], 0.35)}, left=True, right=True)
    fx, fy, _, _ = H["front"]
    n = m["lens"]
    lo = (7 - n) // 2
    # recess shadow around the lens barrel
    for j in range(7):
        for i in range(7):
            if lo - 1 <= i <= lo + n and lo - 1 <= j <= lo + n and not (lo <= i < lo + n and lo <= j < lo + n):
                s.set(fx + i, fy + j, mix(s.get(fx + i, fy + j), m["outline"], 0.35))
    if m["ir"]:
        for (i, j) in ((0, 1), (0, 3), (0, 5), (6, 1), (6, 3), (6, 5), (2, 0), (4, 0), (2, 6), (4, 6)):
            s.set(fx + i, fy + j, (128, 22, 24))
        for (i, j) in ((0, 3), (6, 3)):
            s.set(fx + i, fy + j, (176, 42, 40))
    led, ledhi = m["led"]
    if m["ir"]:
        s.set(fx + 0, fy + 0, led)
    else:
        s.set(fx + 6, fy + 0, led)
        s.set(fx + 5, fy + 0, mix(s.get(fx + 5, fy + 0), ledhi, 0.25))
    # lens glass: n x n at the region's corner
    lx, ly, _, _ = H["lens"]
    c = (n - 1) / 2
    for j in range(n):
        for i in range(n):
            d = max(abs(i - c), abs(j - c))
            if n >= 5 and d == 2 and abs(i - c) == abs(j - c):
                col = LENS_RIM  # rounded corners
            elif n >= 5 and d == 2:
                col = mix(LENS_RIM, (70, 72, 78), 0.3 if j < c else 0.0)
            else:
                col = GLASS[0] if (i + j) > n - 1 else GLASS[1]
                if i + j == n - 2 or (n == 3 and i + j == 1):
                    col = GLASS[2]
            s.set(lx + i, ly + j, col)
    gl = 1 if n >= 5 else 0
    s.set(lx + gl, ly + gl, GLINT)
    if n >= 5:
        s.set(lx + gl + 1, ly + gl, mix(GLINT, GLASS[2], 0.5))
        s.set(lx + 3, ly + 3, mix(GLASS[1], GLINT, 0.3))
    s.panel(H["ring"], {"base": (40, 41, 45), "light": (78, 80, 86), "dark": (22, 22, 25),
                        "outline": (10, 10, 12), "grain": "brushed"}, along="v")
    # back and cable gland cap
    s.panel(H["back"], {**out, "base": mix(m["base"], m["dark"], 0.5)}, left=True, right=True)
    cap = {"base": (58, 60, 64), "light": (92, 95, 100), "dark": (36, 37, 40), "outline": (18, 18, 20), "grain": "brushed"}
    s.panel(H["cap"], cap, left=True, right=True)
    cx, cy, _, _ = H["cap"]
    for (i, j) in ((2, 2), (3, 2), (2, 3), (3, 3)):
        s.set(cx + i, cy + j, (20, 20, 22))  # cable hole
    s.set(cx + 2, cy + 1, (110, 112, 118))
    s.fill(H["cap_edge"], cap["dark"], 3)
    s.fill(H["cap_side"], cap["base"], 3)
    # swivel stub
    s.panel(H["stub"], cap, left=True, right=True)
    # sunshield
    if m["hood"] is not None:
        hood = {**out, "base": mix(m["base"], m["dark"], 0.2)}
        s.panel(H["hood_top"], {**hood, "dark": hood["base"]}, left=True, right=True, along="v")
        hx, hy, _, _ = H["hood_top"]
        for i in range(8):  # rolled front lip
            s.set(hx + i, hy, mix(m["light"], (255, 255, 255), 0.15))
        s.fill(H["hood_side"], mix(m["base"], m["dark"], 0.6), 2)
        s.fill(H["hood_front"], mix(m["light"], m["base"], 0.3), 2)
        s.panel(H["hood_under"], {**hood, "base": m["dark"], "light": m["dark"], "dark": m["outline"]}, top=False, along="v")
    return s.img


def draw_bracket():
    s = Sheet(4242)
    m = STEEL
    s.panel(B["plate"], m, left=True, right=True)
    px, py, _, _ = B["plate"]
    for j in range(1, 6):  # pressed rib
        s.set(px + 3, py + j, mix(s.get(px + 3, py + j), m["light"], 0.4))
        s.set(px + 2, py + j, mix(s.get(px + 2, py + j), m["dark"], 0.3))
    s.fill(B["edge"], m["dark"], 4)
    s.fill(B["bolt"], (96, 100, 106))
    s.panel(B["arm_top"], {**m, "dark": m["base"]}, top=False, bottom=False, left=True, right=True, along="v")
    s.panel(B["arm_side"], m)
    s.fill(B["arm_end"], m["dark"], 3)
    s.panel(B["elbow"], {**m, "base": mix(m["base"], m["dark"], 0.3)}, left=True, right=True)
    s.fill(B["elbow_end"], m["light"], 4)
    s.panel(B["gusset"], m)
    s.panel(B["rod"], m, top=False, bottom=False, left=True, right=True, along="v")
    s.panel(B["post"], m, top=False, bottom=False, left=True, right=True, along="v")
    s.panel(B["collar"], {**m, "base": mix(m["base"], m["dark"], 0.4)})
    s.fill(B["collar_end"], m["base"], 4)
    return s.img


# ---- models ----

def uv(r, mirror=False):
    x, y, w, h = r
    u0, v0, u1, v1 = x / 2, y / 2, (x + w) / 2, (y + h) / 2
    return [rr(u1), rr(v0), rr(u0), rr(v1)] if mirror else [rr(u0), rr(v0), rr(u1), rr(v1)]


def rr(v):
    return round(v, 4)


def box(name, a, b, faces):
    return {"name": name, "from": [rr(v) for v in a], "to": [rr(v) for v in b],
            "faces": {d: f for d, f in faces.items() if f is not None}}


def f(tex, region, mirror=False, rotation=0):
    face = {"uv": uv(region, mirror), "texture": tex}
    if rotation:
        face["rotation"] = rotation
    return face


def head_elements(t, up, tex="#head"):
    # The pivot (8, 8, 8) sits on the body's top face (hanging) or bottom face (standing),
    # and every corner stays within 8.6 px of it, so a tilted head never reaches the wall.
    dy = 8 if up else 1
    n = t["lens"]
    els = []
    els.append(box("body", (4.5, dy, 2), (11.5, dy + 7, 13), {
        "north": f(tex, H["front"]), "south": f(tex, H["back"]),
        "west": f(tex, H["side"]), "east": f(tex, H["side"], mirror=True),
        "up": f(tex, H["top"]), "down": f(tex, H["bottom"])}))
    lz0, lz1 = t["lens_z"]
    els.append(box("lens", (8 - n / 2, dy + 3.5 - n / 2, lz0), (8 + n / 2, dy + 3.5 + n / 2, lz1), {
        "north": f(tex, (H["lens"][0], H["lens"][1], n, n)),
        "west": f(tex, H["ring"]), "east": f(tex, H["ring"]),
        "up": f(tex, H["ring"], rotation=90), "down": f(tex, H["ring"], rotation=90)}))
    els.append(box("cable_gland", (5, dy + 1, 13), (11, dy + 6, 13.5), {
        "south": f(tex, H["cap"]), "west": f(tex, H["cap_side"]), "east": f(tex, H["cap_side"]),
        "up": f(tex, H["cap_edge"]), "down": f(tex, H["cap_edge"])}))
    if t["hood"] is not None:
        hz = t["hood"]
        hy = dy + 7
        length = 13 - hz
        els.append(box("sunshield", (4, hy, hz), (12, hy + 0.75, 13), {
            "up": f(tex, (H["hood_top"][0], H["hood_top"][1], 8, length)),
            "down": f(tex, (H["hood_under"][0], H["hood_under"][1], 8, length)),
            "west": f(tex, (H["hood_side"][0], H["hood_side"][1], length, 0.75)),
            "east": f(tex, (H["hood_side"][0], H["hood_side"][1], length, 0.75), mirror=True),
            "north": f(tex, H["hood_front"]), "south": f(tex, H["hood_front"])}))
        # side skirts so the sunshield reads as a hood
        skirt = (H["hood_side"][0], H["hood_side"][1], length - 1, 0.75)
        for x0, x1 in ((4, 4.5), (11.5, 12)):
            els.append(box("sunshield_skirt", (x0, hy - 1.5, hz + 1), (x1, hy, 13), {
                "west": f(tex, skirt), "east": f(tex, skirt, mirror=True),
                "north": f(tex, (H["hood_front"][0], H["hood_front"][1], 0.5, 0.75)),
                "down": f(tex, (H["hood_front"][0], H["hood_front"][1], 0.5, 0.75))}))
    stub = {"north": f(tex, H["stub"]), "south": f(tex, H["stub"]), "west": f(tex, H["stub"]),
            "east": f(tex, H["stub"])}
    if up:
        stub["down"] = f(tex, H["stub"])
    else:
        stub["up"] = f(tex, H["stub"])
    els.append(box("swivel", (7, 7, 7), (9, 9, 9), stub))
    return els


def plate_bolts(tex, axis, at, spots):
    els = []
    bolt = f(tex, B["bolt"])
    for (a, b) in spots:
        if axis == "z":
            lo, hi = (a, b, at - 0.4), (a + 1, b + 1, at)
            faces = {"north": bolt, "up": bolt, "down": bolt, "west": bolt, "east": bolt}
        elif axis == "ydown":
            lo, hi = (a, at - 0.4, b), (a + 1, at, b + 1)
            faces = {"down": bolt, "north": bolt, "south": bolt, "west": bolt, "east": bolt}
        else:
            lo, hi = (a, at, b), (a + 1, at + 0.4, b + 1)
            faces = {"up": bolt, "north": bolt, "south": bolt, "west": bolt, "east": bolt}
        els.append(box("bolt", lo, hi, faces))
    return els


WALL = 16.64
CEIL = 16.64
FLOOR = -0.64


def edge(w, h):
    return (B["edge"][0], B["edge"][1], w, h)


def wall_bracket(tex="#bracket"):
    e = []
    e.append(box("wall_plate", (5, 6, WALL - 1), (11, 13, WALL), {
        "north": f(tex, B["plate"]),
        "west": f(tex, edge(1, 7)), "east": f(tex, edge(1, 7)),
        "up": f(tex, edge(6, 1)), "down": f(tex, edge(6, 1))}))
    e += plate_bolts(tex, "z", WALL - 1, [(5.5, 6.5), (9.5, 6.5), (5.5, 11.5), (9.5, 11.5)])
    arm = WALL - 1 - 9.25
    e.append(box("arm", (7.25, 9.5, 9.25), (8.75, 11, WALL - 1), {
        "up": f(tex, (B["arm_top"][0], B["arm_top"][1], 1.5, arm)),
        "down": f(tex, (B["arm_top"][0], B["arm_top"][1], 1.5, arm)),
        "west": f(tex, (B["arm_side"][0], B["arm_side"][1], arm, 1.5)),
        "east": f(tex, (B["arm_side"][0], B["arm_side"][1], arm, 1.5), mirror=True)}))
    e.append(box("gusset", (7.5, 8, 13.5), (8.5, 9.5, WALL - 1), {
        "west": f(tex, B["gusset"]), "east": f(tex, B["gusset"], mirror=True),
        "north": f(tex, B["arm_end"]), "down": f(tex, (B["arm_top"][0], B["arm_top"][1], 1, 2.14))}))
    e.append(box("elbow", (6.75, 9, 6.75), (9.25, 11.5, 9.25), {
        "north": f(tex, B["elbow"]), "south": f(tex, B["elbow"]), "west": f(tex, B["elbow"]),
        "east": f(tex, B["elbow"]), "up": f(tex, B["elbow_end"]), "down": f(tex, B["elbow_end"])}))
    return e


def ceiling_bracket(tex="#bracket"):
    e = []
    plate = (B["plate"][0], B["plate"][1], 6, 6)
    e.append(box("ceiling_plate", (5, CEIL - 1, 5), (11, CEIL, 11), {
        "down": f(tex, plate),
        "north": f(tex, edge(6, 1)), "south": f(tex, edge(6, 1)),
        "west": f(tex, edge(6, 1)), "east": f(tex, edge(6, 1))}))
    e += plate_bolts(tex, "ydown", CEIL - 1, [(5.5, 5.5), (9.5, 5.5), (5.5, 9.5), (9.5, 9.5)])
    rod = (B["rod"][0], B["rod"][1], 1.5, CEIL - 1 - 10)
    e.append(box("rod", (7.25, 10, 7.25), (8.75, CEIL - 1, 8.75), {
        "north": f(tex, rod), "south": f(tex, rod), "west": f(tex, rod), "east": f(tex, rod)}))
    e.append(box("collar", (6.75, 8.75, 6.75), (9.25, 10, 9.25), {
        "north": f(tex, B["collar"]), "south": f(tex, B["collar"]), "west": f(tex, B["collar"]),
        "east": f(tex, B["collar"]), "up": f(tex, B["collar_end"]), "down": f(tex, B["collar_end"])}))
    return e


def floor_bracket(tex="#bracket"):
    e = []
    plate = (B["plate"][0], B["plate"][1], 6, 6)
    e.append(box("floor_plate", (5, FLOOR, 5), (11, FLOOR + 1, 11), {
        "up": f(tex, plate),
        "north": f(tex, edge(6, 1)), "south": f(tex, edge(6, 1)),
        "west": f(tex, edge(6, 1)), "east": f(tex, edge(6, 1))}))
    e += plate_bolts(tex, "yup", FLOOR + 1, [(5.5, 5.5), (9.5, 5.5), (5.5, 9.5), (9.5, 9.5)])
    post = (B["post"][0], B["post"][1], 1.5, 6.25 - (FLOOR + 1))
    e.append(box("post", (7.25, FLOOR + 1, 7.25), (8.75, 6.25, 8.75), {
        "north": f(tex, post), "south": f(tex, post), "west": f(tex, post), "east": f(tex, post)}))
    e.append(box("collar", (6.75, 6.25, 6.75), (9.25, 7.25, 9.25), {
        "north": f(tex, B["collar"]), "south": f(tex, B["collar"]), "west": f(tex, B["collar"]),
        "east": f(tex, B["collar"]), "up": f(tex, B["collar_end"]), "down": f(tex, B["collar_end"])}))
    return e


IDENTITY = {"fixed": {"rotation": [0, 0, 0], "translation": [0, 0, 0], "scale": [1, 1, 1]}}

ITEM_DISPLAY = {
    "gui": {"rotation": [22, 152, 0], "translation": [-0.25, 0.75, 0], "scale": [0.92, 0.92, 0.92]},
    "ground": {"rotation": [0, 0, 0], "translation": [0, 2, 0], "scale": [0.5, 0.5, 0.5]},
    "fixed": {"rotation": [0, 180, 0], "translation": [0, 0.5, -1.5], "scale": [0.8, 0.8, 0.8]},
    "head": {"rotation": [0, 180, 0], "translation": [0, 10, -2], "scale": [0.8, 0.8, 0.8]},
    "thirdperson_righthand": {"rotation": [10, 160, 0], "translation": [0, 2.5, -1], "scale": [0.5, 0.5, 0.5]},
    "thirdperson_lefthand": {"rotation": [10, 160, 0], "translation": [0, 2.5, -1], "scale": [0.5, 0.5, 0.5]},
    "firstperson_righthand": {"rotation": [0, 150, 0], "translation": [1, 3, 0], "scale": [0.55, 0.55, 0.55]},
    "firstperson_lefthand": {"rotation": [0, 150, 0], "translation": [1, 3, 0], "scale": [0.55, 0.55, 0.55]},
}


def write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(data, fh, indent=2)
        fh.write("\n")


def model(mid, textures, elements, display):
    write_json(os.path.join(OUT, "models", "item", mid + ".json"),
               {"textures": textures, "elements": elements, "display": display})
    write_json(os.path.join(OUT, "items", mid + ".json"),
               {"model": {"type": "minecraft:model", "model": f"lookout:item/{mid}"}})


def main():
    tex_dir = os.path.join(OUT, "textures", "item")
    os.makedirs(tex_dir, exist_ok=True)
    draw_bracket().save(os.path.join(tex_dir, "camera_bracket.png"))
    br = "lookout:item/camera_bracket"
    for name, t in TIERS.items():
        draw_head(name, t).save(os.path.join(tex_dir, f"camera_{name}.png"))
        tex = f"lookout:item/camera_{name}"
        model(f"camera_{name}_head", {"head": tex, "particle": tex}, head_elements(t, False), IDENTITY)
        model(f"camera_{name}_head_up", {"head": tex, "particle": tex}, head_elements(t, True), IDENTITY)
        model(f"camera_{name}", {"head": tex, "bracket": br, "particle": tex},
              head_elements(t, False) + wall_bracket(), ITEM_DISPLAY)
    model("camera_bracket_wall", {"bracket": br, "particle": br}, wall_bracket(), IDENTITY)
    model("camera_bracket_ceiling", {"bracket": br, "particle": br}, ceiling_bracket(), IDENTITY)
    model("camera_bracket_floor", {"bracket": br, "particle": br}, floor_bracket(), IDENTITY)
    print("wrote", os.path.normpath(OUT))


if __name__ == "__main__":
    main()
