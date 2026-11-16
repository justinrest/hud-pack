# Draws the firefighter uniform (item icons and worn layers) from scratch.
# Usage: python -I make_uniform.py <assets/firestation folder>
import os
import sys

from PIL import Image

OUT = sys.argv[1]
CLEAR = (0, 0, 0, 0)
TAN, TAN_D, TAN_L = (176, 148, 92, 255), (128, 104, 60, 255), (204, 178, 120, 255)
YEL, SIL = (238, 214, 40, 255), (222, 226, 232, 255)
RED, RED_D, RED_L = (178, 30, 30, 255), (120, 16, 16, 255), (220, 70, 60, 255)
GOLD, GOLD_D = (240, 196, 60, 255), (178, 130, 30, 255)
BLK, BLK_L = (34, 34, 38, 255), (70, 70, 78, 255)


def fill(img, x0, y0, x1, y1, c):
    for y in range(y0, y1):
        for x in range(x0, x1):
            img.putpixel((x, y), c)


def shade(img, x0, y0, x1, y1, base, dark, light):
    """A box with a light left edge and a dark right and bottom edge."""
    fill(img, x0, y0, x1, y1, base)
    fill(img, x0, y0, x0 + 1, y1, light)
    fill(img, x1 - 1, y0, x1, y1, dark)
    fill(img, x0, y1 - 1, x1, y1, dark)


def bands(img, rows, x0, x1):
    """Reflective trim: silver with yellow on each side."""
    for i, y in enumerate(rows):
        for x in range(x0, x1):
            if img.getpixel((x, y))[3]:
                img.putpixel((x, y), SIL if i % 3 == 1 else YEL)


def icon(name, draw):
    img = Image.new("RGBA", (16, 16), CLEAR)
    draw(img)
    img.save(f"{OUT}/textures/item/{name}.png")


def helmet(img):
    shade(img, 4, 3, 12, 10, RED, RED_D, RED_L)  # dome
    fill(img, 5, 2, 11, 3, RED)
    fill(img, 2, 10, 15, 12, RED_D)  # brim, longer at the back
    fill(img, 1, 11, 4, 12, RED_D)
    fill(img, 7, 4, 10, 8, GOLD)  # front shield
    fill(img, 8, 5, 9, 7, GOLD_D)


def coat(img):
    shade(img, 4, 2, 12, 15, TAN, TAN_D, TAN_L)
    shade(img, 1, 3, 4, 12, TAN, TAN_D, TAN_L)
    shade(img, 12, 3, 15, 12, TAN, TAN_D, TAN_L)
    fill(img, 6, 2, 10, 4, CLEAR)  # collar opening
    fill(img, 7, 4, 9, 15, TAN_D)  # front closure
    bands(img, [9, 10, 11], 1, 15)


def trousers(img):
    shade(img, 3, 2, 13, 5, TAN, TAN_D, TAN_L)
    shade(img, 3, 5, 7, 15, TAN, TAN_D, TAN_L)
    shade(img, 9, 5, 13, 15, TAN, TAN_D, TAN_L)
    bands(img, [10, 11, 12], 3, 13)


def boots(img):
    for x0 in (2, 9):
        shade(img, x0, 7, x0 + 4, 14, BLK, BLK, BLK_L)
        fill(img, x0 - 1, 12, x0 + 4, 14, BLK)  # toe
        fill(img, x0, 9, x0 + 4, 10, YEL)


os.makedirs(f"{OUT}/textures/item", exist_ok=True)
icon("fire_helmet", helmet)
icon("fire_turnout_coat", coat)
icon("fire_turnout_trousers", trousers)
icon("fire_boots", boots)


# Worn layers, laid out like vanilla armour textures (64 x 32): head box at
# (0,0) 8x8x8, body at (16,16) 8x12x4, arms at (40,16) 4x12x4, legs at
# (0,16) 4x12x4. Rows 20-31 are the side faces of body, arms and legs.
def worn_humanoid():
    img = Image.new("RGBA", (64, 32), CLEAR)
    # Helmet: top and sides red, the face left open below the brim.
    fill(img, 8, 0, 24, 8, RED)  # top and bottom of the head box
    fill(img, 0, 8, 32, 12, RED)  # upper band of all four sides
    fill(img, 0, 12, 8, 14, RED)  # right side, lower
    fill(img, 16, 12, 24, 14, RED)  # left side, lower
    fill(img, 24, 8, 32, 16, RED)  # back, down to the neck
    fill(img, 8, 8, 16, 9, RED_D)  # brim over the face
    fill(img, 11, 9, 13, 11, GOLD)  # front shield
    fill(img, 24, 15, 32, 16, RED_D)  # back brim
    # Coat: body and arms in tan with trim.
    fill(img, 16, 16, 40, 32, TAN)
    fill(img, 40, 16, 56, 32, TAN)
    fill(img, 23, 20, 25, 32, TAN_D)  # front closure
    bands(img, [26, 27, 28], 16, 40)
    bands(img, [27, 28, 29], 40, 56)
    # Boots: the lower legs, black with a yellow band.
    fill(img, 4, 16, 12, 20, BLK)  # top and sole
    fill(img, 0, 26, 16, 32, BLK)
    fill(img, 0, 27, 16, 28, YEL)
    return img


def worn_leggings():
    img = Image.new("RGBA", (64, 32), CLEAR)
    fill(img, 16, 26, 40, 32, TAN)  # waist
    fill(img, 20, 16, 36, 20, TAN)
    fill(img, 0, 16, 16, 32, TAN)  # legs
    fill(img, 4, 20, 6, 32, TAN_D)  # seam
    bands(img, [24, 25, 26], 0, 16)
    return img


os.makedirs(f"{OUT}/textures/entity/equipment/humanoid", exist_ok=True)
os.makedirs(f"{OUT}/textures/entity/equipment/humanoid_leggings", exist_ok=True)
worn_humanoid().save(f"{OUT}/textures/entity/equipment/humanoid/turnout.png")
worn_leggings().save(f"{OUT}/textures/entity/equipment/humanoid_leggings/turnout.png")
