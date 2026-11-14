"""Creates 16 dummy product photos + one room scene in static/img/demo/.
Run once:  python make_demo_images.py
Replace them later from the admin panel (Products > upload photo)."""
import math
import os
import random

from PIL import Image, ImageChops, ImageDraw, ImageFilter

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "img", "demo")
os.makedirs(OUT, exist_ok=True)
W, H = 900, 1200
random.seed(7)


def mix(c, f):
    return tuple(max(0, min(255, int(v * f))) for v in c)


def grain(img, amount=0.10):
    noise = Image.effect_noise(img.size, 60).convert("RGB")
    return Image.blend(img, ImageChops.multiply(img, noise), amount)


def backdrop(size=(W, H), top=(238, 230, 214), bottom=(214, 203, 182)):
    img = Image.new("RGB", size)
    d = ImageDraw.Draw(img)
    for y in range(size[1]):
        t = y / size[1]
        d.line([(0, y), (size[0], y)], fill=tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3)))
    return img


def twill(size, base, stripe=None, pin=0):
    img = Image.new("RGB", size, base)
    d = ImageDraw.Draw(img, "RGBA")
    for k in range(-size[1], size[0], 6):
        d.line([(k, 0), (k + size[1], size[1])], fill=(255, 255, 255, 16), width=2)
        d.line([(k + 3, 0), (k + 3 + size[1], size[1])], fill=(0, 0, 0, 20), width=1)
    if pin:
        for x in range(0, size[0], pin):
            d.line([(x, 0), (x, size[1])], fill=stripe or (255, 255, 255, 60), width=2)
    return grain(img, 0.14)


def jacket(base, stripe=None, pin=0, trim=(20, 20, 24)):
    bg = backdrop()
    tex = twill((W, H), base, stripe, pin)
    mask = Image.new("L", (W, H), 0)
    m = ImageDraw.Draw(mask)
    body = [(190, 330), (330, 250), (450, 330), (570, 250), (710, 330), (770, 1020), (130, 1020)]
    m.polygon(body, fill=255)
    m.polygon([(190, 330), (90, 360), (60, 900), (150, 920), (190, 330)], fill=255)
    m.polygon([(710, 330), (810, 360), (840, 900), (750, 920), (710, 330)], fill=255)
    shadow = mask.filter(ImageFilter.GaussianBlur(18)).point(lambda v: int(v * 0.35))
    bg.paste(Image.new("RGB", (W, H), (60, 50, 40)), (14, 24), shadow)
    bg.paste(tex, (0, 0), mask)
    d = ImageDraw.Draw(bg)
    d.polygon([(450, 330), (330, 250), (300, 420), (390, 560), (450, 700)], fill=mix(base, 0.82))
    d.polygon([(450, 330), (570, 250), (600, 420), (510, 560), (450, 700)], fill=mix(base, 0.82))
    d.line([(450, 700), (450, 1020)], fill=mix(base, 0.6), width=4)
    d.polygon([(380, 250), (450, 330), (520, 250), (450, 190)], fill=(246, 244, 240))
    d.polygon([(450, 330), (415, 270), (450, 600), (485, 270)], fill=trim)
    for y in (760, 860):
        d.ellipse([436, y, 464, y + 28], fill=(30, 30, 30))
    return bg


def kurta(base, trim=(209, 155, 83)):
    bg = backdrop()
    tex = twill((W, H), base)
    mask = Image.new("L", (W, H), 0)
    m = ImageDraw.Draw(mask)
    m.polygon([(250, 200), (400, 160), (500, 160), (650, 200), (840, 420), (760, 480), (690, 400),
               (720, 1080), (180, 1080), (210, 400), (140, 480), (60, 420)], fill=255)
    bg.paste(Image.new("RGB", (W, H), (70, 60, 50)), (12, 22), mask.filter(ImageFilter.GaussianBlur(18)).point(lambda v: int(v * 0.3)))
    bg.paste(tex, (0, 0), mask)
    d = ImageDraw.Draw(bg)
    d.polygon([(400, 160), (500, 160), (450, 330)], fill=mix(base, 0.7))
    d.line([(450, 330), (450, 560)], fill=trim, width=5)
    for y in range(380, 560, 45):
        d.ellipse([440, y, 460, y + 20], fill=trim)
    return bg


def folds(size, base, n=9, depth=0.30, phase=0.0, sheer=False):
    w, h = size
    img = Image.new("RGB", size)
    d = ImageDraw.Draw(img)
    for x in range(w):
        f = 1 - depth + depth * (0.5 + 0.5 * math.sin(x / w * math.pi * 2 * n + phase))
        f *= 1 - 0.10 * math.sin(x / w * math.pi * 2 * 2.3 + 1.3)
        d.line([(x, 0), (x, h)], fill=mix(base, f))
    if sheer:
        wash = Image.new("RGB", size, (255, 252, 244))
        img = Image.blend(img, wash, 0.35)
        d = ImageDraw.Draw(img, "RGBA")
        for y in range(0, h, 4):
            d.line([(0, y), (w, y)], fill=(255, 255, 255, 26))
    return grain(img, 0.10)


def parda(base, sheer=False, jacquard=False, rod=(176, 128, 56)):
    bg = backdrop((W, H), (240, 233, 218), (222, 212, 192))
    panel = folds((W, H - 170), base, n=9, sheer=sheer)
    if jacquard:
        d = ImageDraw.Draw(panel, "RGBA")
        for y in range(40, panel.height, 90):
            for x in range(0, W, 90):
                d.polygon([(x + 45, y), (x + 70, y + 25), (x + 45, y + 50), (x + 20, y + 25)], outline=(220, 180, 100, 90))
    bg.paste(panel, (0, 120))
    d = ImageDraw.Draw(bg)
    d.rounded_rectangle([0, 90, W, 112], radius=10, fill=rod)
    for x in range(40, W, 76):
        d.rounded_rectangle([x, 98, x + 26, 150], radius=8, outline=rod, width=5)
    return bg


def sheet(base, alt, style="stripe"):
    img = Image.new("RGB", (W, H), base)
    d = ImageDraw.Draw(img)
    if style == "stripe":
        for x in range(0, W, 70):
            d.rectangle([x, 0, x + 34, H], fill=alt)
    elif style == "motif":
        for y in range(0, H, 80):
            for x in range(0, W, 80):
                ox = 40 if (y // 80) % 2 else 0
                d.rounded_rectangle([x + ox + 22, y + 22, x + ox + 44, y + 44], radius=3, fill=alt)
    elif style == "satin":
        pass
    shade = Image.new("L", (W, H))
    sd = ImageDraw.Draw(shade)
    for i in range(0, W + H, 2):
        v = int(200 + 55 * math.sin(i / 70.0) * math.cos(i / 230.0))
        sd.line([(i, 0), (i - H, H)], fill=v, width=3)
    img = ImageChops.multiply(img, Image.merge("RGB", (shade, shade, shade)))
    if style == "satin":
        img = ImageChops.add(img, Image.merge("RGB", (shade.point(lambda v: max(0, v - 220)),) * 3), scale=0.5)
    img = Image.blend(img, ImageChops.multiply(img, img.point(lambda v: 255)), 0)
    return grain(img, 0.08)


def comforter(base, alt):
    img = sheet(base, alt, "stripe")
    d = ImageDraw.Draw(img, "RGBA")
    for x in range(0, W, 150):
        d.line([(x, 0), (x, H)], fill=(0, 0, 0, 60), width=3)
    for y in range(0, H, 150):
        d.line([(0, y), (W, y)], fill=(0, 0, 0, 60), width=3)
    return img.filter(ImageFilter.GaussianBlur(0.6))


def save(img, name):
    img.convert("RGB").save(os.path.join(OUT, name), "JPEG", quality=90, optimize=True, progressive=True)
    print("made", name)


# --- suits
save(jacket((54, 56, 62)), "suit-1.jpg")
save(jacket((28, 40, 72), stripe=(220, 222, 232, 70), pin=34), "suit-2.jpg")
save(jacket((18, 18, 20), trim=(40, 40, 46)), "suit-3.jpg")
save(jacket((178, 150, 108), trim=(120, 96, 64)), "suit-4.jpg")
# --- parda
save(parda((2, 106, 107)), "parda-1.jpg")
save(parda((240, 232, 214), sheer=True), "parda-2.jpg")
save(parda((150, 112, 44), jacquard=True), "parda-3.jpg")
save(parda((196, 176, 140)), "parda-4.jpg")
# --- clothing
save(kurta((246, 242, 232), trim=(209, 155, 83)), "clothing-1.jpg")
save(kurta((98, 108, 70), trim=(240, 232, 214)), "clothing-2.jpg")
save(jacket((44, 46, 52), trim=(209, 155, 83)), "clothing-3.jpg")
save(kurta((176, 132, 84), trim=(250, 246, 238)), "clothing-4.jpg")
# --- bed sheets
save(sheet((250, 246, 238), (2, 106, 107), "stripe"), "sheet-1.jpg")
save(sheet((236, 228, 210), (236, 228, 210), "satin"), "sheet-2.jpg")
save(sheet((250, 246, 238), (209, 155, 83), "motif"), "sheet-3.jpg")
save(comforter((70, 72, 78), (86, 88, 96)), "sheet-4.jpg")

# --- room scene (used by "Shop the room")
RW, RH = 2000, 1100
room = backdrop((RW, RH), (226, 214, 190), (204, 190, 164))
d = ImageDraw.Draw(room)
d.rectangle([0, 900, RW, RH], fill=(120, 92, 62))
d.rectangle([640, 170, 1360, 700], fill=(206, 226, 226))
d.rectangle([640, 170, 1360, 700], outline=(250, 246, 238), width=14)
d.line([(1000, 170), (1000, 700)], fill=(250, 246, 238), width=10)
room.paste(folds((330, 640), (2, 106, 107), n=5), (360, 150))
room.paste(folds((330, 640), (2, 106, 107), n=5, phase=1.2), (1310, 150))
d = ImageDraw.Draw(room)
d.rounded_rectangle([330, 130, 1670, 150], radius=9, fill=(176, 128, 56))
bed = sheet((250, 246, 238), (2, 106, 107), "stripe").resize((1000, 360))
d.rounded_rectangle([480, 590, 1520, 930], radius=22, fill=(110, 84, 56))
room.paste(bed, (500, 640))
d = ImageDraw.Draw(room)
d.rounded_rectangle([540, 590, 880, 690], radius=40, fill=(246, 242, 232))
d.rounded_rectangle([1120, 590, 1460, 690], radius=40, fill=(246, 242, 232))
d.rectangle([1640, 150, 1650, 940], fill=(70, 56, 44))
d.line([(1560, 260), (1730, 260)], fill=(70, 56, 44), width=10)
suit = jacket((54, 56, 62)).resize((300, 400))
room.paste(suit, (1560, 280))
save(grain(room, 0.06), "room.jpg")


# --- homepage banners (wide) and split banners
def wide_bg(w=2400, h=1000, top=(226, 214, 190), bottom=(204, 190, 164)):
    return backdrop((w, h), top, bottom)


def banner_suit():
    img = wide_bg(top=(214, 222, 220), bottom=(186, 198, 196))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 860, 2400, 1000], fill=(96, 78, 56))
    for i, (col, x) in enumerate([((54, 56, 62), 1010), ((28, 40, 72), 1430), ((178, 150, 108), 1850)]):
        j = jacket(col, stripe=(220, 222, 232, 70) if i == 1 else None, pin=34 if i == 1 else 0).resize((540, 720))
        d.rectangle([x + 268, 90, x + 272, 200], fill=(70, 56, 44))
        img.paste(j, (x - 60, 150))
    return grain(img, 0.05)


def banner_parda():
    img = wide_bg()
    d = ImageDraw.Draw(img)
    d.rectangle([0, 880, 2400, 1000], fill=(120, 92, 62))
    d.rectangle([1250, 160, 2150, 760], fill=(206, 226, 226))
    d.rectangle([1250, 160, 2150, 760], outline=(250, 246, 238), width=16)
    d.line([(1700, 160), (1700, 760)], fill=(250, 246, 238), width=10)
    img.paste(folds((420, 760), (2, 106, 107), n=6), (1090, 110))
    img.paste(folds((420, 760), (2, 106, 107), n=6, phase=1.4), (2090, 110))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([1040, 90, 2560, 114], radius=10, fill=(176, 128, 56))
    return grain(img, 0.05)


def banner_bed():
    img = wide_bg(top=(232, 224, 206), bottom=(210, 198, 174))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 880, 2400, 1000], fill=(120, 92, 62))
    d.rounded_rectangle([1150, 330, 2250, 800], radius=26, fill=(110, 84, 56))
    bed = sheet((250, 246, 238), (2, 106, 107), "stripe").resize((1060, 470))
    img.paste(bed, (1170, 420))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([1230, 340, 1590, 460], radius=46, fill=(246, 242, 232))
    d.rounded_rectangle([1810, 340, 2170, 460], radius=46, fill=(246, 242, 232))
    return grain(img, 0.05)


save(banner_suit(), "banner-suit.jpg")
save(banner_parda(), "banner-parda.jpg")
save(banner_bed(), "banner-bed.jpg")
