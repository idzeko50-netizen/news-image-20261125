#!/usr/bin/env python3
"""Draw the news-image-20261125 front page: entry/entry.png, 1024x1024.

A cream-paper newspaper front page summing up Wednesday 25 November 2026:
giant date headline, number strip, region bar, 3 large + 10 small
illustrated panels, a world map with numbered pins, a 17-story index, a
DATE CHECK box and a footer. Every illustration is drawn in code with PIL.
"""

import math
import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (247, 241, 227)
INK = (26, 26, 26)
RED = (164, 30, 34)
BLUE = (31, 78, 121)
GOLD = (176, 132, 40)
GREY = (110, 104, 92)
RULE = (60, 54, 44)
SKY = (174, 205, 225)
SEA = (140, 178, 205)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


SERIF_B = lambda s: font("DejaVuSerif-Bold.ttf", s)   # noqa: E731
SERIF = lambda s: font("DejaVuSerif.ttf", s)         # noqa: E731
SANS_B = lambda s: font("DejaVuSans-Bold.ttf", s)    # noqa: E731
SANS = lambda s: font("DejaVuSans.ttf", s)           # noqa: E731


def text_w(draw, text, fnt):
    return draw.textlength(text, font=fnt)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns list of lines, each fitting max_w."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if text_w(draw, trial, fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_lines(draw, text, fnt, max_w, max_lines):
    """Wrap and assert the text fits in max_lines; returns the lines."""
    lines = wrap(draw, text, fnt, max_w)
    assert len(lines) <= max_lines, (
        "overflow: %r wraps to %d lines (max %d)" % (text, len(lines), max_lines)
    )
    return lines


def draw_lines(draw, lines, x, y, fnt, fill, leading):
    for i, line in enumerate(lines):
        draw.text((x, y + i * leading), line, font=fnt, fill=fill)
    return y + len(lines) * leading


# ---------------------------------------------------------------- data
# (number, tag, headline, deck, region, lon, lat, scene)
FEATURED = [
    (1, "SPACE · CHINA",
     "China launches Shenzhou-24 with Pakistan's first astronaut",
     "Zeeshan Ali joins the crew from Jiuquan — the first foreign "
     "astronaut on a Chinese mission.", "Asia", 100.0, 40.0, "rocket"),
    (2, "TECH · USA",
     "Huawei convicted in US over trade secrets",
     "A jury finds the Chinese firm guilty of conspiracy to steal trade "
     "secrets and bank fraud.", "Americas", -77.0, 39.0, "court"),
    (3, "MIDDLE EAST",
     "Houthis hit Riyadh's tallest tower again",
     "A drone strike on the PIF tower wounds 11 people — the second attack "
     "on the skyscraper in a week.", "Middle East", 46.7, 24.7, "tower"),
    (4, "USA",
     "Trump: Huang pardon 'always an option'",
     "He also floats a US government stake in Nvidia.", "Americas",
     -77.0, 38.9, "whitehouse"),
    (5, "MIDDLE EAST",
     "Hamas security chief killed in Gaza strike",
     "Seven die in Israeli strikes despite the ceasefire.",
     "Middle East", 34.5, 31.5, "gaza"),
    (6, "ASIA · CHINA",
     "Shanghai chief probed in widening purge",
     "The fourth Politburo member investigated since 2025.",
     "Asia", 121.5, 31.2, "shanghai"),
    (7, "AFRICA · SPORT",
     "Senegal get the Africa Cup back",
     "CAS restores their 1–0 final win over Morocco, ten months on.",
     "Africa", -17.4, 14.7, "trophy"),
    (8, "USA",
     "Trump pardons turkeys Freedom and Feathers",
     "The annual Thanksgiving ceremony spares two birds.", "Americas",
     -77.0, 38.8, "turkey"),
    (9, "EUROPE",
     "Kyiv confirms it hit a Russian ship",
     "Ukraine struck a cargo vessel in the Gulf of Finland.",
     "Europe", 23.0, 60.0, "ship"),
    (10, "OCEANIA",
     "Magnitude 5.9 quake off Antarctica",
     "The tremor strikes the remote Balleny Islands region.", "Oceania",
     163.0, -66.0, "quake"),
    (11, "EUROPE",
     "Sweden to vote on Kristersson as PM",
     "A 30 Nov vote aims to end 72 days without a government.",
     "Europe", 18.1, 59.3, "parliament"),
    (12, "EUROPE",
     "Pelicot attacks book using her photos",
     "She slams a publisher over her ex-husband's photos.",
     "Europe", 2.3, 46.5, "book"),
    (13, "ASIA · UN",
     "India: keep humans in charge of AI weapons",
     "India urges human oversight of AI in war.", "Asia",
     -74.0, 40.7, "un"),
]

INDEX = [
    "Huang apologises to staff, says he is in therapy",
    "CIA and ODNI suffer breach of unclassified data",
    "US charges 800+ in biggest anti-scam sweep",
    "Eisenkot clinches first coalition deal",
    "Gukesh holds Sindarov to a draw in chess Game 1",
    "Landmine toll hits 5-year high: 6,929 hurt",
    "Huckabee doubts Israel aid ends this year",
    "Russia calls Ukraine 'neo-Nazi' in UN showdown",
    "Iran's Araghchi accuses US of hypocrisy at OPCW",
    "Copa America returns to the US in 2028",
    "Peru cuts 2026 growth forecast to 3.1%",
    "FAA 'line up and wait' rule takes effect",
    "Santas and a polar bear wash up in Bulgaria",
    "Xi delays retaliatory rare-earths ban",
    "Houthis advance to within 60 km of Aden",
    "Bangladesh PM meets Jamaat-linked students",
    "Goldman sees gold at $4,650 by 2027",
]

NUMBERS = [
    ("11", "wounded in Riyadh strike"),
    ("800+", "charged in US scam sweep"),
    ("6,929", "landmine casualties in 2025"),
    ("5.9", "Balleny Islands quake"),
    ("$4,650", "Goldman gold call for 2027"),
    ("60 km", "Houthis from Aden"),
]

REGIONS = [
    ("Europe", 5, (31, 78, 121)),
    ("Americas", 9, (164, 30, 34)),
    ("Asia", 5, (176, 132, 40)),
    ("Middle East", 6, (110, 70, 20)),
    ("Africa", 1, (46, 120, 70)),
    ("Oceania", 1, (20, 110, 120)),
    ("Global", 3, (110, 104, 92)),
]

DATE_CHECK = [
    "NOT TODAY — all 24 Nov:",
    "Korea jet in Russian airspace",
    "Kyiv strikes kill 14",
    "Luanda summit opens",
    "Nvidia shares +31%",
    "Chess title match opens",
]

# ---------------------------------------------------------------- scenes
def scene_rocket(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(24, 34, 58))
    for sx, sy in [(0.12, 0.2), (0.85, 0.15), (0.7, 0.35), (0.25, 0.55),
                   (0.9, 0.6), (0.45, 0.12)]:
        px, py = x + w * sx, y + h * sy
        d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(255, 255, 255))
    cx = x + w * 0.5
    d.polygon([(cx, y + h * 0.08), (cx - w * 0.07, y + h * 0.28),
               (cx + w * 0.07, y + h * 0.28)], fill=RED)
    d.rectangle([cx - w * 0.07, y + h * 0.28, cx + w * 0.07, y + h * 0.62],
                fill=(240, 240, 235))
    d.rectangle([cx - w * 0.07, y + h * 0.42, cx + w * 0.07, y + h * 0.48],
                fill=RED)
    d.polygon([(cx - w * 0.07, y + h * 0.62), (cx - w * 0.13, y + h * 0.72),
               (cx - w * 0.07, y + h * 0.68)], fill=RED)
    d.polygon([(cx + w * 0.07, y + h * 0.62), (cx + w * 0.13, y + h * 0.72),
               (cx + w * 0.07, y + h * 0.68)], fill=RED)
    d.polygon([(cx - w * 0.05, y + h * 0.62), (cx + w * 0.05, y + h * 0.62),
               (cx + w * 0.1, y + h * 0.9), (cx - w * 0.1, y + h * 0.9)],
              fill=(255, 170, 40))
    d.ellipse([cx - w * 0.035, y + h * 0.3, cx + w * 0.035, y + h * 0.38],
              fill=SKY, outline=INK)


def scene_court(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(232, 222, 196))
    d.rectangle([x + w * 0.1, y + h * 0.78, x + w * 0.9, y + h * 0.86],
                fill=(120, 84, 50))
    cx = x + w * 0.5
    d.line([cx, y + h * 0.14, cx, y + h * 0.78], fill=(70, 50, 30),
           width=max(3, int(h * 0.05)))
    d.line([cx - w * 0.3, y + h * 0.2, cx + w * 0.3, y + h * 0.2],
           fill=(70, 50, 30), width=max(3, int(h * 0.05)))
    d.ellipse([cx - w * 0.03, y + h * 0.08, cx + w * 0.03, y + h * 0.14],
              fill=GOLD)
    for side in (-1, 1):
        px = cx + side * w * 0.3
        d.line([px, y + h * 0.2, px, y + h * 0.42], fill=(70, 50, 30),
               width=2)
        d.polygon([(px - w * 0.1, y + h * 0.42), (px + w * 0.1, y + h * 0.42),
                   (px, y + h * 0.56)], fill=GOLD, outline=(70, 50, 30))


def scene_tower(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(208, 222, 232))
    d.rectangle([x, y + h * 0.75, x + w, y + h], fill=(150, 160, 150))
    tx = x + w * 0.42
    d.polygon([(tx, y + h * 0.06), (tx + w * 0.16, y + h * 0.06),
               (tx + w * 0.16, y + h * 0.75), (tx, y + h * 0.75)],
              fill=(70, 90, 110))
    for i in range(6):
        yy = y + h * (0.14 + i * 0.1)
        d.rectangle([tx + 2, yy, tx + w * 0.16 - 2, yy + h * 0.04],
                    fill=(200, 220, 235))
    d.ellipse([tx + w * 0.2, y + h * 0.08, tx + w * 0.36, y + h * 0.24],
              fill=(150, 150, 150))
    d.ellipse([tx + w * 0.28, y + h * 0.02, tx + w * 0.42, y + h * 0.14],
              fill=(170, 170, 170))
    d.rectangle([x + w * 0.1, y + h * 0.55, x + w * 0.35, y + h * 0.75],
                fill=(90, 105, 125))
    d.rectangle([x + w * 0.68, y + h * 0.6, x + w * 0.92, y + h * 0.75],
                fill=(100, 112, 130))


def scene_whitehouse(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(178, 208, 228))
    d.rectangle([x, y + h * 0.78, x + w, y + h], fill=(90, 130, 80))
    d.rectangle([x + w * 0.2, y + h * 0.42, x + w * 0.8, y + h * 0.78],
                fill=(245, 244, 238))
    d.ellipse([x + w * 0.42, y + h * 0.24, x + w * 0.58, y + h * 0.46],
              fill=(245, 244, 238))
    for i in range(5):
        cx = x + w * (0.27 + i * 0.115)
        d.rectangle([cx, y + h * 0.5, cx + w * 0.04, y + h * 0.78],
                    fill=(220, 218, 208))
    d.rectangle([x + w * 0.2, y + h * 0.38, x + w * 0.8, y + h * 0.44],
                fill=(230, 228, 218))
    d.line([x + w * 0.88, y + h * 0.1, x + w * 0.88, y + h * 0.55],
           fill=INK, width=2)
    d.polygon([(x + w * 0.88, y + h * 0.1), (x + w * 0.98, y + h * 0.16),
               (x + w * 0.88, y + h * 0.22)], fill=RED)


def scene_gaza(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(222, 200, 170))
    d.rectangle([x, y + h * 0.72, x + w, y + h], fill=(160, 140, 115))
    for bx, bh, bw in [(0.06, 0.5, 0.16), (0.26, 0.62, 0.18),
                       (0.5, 0.45, 0.15), (0.7, 0.58, 0.2)]:
        d.rectangle([x + w * bx, y + h * (0.72 - bh), x + w * (bx + bw),
                     y + h * 0.72], fill=(120, 105, 85))
    d.ellipse([x + w * 0.44, y + h * 0.04, x + w * 0.62, y + h * 0.22],
              fill=(160, 160, 160))
    d.ellipse([x + w * 0.52, y + h * 0.14, x + w * 0.68, y + h * 0.3],
              fill=(140, 140, 140))
    d.line([x + w * 0.15, y + h * 0.2, x + w * 0.3, y + h * 0.35],
           fill=(90, 90, 90), width=2)


def scene_shanghai(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(200, 214, 230))
    d.rectangle([x, y + h * 0.78, x + w, y + h], fill=(70, 90, 110))
    cx = x + w * 0.5
    d.line([cx, y + h * 0.08, cx, y + h * 0.78], fill=INK, width=3)
    d.ellipse([cx - w * 0.09, y + h * 0.18, cx + w * 0.09, y + h * 0.34],
              fill=RED)
    d.ellipse([cx - w * 0.06, y + h * 0.48, cx + w * 0.06, y + h * 0.6],
              fill=RED)
    for bx, bh, bw in [(0.06, 0.4, 0.14), (0.24, 0.55, 0.12),
                       (0.68, 0.5, 0.12), (0.84, 0.38, 0.12)]:
        d.rectangle([x + w * bx, y + h * (0.78 - bh), x + w * (bx + bw),
                     y + h * 0.78], fill=(60, 75, 95))
    for i in range(4):
        yy = y + h * (0.3 + i * 0.12)
        d.rectangle([x + w * 0.08, yy, x + w * 0.18, yy + h * 0.04],
                    fill=(230, 220, 140))


def scene_trophy(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(40, 110, 70))
    cx = x + w * 0.5
    d.polygon([(cx - w * 0.2, y + h * 0.16), (cx + w * 0.2, y + h * 0.16),
               (cx + w * 0.13, y + h * 0.48), (cx - w * 0.13, y + h * 0.48)],
              fill=GOLD)
    d.arc([cx - w * 0.3, y + h * 0.14, cx - w * 0.08, y + h * 0.42],
          90, 270, fill=GOLD, width=max(3, int(h * 0.05)))
    d.arc([cx + w * 0.08, y + h * 0.14, cx + w * 0.3, y + h * 0.42],
          270, 90, fill=GOLD, width=max(3, int(h * 0.05)))
    d.rectangle([cx - w * 0.05, y + h * 0.48, cx + w * 0.05, y + h * 0.62],
                fill=GOLD)
    d.rectangle([cx - w * 0.14, y + h * 0.62, cx + w * 0.14, y + h * 0.7],
                fill=GOLD)
    for sx, sy, c in [(0.15, 0.2, RED), (0.85, 0.25, (255, 255, 255)),
                      (0.8, 0.7, RED), (0.18, 0.75, (255, 255, 255)),
                      (0.5, 0.08, RED)]:
        d.rectangle([x + w * sx, y + h * sy, x + w * sx + 4, y + h * sy + 4],
                    fill=c)


def scene_turkey(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(222, 200, 160))
    cx, cy = x + w * 0.5, y + h * 0.6
    for i, ang in enumerate(range(-70, 71, 28)):
        rad = math.radians(ang - 90)
        ex = cx + w * 0.26 * math.cos(rad)
        ey = cy + h * 0.26 * math.sin(rad)
        d.ellipse([ex - w * 0.07, ey - h * 0.1, ex + w * 0.07, ey + h * 0.1],
                  fill=(150, 90, 50))
    d.ellipse([cx - w * 0.16, cy - h * 0.12, cx + w * 0.16, cy + h * 0.22],
              fill=(120, 70, 40))
    d.ellipse([cx - w * 0.07, cy - h * 0.26, cx + w * 0.07, cy - h * 0.08],
              fill=(150, 90, 50))
    d.polygon([(cx + w * 0.05, cy - h * 0.2), (cx + w * 0.13, cy - h * 0.14),
               (cx + w * 0.05, cy - h * 0.1)], fill=(230, 180, 60))
    d.ellipse([cx + w * 0.02, cy - h * 0.24, cx + w * 0.05, cy - h * 0.2],
              fill=INK)
    d.line([cx - w * 0.05, cy + h * 0.22, cx - w * 0.05, cy + h * 0.32],
           fill=(230, 180, 60), width=3)
    d.line([cx + w * 0.05, cy + h * 0.22, cx + w * 0.05, cy + h * 0.32],
           fill=(230, 180, 60), width=3)


def scene_ship(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(168, 200, 222))
    d.rectangle([x, y + h * 0.62, x + w, y + h], fill=SEA)
    for i in range(3):
        yy = y + h * (0.68 + i * 0.1)
        d.arc([x + w * 0.05, yy, x + w * 0.95, yy + h * 0.08], 0, 180,
              fill=(255, 255, 255), width=2)
    cx = x + w * 0.5
    d.polygon([(cx - w * 0.34, y + h * 0.5), (cx + w * 0.34, y + h * 0.5),
               (cx + w * 0.28, y + h * 0.62), (cx - w * 0.28, y + h * 0.62)],
              fill=(120, 40, 40))
    for i, c in enumerate([(200, 60, 60), (60, 120, 200), (220, 180, 60)]):
        bx = cx - w * 0.26 + i * w * 0.16
        d.rectangle([bx, y + h * 0.3, bx + w * 0.12, y + h * 0.5], fill=c)
    d.line([cx + w * 0.05, y + h * 0.3, cx + w * 0.05, y + h * 0.18],
           fill=INK, width=2)
    d.ellipse([cx + w * 0.3, y + h * 0.12, cx + w * 0.34, y + h * 0.16],
              fill=INK)
    d.ellipse([cx + w * 0.38, y + h * 0.2, cx + w * 0.42, y + h * 0.24],
              fill=INK)


def scene_quake(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(210, 226, 238))
    d.rectangle([x, y + h * 0.6, x + w, y + h], fill=(90, 120, 150))
    pts = []
    n = 24
    for i in range(n + 1):
        px = x + w * 0.05 + (w * 0.9) * i / n
        amp = h * 0.08 if i % 5 in (2, 3) else h * 0.02
        py = y + h * 0.3 + (amp if i % 2 else -amp)
        pts.append((px, py))
    d.line(pts, fill=RED, width=3, joint="curve")
    d.line([x, y + h * 0.6, x + w * 0.4, y + h * 0.72, x + w * 0.42,
            y + h * 0.6], fill=(60, 80, 100), width=2)
    d.polygon([(x + w * 0.7, y + h * 0.6), (x + w * 0.78, y + h * 0.42),
               (x + w * 0.86, y + h * 0.6)], fill=(255, 255, 255))
    d.polygon([(x + w * 0.7, y + h * 0.6), (x + w * 0.86, y + h * 0.6),
               (x + w * 0.78, y + h * 0.52)], fill=(200, 220, 235))


def scene_parliament(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(190, 205, 225))
    d.rectangle([x, y + h * 0.78, x + w, y + h], fill=(100, 130, 90))
    d.rectangle([x + w * 0.15, y + h * 0.4, x + w * 0.85, y + h * 0.78],
                fill=(240, 238, 228))
    d.polygon([(x + w * 0.15, y + h * 0.4), (x + w * 0.5, y + h * 0.2),
               (x + w * 0.85, y + h * 0.4)], fill=(225, 222, 210))
    for i in range(4):
        cx = x + w * (0.24 + i * 0.16)
        d.rectangle([cx, y + h * 0.46, cx + w * 0.05, y + h * 0.78],
                    fill=(210, 207, 195))
    d.line([x + w * 0.88, y + h * 0.08, x + w * 0.88, y + h * 0.5],
           fill=INK, width=2)
    d.rectangle([x + w * 0.88, y + h * 0.08, x + w * 0.99, y + h * 0.2],
                fill=(0, 90, 160))
    d.rectangle([x + w * 0.88, y + h * 0.12, x + w * 0.99, y + h * 0.15],
                fill=(250, 200, 0))
    d.rectangle([x + w * 0.925, y + h * 0.08, x + w * 0.945, y + h * 0.2],
                fill=(250, 200, 0))


def scene_book(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(228, 214, 190))
    cx, cy = x + w * 0.5, y + h * 0.55
    d.polygon([(cx - w * 0.34, y + h * 0.2), (cx, y + h * 0.3),
               (cx, y + h * 0.78), (cx - w * 0.34, y + h * 0.68)],
              fill=(245, 242, 232))
    d.polygon([(cx + w * 0.34, y + h * 0.2), (cx, y + h * 0.3),
               (cx, y + h * 0.78), (cx + w * 0.34, y + h * 0.68)],
              fill=(235, 231, 218))
    for i in range(3):
        yy = y + h * (0.34 + i * 0.1)
        d.line([cx - w * 0.28, yy, cx - w * 0.06, yy + h * 0.03],
               fill=GREY, width=1)
        d.line([cx + w * 0.06, yy + h * 0.03, cx + w * 0.28, yy],
               fill=GREY, width=1)
    d.line([cx - w * 0.3, y + h * 0.14, cx + w * 0.3, y + h * 0.86],
           fill=RED, width=max(4, int(h * 0.06)))
    d.line([cx - w * 0.3, y + h * 0.86, cx + w * 0.3, y + h * 0.14],
           fill=RED, width=max(4, int(h * 0.06)))


def scene_un(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(196, 212, 228))
    d.rectangle([x + w * 0.3, y + h * 0.2, x + w * 0.55, y + h * 0.78],
                fill=(120, 140, 165))
    for i in range(7):
        yy = y + h * (0.26 + i * 0.07)
        d.rectangle([x + w * 0.32, yy, x + w * 0.53, yy + h * 0.03],
                    fill=(210, 225, 240))
    d.rectangle([x + w * 0.58, y + h * 0.55, x + w * 0.85, y + h * 0.78],
                fill=(100, 120, 145))
    cx, cy = x + w * 0.72, y + h * 0.32
    d.rectangle([cx - w * 0.11, cy - h * 0.12, cx + w * 0.11, cy + h * 0.12],
                fill=(200, 210, 220), outline=INK)
    d.ellipse([cx - w * 0.05, cy - h * 0.05, cx - w * 0.01, cy - h * 0.01],
              fill=BLUE)
    d.ellipse([cx + w * 0.01, cy - h * 0.05, cx + w * 0.05, cy - h * 0.01],
              fill=BLUE)
    d.line([cx - w * 0.04, cy + h * 0.05, cx + w * 0.04, cy + h * 0.05],
           fill=INK, width=2)
    d.line([cx - w * 0.11, cy - h * 0.16, cx - w * 0.06, cy - h * 0.12],
           fill=INK, width=2)
    d.line([cx + w * 0.11, cy - h * 0.16, cx + w * 0.06, cy - h * 0.12],
           fill=INK, width=2)


SCENES = {
    "rocket": scene_rocket, "court": scene_court, "tower": scene_tower,
    "whitehouse": scene_whitehouse, "gaza": scene_gaza,
    "shanghai": scene_shanghai, "trophy": scene_trophy,
    "turkey": scene_turkey, "ship": scene_ship, "quake": scene_quake,
    "parliament": scene_parliament, "book": scene_book, "un": scene_un,
}

# ---------------------------------------------------------------- layout
def draw_panel(d, item, x, y, w, h, large):
    num, tag, head, deck, region, lon, lat, scene = item
    scene_h = 108 if large else 62
    d.rectangle([x, y, x + w, y + h], outline=RULE, width=1)
    SCENES[scene](d, x + 1, y + 1, w - 2, scene_h)
    d.rectangle([x, y + scene_h + 1, x + w, y + scene_h + 1 + 20],
                fill=RED)
    d.text((x + 8, y + scene_h + 5), "%d · %s" % (num, tag),
           font=SANS_B(10 if large else 9), fill=(255, 255, 255))
    tx = x + 8
    tw = w - 16
    head_f = SANS_B(17 if large else 13)
    deck_f = SANS(12 if large else 11)
    head_lines = fit_lines(d, head, head_f, tw, 2)
    y2 = draw_lines(d, head_lines, tx, y + scene_h + 28, head_f, INK,
                    20 if large else 15)
    deck_lines = fit_lines(d, deck, deck_f, tw, 2)
    draw_lines(d, deck_lines, tx, y2 + 2, deck_f, (60, 58, 52),
               15 if large else 13)


def draw_map(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(214, 228, 236),
                outline=RULE, width=1)
    d.text((x + 6, y + 4), "WHERE IT HAPPENED", font=SANS_B(10), fill=INK)

    def px(lon):
        return x + 6 + (lon + 170.0) / 360.0 * (w - 12)

    def py(lat):
        return y + 18 + (75.0 - lat) / 135.0 * (h - 24)

    land = (150, 170, 140)
    # North America
    d.polygon([(px(-168), py(66)), (px(-140), py(70)), (px(-120), py(71)),
               (px(-95), py(70)), (px(-75), py(62)), (px(-60), py(50)),
               (px(-70), py(42)), (px(-80), py(32)), (px(-97), py(26)),
               (px(-105), py(20)), (px(-118), py(34)), (px(-125), py(48)),
               (px(-150), py(60))], fill=land)
    # South America
    d.polygon([(px(-80), py(10)), (px(-60), py(5)), (px(-35), py(-5)),
               (px(-40), py(-20)), (px(-55), py(-35)), (px(-65), py(-50)),
               (px(-70), py(-30)), (px(-75), py(-15)), (px(-80), py(0))],
              fill=land)
    # Europe
    d.polygon([(px(-10), py(36)), (px(-5), py(43)), (px(0), py(50)),
               (px(8), py(57)), (px(18), py(60)), (px(30), py(60)),
               (px(28), py(50)), (px(20), py(42)), (px(12), py(38)),
               (px(3), py(36))], fill=land)
    # Africa
    d.polygon([(px(-17), py(15)), (px(-10), py(30)), (px(10), py(35)),
               (px(30), py(32)), (px(43), py(12)), (px(40), py(-5)),
               (px(35), py(-20)), (px(20), py(-35)), (px(12), py(-18)),
               (px(8), py(0)), (px(-8), py(5))], fill=land)
    # Asia
    d.polygon([(px(30), py(60)), (px(45), py(68)), (px(70), py(72)),
               (px(100), py(76)), (px(130), py(72)), (px(160), py(66)),
               (px(178), py(65)), (px(160), py(60)), (px(140), py(40)),
               (px(122), py(32)), (px(110), py(20)), (px(100), py(8)),
               (px(90), py(22)), (px(77), py(8)), (px(70), py(25)),
               (px(55), py(25)), (px(45), py(40)), (px(35), py(45))],
              fill=land)
    # Australia
    d.polygon([(px(114), py(-22)), (px(130), py(-12)), (px(142), py(-11)),
               (px(150), py(-25)), (px(146), py(-38)), (px(130), py(-32)),
               (px(115), py(-33))], fill=land)

    offsets = {
        2: (-10, -16), 4: (-30, 6), 8: (18, 12), 13: (-36, -10),
        9: (6, -12), 11: (-24, -10), 12: (-6, 14),
    }
    for num, tag, head, deck, region, lon, lat, scene in FEATURED:
        mx, my = px(lon), py(lat)
        mx = min(max(mx, x + 12), x + w - 12)
        my = min(max(my, y + 26), y + h - 12)
        dx, dy = offsets.get(num, (0, 0))
        lx, ly = mx + dx, my + dy
        if (lx, ly) != (mx, my):
            d.line([mx, my, lx, ly], fill=INK, width=1)
        d.ellipse([lx - 7, ly - 7, lx + 7, ly + 7], fill=RED,
                  outline=(255, 255, 255), width=1)
        label = str(num)
        tw = text_w(d, label, SANS_B(9))
        d.text((lx - tw / 2, ly - 5), label, font=SANS_B(9),
               fill=(255, 255, 255))


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    mx = 24
    right = W - mx

    # Masthead
    d.line([mx, 10, right, 10], fill=RULE, width=2)
    d.line([mx, 14, right, 14], fill=RULE, width=1)
    d.text((mx, 22), "Wednesday 25 November 2026",
           font=SERIF_B(44), fill=INK)
    d.text((mx, 74),
           "Every story below happened, or was first reported, today — "
           "checked against today's reporting.",
           font=SERIF(15), fill=(70, 66, 58))

    # Number strip
    strip_y, strip_h = 100, 48
    cell_w = (right - mx) / 6.0
    for i, (num, label) in enumerate(NUMBERS):
        cx0 = mx + i * cell_w
        d.rectangle([cx0 + 1, strip_y, cx0 + cell_w - 1, strip_y + strip_h],
                    outline=RULE, width=1)
        d.text((cx0 + 8, strip_y + 3), num, font=SERIF_B(17), fill=RED)
        lab_lines = fit_lines(d, label, SANS(10), cell_w - 16, 2)
        draw_lines(d, lab_lines, cx0 + 8, strip_y + 24, SANS(10), INK, 11)

    # Region bar
    bar_y, bar_h = 152, 14
    total = sum(c for _, c, _ in REGIONS)
    assert total == 30, "region counts must sum to 30, got %d" % total
    bx = mx
    for name, count, color in REGIONS:
        seg = (right - mx) * count / total
        d.rectangle([bx, bar_y, bx + seg, bar_y + bar_h], fill=color)
        bx += seg
    d.rectangle([mx, bar_y, right, bar_y + bar_h], outline=RULE, width=1)
    lx = mx
    leg_y = 172
    for name, count, color in REGIONS:
        d.rectangle([lx, leg_y, lx + 9, leg_y + 9], fill=color)
        txt = "%s %d" % (name, count)
        d.text((lx + 12, leg_y - 1), txt, font=SANS(10), fill=INK)
        lx += 12 + text_w(d, txt, SANS(10)) + 14

    # Section label
    d.text((mx, 192), "THE DAY'S NEWS — 13 STORIES IN PICTURES",
           font=SANS_B(12), fill=RED)
    d.line([mx, 208, right, 208], fill=RULE, width=1)

    # Large panels: 3 across
    gap = 8
    lw = (right - mx - 2 * gap) / 3.0
    for i, item in enumerate(FEATURED[:3]):
        draw_panel(d, item, mx + i * (lw + gap), 214, lw, 208, True)

    # Small panels: two rows of five
    sw = (right - mx - 4 * gap) / 5.0
    for row in range(2):
        for col in range(5):
            item = FEATURED[3 + row * 5 + col]
            draw_panel(d, item, mx + col * (sw + gap),
                       428 + row * 158, sw, 150, False)

    # Bottom section: map + date check on the left, index on the right
    by = 746
    map_w, map_h = 340, 122
    draw_map(d, mx, by, map_w, map_h)
    dc_y = by + map_h + 8
    dc_h = 984 - dc_y
    d.rectangle([mx, dc_y, mx + map_w, dc_y + dc_h], outline=RULE, width=1)
    d.rectangle([mx, dc_y, mx + map_w, dc_y + 20], fill=INK)
    d.text((mx + 8, dc_y + 4), "DATE CHECK", font=SANS_B(11),
           fill=(255, 255, 255))
    check_f = SANS(11)
    lines = []
    for line in DATE_CHECK:
        lines.extend(fit_lines(d, line, check_f, map_w - 16, 2))
    draw_lines(d, lines, mx + 8, dc_y + 26, check_f, INK, 14)

    ix = mx + map_w + 16
    iw = right - ix
    d.text((ix, by), "ALSO TODAY — 17 MORE STORIES",
           font=SANS_B(12), fill=RED)
    d.line([ix, by + 16, right, by + 16], fill=RULE, width=1)
    col_w = (iw - 12) / 2.0
    idx_f = SANS(11)
    for i, text in enumerate(INDEX):
        col = i % 2
        row = i // 2
        x0 = ix + col * (col_w + 12)
        y0 = by + 22 + row * 24
        entry = "%d. %s" % (14 + i, text)
        entry_lines = fit_lines(d, entry, idx_f, col_w, 1)
        d.text((x0, y0), entry_lines[0], font=idx_f, fill=INK)

    # Footer
    d.line([mx, 992, right, 992], fill=RULE, width=1)
    d.text((mx, 998),
           "Drawn in code · 30 verified stories · 7 regions · "
           "The World in a Day",
           font=SANS(10), fill=GREY)
    d.text((right - text_w(d, "25 November 2026", SANS(10)), 998),
           "25 November 2026", font=SANS(10), fill=GREY)

    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "entry")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    img.save(path, "PNG", optimize=True)
    size = os.path.getsize(path)
    assert size <= 1048576, "entry.png too big: %d bytes" % size
    print("wrote %s (%d bytes)" % (path, size))


if __name__ == "__main__":
    main()
