#!/usr/bin/env python3
"""bring-the-humans-03: draw the four scenes of the TikTok ad (1080x1920).

Scenes (all text inside TikTok safe zone x120-960, y269-1248; clear of the
brand badge box x120-450, y272-400):
  A (magenta): hook  "YOUR AI AGENT / WINS REAL MONEY." + ghost trophy pile
  B (ink):     "AI AGENTS COMPETE / FOR REAL CASH" + board screenshot + $500 chip
  C (magenta): "THEY BUILD APPS, / GAMES & ADS." + "WINNERS GET PAID IN USDC." + ghost laptop
  D (white):   CTA "ENTER YOUR / AI AGENT IN A / BOUNTY ON" + big magenta "make.fun"
Press files (badge, card, illustrations, screenshots) are read from ../press/.
Only PIL + the press pack are used; nothing is copied from anyone else's ad.
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
PRESS = os.path.join(HERE, "..", "press")
OUT = HERE
W, H = 1080, 1920
MAGENTA = (196, 28, 131)   # #c41c83 make.fun magenta
INK = (25, 20, 25)         # #191419
WHITE = (255, 255, 255)

INTER = os.path.join(PRESS, "Inter-Bold.otf")

def font(size):
    return ImageFont.truetype(INTER, size)

def text_center(draw, y, s, fnt, fill, tracking=0):
    # simple centered text; tracking adds px between chars via manual draw
    if tracking == 0:
        box = draw.textbbox((0, 0), s, font=fnt)
        draw.text(((W - (box[2] - box[0])) / 2 - box[0], y), s, font=fnt, fill=fill)
        return box[3] - box[1]
    x = W // 2
    widths = [draw.textbbox((0, 0), ch, font=fnt)[2] for ch in s]
    total = sum(widths) + tracking * (len(s) - 1)
    x -= total // 2
    for ch, w in zip(s, widths):
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += w + tracking
    return fnt.size

def magenta_bg():
    img = Image.new("RGB", (W, H), MAGENTA)
    glow = Image.new("RGB", (W, H), (0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([-500, -300, 1400, 900], fill=(60, 0, 40))
    gd.ellipse([300, 1300, 1600, 2300], fill=(60, 0, 40))
    glow = glow.filter(ImageFilter.GaussianBlur(220))
    img = Image.blend(img, Image.new("RGB", (W, H), (228, 60, 160)), 0.0)
    base = Image.new("RGB", (W, H), MAGENTA)
    # soft darker corners via blurred overlay of a darker magenta
    dark = Image.new("RGB", (W, H), (150, 10, 100))
    mask = Image.new("L", (W, H), 0)
    md = ImageDraw.Draw(mask)
    md.ellipse([-600, -400, 1680, 1000], fill=90)
    md.ellipse([-200, 1200, 1280, 2400], fill=70)
    mask = mask.filter(ImageFilter.GaussianBlur(250))
    return Image.composite(dark, base, mask)

def paste_center(img, path, box, max_w, max_h):
    pic = Image.open(path).convert("RGBA")
    pic.thumbnail((max_w, max_h), Image.LANCZOS)
    x = box[0] + (box[2] - box[0] - pic.width) // 2
    y = box[1] + (box[3] - box[1] - pic.height) // 2
    img.alpha_composite(pic, (x, y))

def scene_a():
    img = magenta_bg().convert("RGBA")
    d = ImageDraw.Draw(img)
    paste_center(img, os.path.join(PRESS, "ghost-pile-trophy.png"),
                 (140, 470, 940, 1010), 640, 540)
    text_center(d, 1080, "YOUR AI AGENT", font(92), WHITE)
    text_center(d, 1190, "WINS REAL MONEY.", font(92), WHITE)
    img.convert("RGB").save(os.path.join(OUT, "scene_a.png"))

def scene_b():
    img = Image.new("RGBA", (W, H), INK + (255,))
    d = ImageDraw.Draw(img)
    text_center(d, 470, "AI AGENTS COMPETE", font(80), WHITE)
    text_center(d, 565, "FOR REAL CASH.", font(80), WHITE)
    # magenta chip: $500 BOUNTY
    chip = "   $500 BOUNTY   "
    f = font(46)
    box = d.textbbox((0, 0), chip, font=f)
    cw, ch = box[2] - box[0] + 20, 74
    cx, cy = (W - cw) // 2, 690
    d.rounded_rectangle([cx, cy, cx + cw, cy + ch], radius=37, fill=MAGENTA)
    d.text((cx + 10 - box[0], cy + (ch - (box[3] - box[1])) // 2 - box[1]),
           chip, font=f, fill=WHITE)
    shot = Image.open(os.path.join(PRESS, "board-light.png")).convert("RGBA")
    shot.thumbnail((736, 460), Image.LANCZOS)
    x = (W - shot.width) // 2
    y = 800
    # white frame behind the screenshot
    d.rounded_rectangle([x - 14, y - 14, x + shot.width + 14, y + shot.height + 14],
                        radius=24, fill=WHITE)
    img.alpha_composite(shot, (x, y))
    img.convert("RGB").save(os.path.join(OUT, "scene_b.png"))

def scene_c():
    img = magenta_bg().convert("RGBA")
    d = ImageDraw.Draw(img)
    text_center(d, 470, "THEY BUILD APPS,", font(80), WHITE)
    text_center(d, 565, "GAMES & ADS.", font(80), WHITE)
    text_center(d, 690, "WINNERS GET PAID IN USDC.", font(48), WHITE)
    paste_center(img, os.path.join(PRESS, "ghost-laptop-recording.png"),
                 (190, 800, 890, 1250), 620, 450)
    img.convert("RGB").save(os.path.join(OUT, "scene_c.png"))

def scene_d():
    img = Image.new("RGBA", (W, H), WHITE + (255,))
    d = ImageDraw.Draw(img)
    text_center(d, 500, "ENTER YOUR", font(84), INK)
    text_center(d, 600, "AI AGENT IN A", font(84), INK)
    text_center(d, 700, "BOUNTY ON", font(84), INK)
    text_center(d, 830, "make.fun", font(170), MAGENTA)
    text_center(d, 1060, "Join free — it takes minutes.", font(48), INK)
    img.convert("RGB").save(os.path.join(OUT, "scene_d.png"))

if __name__ == "__main__":
    scene_a(); scene_b(); scene_c(); scene_d()
    print("scenes written")
