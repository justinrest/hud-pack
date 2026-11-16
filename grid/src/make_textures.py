# Draws grid's protective gear textures from vanilla leather armour shapes.
import sys, os
from PIL import Image
V, OUT = sys.argv[1], sys.argv[2]
T = os.path.join(V, 'assets/minecraft/textures')
YEL = (242, 190, 24); ORA = (240, 140, 20); BLK = (46, 46, 52); SIL = (225, 230, 235)

def tint(img, color, box=None):
    img = img.convert('RGBA'); px = img.load()
    w, h = img.size
    x0, y0, x1, y1 = box or (0, 0, w, h)
    for y in range(y0, y1):
        for x in range(x0, x1):
            r, g, b, a = px[x, y]
            if a:
                l = (r + g + b) / 3 / 255
                l = 0.55 + 0.45 * l
                px[x, y] = tuple(min(255, int(c * l)) for c in color) + (a,)
    return img

DARK = (70, 70, 78)

def over(base, top):
    # Leather's straps and stitches, in dark grey instead of brown.
    base.alpha_composite(tint(top, DARK)); return base

def stripe_rows(img, rows, color, box=None):
    px = img.load(); w, h = img.size
    x0, _, x1, _ = box or (0, 0, w, h)
    for y in rows:
        for x in range(x0, x1):
            if px[x, y][3]:
                px[x, y] = color + (255,)

def item(name, color, stripes=()):
    base = tint(Image.open(f'{T}/item/leather_{name}.png'), color)
    base = over(base, Image.open(f'{T}/item/leather_{name}_overlay.png'))
    stripe_rows(base, stripes, SIL)
    return base

os.makedirs(f'{OUT}/textures/item', exist_ok=True)
os.makedirs(f'{OUT}/textures/entity/equipment/humanoid', exist_ok=True)
os.makedirs(f'{OUT}/textures/entity/equipment/humanoid_leggings', exist_ok=True)
hat = item('helmet', YEL)
# A white hard-hat ridge down the middle.
px = hat.load()
for y in range(16):
    for x in (7, 8):
        if px[x, y][3] and y < 6: px[x, y] = (255, 236, 150, 255)
hat.save(f'{OUT}/textures/item/hard_hat.png')
item('chestplate', ORA, stripes=(7, 10)).save(f'{OUT}/textures/item/hazmat_suit.png')
item('leggings', ORA, stripes=(9,)).save(f'{OUT}/textures/item/insulated_trousers.png')
item('boots', BLK).save(f'{OUT}/textures/item/rubber_boots.png')

# Worn layer: helmet (rows 0-15) yellow, body and arms (rows 16-31, x 16-56) orange with
# reflective bands, boots (legs, x 0-16) black rubber.
hum = Image.open(f'{T}/entity/equipment/humanoid/leather.png').convert('RGBA')
hum = tint(hum, YEL, (0, 0, 64, 16))
hum = tint(hum, ORA, (16, 16, 56, 32))
hum = tint(hum, BLK, (0, 16, 16, 32))
over(hum, Image.open(f'{T}/entity/equipment/humanoid/leather_overlay.png'))
stripe_rows(hum, (24, 27), SIL, (16, 16, 56, 32))
hum.save(f'{OUT}/textures/entity/equipment/humanoid/hazmat.png')
leg = Image.open(f'{T}/entity/equipment/humanoid_leggings/leather.png').convert('RGBA')
leg = tint(leg, ORA)
over(leg, Image.open(f'{T}/entity/equipment/humanoid_leggings/leather_overlay.png'))
stripe_rows(leg, (27,), SIL, (0, 16, 16, 32))
leg.save(f'{OUT}/textures/entity/equipment/humanoid_leggings/hazmat.png')

# Preview sheet, scaled up.
sheet = Image.new('RGBA', (16 * 4 * 8 + 64 * 6 * 2, 32 * 6), (60, 60, 70, 255))
for i, n in enumerate(['hard_hat', 'hazmat_suit', 'insulated_trousers', 'rubber_boots']):
    im = Image.open(f'{OUT}/textures/item/{n}.png').resize((128, 128), Image.NEAREST)
    sheet.alpha_composite(im, (i * 128, 0))
sheet.alpha_composite(hum.resize((384, 192), Image.NEAREST), (512, 0))
sheet.alpha_composite(leg.resize((384, 192), Image.NEAREST), (512 + 384, 0))
sheet.save(sys.argv[3])
