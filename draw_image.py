#!/usr/bin/env python3
"""Render the make.fun news-image-20261125 entry: one dense broadsheet of
25 November 2026 world news (3 heroes + 10 grid panels + 20 ALSO ON
one-liners = 33 stories). Deterministic: fixed palette, fixed fonts, no
randomness, no timestamps.
v1: new 3-hero format, dull newspaper-paper theme (like news-24 v3).
v2: fix grid-panel chip/label overlap (chip moved to the kicker row, label
gets the full row); shorten hero + grid descriptions so they fit their
line budgets (hero 2 lines, grid 4 lines) instead of truncating mid-sentence.
Run: python3 draw_image.py [out_path]  (default: entry.png next to this file)
"""
import os
import sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
FONT_DIR = "/usr/share/fonts/truetype/dejavu"
BOLD = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")
REG = os.path.join(FONT_DIR, "DejaVuSans.ttf")

# Palette — dull newspaper paper
PAPER = (237, 230, 214)      # #EDE6D6 base
BANNER_BG = (232, 223, 202)
PANEL = (246, 241, 229)      # #F6F1E5 panel background
PANEL_DARK = (228, 219, 198)  # #E4DBC6 darker panel / map bg
BORDER = (178, 166, 138)
AMBER = (138, 109, 27)       # #8A6D1B dark amber (headers, numbers)
WHITE = (246, 241, 229)      # paper-white (text on dark chips/bands)
MUTED = (96, 88, 74)
BODY = (56, 51, 44)          # body text on paper
BLUE = (46, 74, 98)          # #2E4A62 region blue
GREEN = (34, 110, 66)
RED = (163, 59, 46)          # #A33B2E claim red
SKY = (38, 74, 110)
SEA = (38, 62, 88)
INK = (27, 26, 23)           # #1B1A17 ink text

_font_cache = {}


def font(path, size):
    key = (path, size)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(path, size)
    return _font_cache[key]


def fit_font(text, path, max_size, max_w, min_size=8):
    """Largest font size <= max_size whose rendered width fits max_w."""
    size = max_size
    while size > min_size:
        f = font(path, size)
        if f.getlength(text) <= max_w:
            return f
        size -= 1
    return font(path, min_size)


def wrap_text(text, fnt, max_w):
    """Greedy word wrap; returns list of lines."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if fnt.getlength(trial) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def vgrad(draw, box, c1, c2, steps=24):
    x0, y0, x1, y1 = box
    h = max(1, y1 - y0)
    for i in range(steps):
        t = i / max(1, steps - 1)
        c = tuple(int(c1[j] + (c2[j] - c1[j]) * t) for j in range(3))
        yy0 = y0 + int(h * i / steps)
        yy1 = y0 + int(h * (i + 1) / steps)
        draw.rectangle([x0, yy0, x1, yy1], fill=c)


def dashed_line(draw, x1, y1, x2, y2, fill, dash=9, gap=6, width=2):
    import math
    dx, dy = x2 - x1, y2 - y1
    dist = math.hypot(dx, dy)
    if dist == 0:
        return
    ux, uy = dx / dist, dy / dist
    d = 0.0
    while d < dist:
        e = min(d + dash, dist)
        draw.line([x1 + ux * d, y1 + uy * d, x1 + ux * e, y1 + uy * e],
                  fill=fill, width=width)
        d = e + gap


def chip(draw, x, y, text, bg=BLUE, fg=WHITE, size=11):
    f = font(BOLD, size)
    tw = f.getlength(text)
    pad = 6
    draw.rounded_rectangle([x, y, x + tw + 2 * pad, y + size + 8],
                           radius=4, fill=bg)
    draw.text((x + pad, y + 4), text, font=f, fill=fg)
    return x + tw + 2 * pad


def kicker(draw, x, y, text, size=11):
    draw.text((x, y), text, font=font(BOLD, size), fill=BLUE)


def draw_skyline(draw, x0, y0, w, base_y, color, seed_heights):
    """Simple flat building silhouettes."""
    n = len(seed_heights)
    bw = w // n
    for i, hh in enumerate(seed_heights):
        bx = x0 + i * bw
        draw.rectangle([bx + 1, base_y - hh, bx + bw - 1, base_y], fill=color)


# ---------------------------------------------------------------- data
HEROES = [
    # (kicker, label, sub, chip, kind, description)
    ("EUROPE · WAR", "PUTIN: RETALIATION INEVITABLE",
     "Ukraine hits Samara refineries — Kyiv claims Baltic ship strike",
     "CONFIRMED", "putin",
     "Putin tells oil executives retaliation is inevitable as Ukrainian "
     "drones hit Samara refineries."),
    ("CHINA · SPACE", "PAKISTAN REACHES SPACE",
     "First foreign astronaut aboard China's Tiangong",
     "CONFIRMED", "space",
     "Shenzhou-24 launches at 00:18 UTC and docks at 03:56 UTC with "
     "Pakistan's first astronaut aboard."),
    ("PACIFIC · DIPLOMACY", "PACIFIC PACT SIGNED",
     "Solomons choose Australia — no foreign bases",
     "CONFIRMED", "pact",
     "Australia and Solomon Islands sign a treaty in Canberra; no foreign "
     "military base may be built."),
]

PANELS = [
    # (kicker, label, sub, chip, kind, description)
    ("ASIA · MARKETS", "AI SELL-OFF DEEPENS",
     "Nikkei −2.76% — S&P −2.2%", "CONFIRMED", "markets",
     "Asian tech falls on AI doubts: Nikkei −2.76%, Kospi −6%, Taiex "
     "~−5%. Wall Street follows: S&P −2.2%, Nasdaq ~−3.2%."),
    ("MIDDLE EAST · WAR", "GAZA: SECOND CHIEF KILLED",
     "Strike hits colonel's home — family dead", "CONFIRMED", "gaza",
     "An early airstrike kills Hamas colonel Abuelouf, his wife and two "
     "children in Beach camp — the second senior Hamas official killed in "
     "a day."),
    ("AMERICAS · CRIME", "CARTAGENA HOSTAGES FREED",
     "All freed after 17-hour siege — 1 gunman killed", "CONFIRMED",
     "cartagena",
     "Special forces storm an Éxito supermarket at ~01:00, ending a "
     "17-hour siege. All hostages freed; one gunman killed, four detained."),
    ("S. ASIA · LABOUR", "GARMENT PAY +36%",
     "Minimum wage Tk17,000 after weeks of protests", "CONFIRMED", "wage",
     "Bangladesh approves a 36% garment minimum-wage rise to Tk17,000 "
     "from 1 Dec. Workers wanted a doubling; protests cost the industry "
     "$428m."),
    ("MIDDLE EAST · WAR", "HOUTHIS CLAIM NEW STRIKES",
     "Ras Tanura refinery claim — unverified", "CLAIM", "houthis",
     "The Houthis say they hit Ras Tanura refinery and Riyadh's financial "
     "district. Refinery fires are unconfirmed; the Tue PIF strike is "
     "confirmed."),
    ("SE ASIA · DISASTER", "BOGOR MINE: 3 DEAD",
     "23 still trapped in flooded shaft", "CONFIRMED", "mine",
     "Rescuers recover three bodies from a flooded gold mine in Bogor; 23 "
     "miners remain trapped 100m down. The flood began Monday; 11 escaped."),
    ("CHINA · POLITICS", "SHANGHAI CHIEF PROBED",
     "4th Politburo member under graft inquiry", "CONFIRMED", "probe",
     "China's anti-graft watchdog investigates Politburo member Chen "
     "Jining, the Shanghai party chief — the fourth such inquiry since "
     "2025."),
    ("GLOBAL · TRADE", "TARIFFS HIT 14 NATIONS",
     "China 20% — Vietnam up to 35% — proposed", "CONFIRMED", "tariffs",
     "The US proposes duties on 14 partners: China 20%, Vietnam 20–35%, "
     "India 17–25%, EU 15%. A hearing is set for 25 January."),
    ("US · ECONOMY", "US GROWTH 4.3%",
     "GDP surges — core inflation 3.3%", "CONFIRMED", "gdp",
     "US Q3 GDP is revised up to 4.3%, the fastest in three years, above "
     "the 3.5% consensus. Core PCE runs at 3.3% y/y, largest since Nov "
     "2023."),
    ("SPACE · SCIENCE", "ASTEROID'S NEW CRATER",
     "Hera sees DART's stadium-sized scar", "CONFIRMED", "asteroid",
     "ESA unveils Hera's first images of Dimorphos: the 2022 DART impact "
     "left a crater spanning its width. The moonlet tumbles chaotically."),
]

# (text, region, flag) — flag "" | "PROPOSAL" | "CLAIM" | "UTC"
ALSO_ON = [
    ("Sparta II towed to St Petersburg — Kyiv says it carried weapons",
     "EUROPE", ""),
    ("Latvia weighs border closure; Moscow summons its diplomat",
     "EUROPE", ""),
    ("Sweden announces €48m winter aid for Ukraine", "EUROPE", ""),
    ("Poland plans limited no-fly zone on eastern border",
     "EUROPE", "PROPOSAL"),
    ("Iran says 2 tankers hit mines in Hormuz", "MIDDLE EAST", "CLAIM"),
    ("China reportedly orders 50 Boeing jets, ~$7.4bn", "ASIA", ""),
    ("Meningitis cases rising in Gaza, esp. infants", "MIDDLE EAST", ""),
    ("Sudan: drone strikes kill 19 in Blue Nile", "AFRICA", ""),
    ("Sánchez vs Feijóo debate ahead of Nov 29 snap vote", "EUROPE", ""),
    ("Norway to give Ukraine $7bn+ in 2027, air defence first",
     "EUROPE", ""),
    ("Poundland enters administration, ~11,000 jobs at risk",
     "EUROPE", ""),
    ("Zambia indicts opposition leader on treason charges", "AFRICA", ""),
    ("Iran flogs singer 74 times over unveiled concert",
     "MIDDLE EAST", ""),
    ("North Korea orders closure of Swiss diplomatic office", "ASIA", ""),
    ("Venezuela discloses ~$237.5bn public debt", "AMERICAS", ""),
    ("Argentina enters technical recession", "AMERICAS", ""),
    ("Australia inflation rises to 4.9%", "OCEANIA", ""),
    ("Chile teachers join nationwide strike", "AMERICAS", ""),
    ('Trump pardons turkeys "Freedom and Feathers"', "AMERICAS", ""),
    ("Ronaldo scores 987th career goal for Al Nassr", "ASIA", ""),
]

BIG_NUMBERS = ("36% WAGE  ·  4.3% GDP  ·  20% TARIFF  ·  −2.76% NIKKEI  ·  "
               "26 MINERS  ·  987 GOALS")

UTC_LINE = ("00:18 Shenzhou launches  ·  02:12 Samara hit  ·  03:56 Tiangong "
            "docks  ·  06:00 Cartagena freed  ·  13:30 US GDP 4.3%  ·  "
            "Canberra treaty signed")

REGION_COUNTS = ("EUROPE 9  ·  AMERICAS 8  ·  ASIA 7  ·  MIDDLE EAST 5  ·  "
                 "AFRICA 2  ·  OCEANIA 2")

# Coarse continent outlines (lon, lat) for the small world map.
CONTINENTS = [
    # North America
    [(-168, 66), (-140, 70), (-120, 72), (-95, 80), (-80, 73), (-75, 62),
     (-65, 60), (-55, 47), (-70, 42), (-75, 35), (-80, 26), (-85, 30),
     (-90, 21), (-97, 16), (-105, 20), (-115, 28), (-125, 40), (-125, 49),
     (-140, 60), (-165, 60)],
    # South America
    [(-80, 10), (-75, 5), (-60, 5), (-50, 0), (-40, -5), (-35, -10),
     (-40, -20), (-50, -30), (-60, -38), (-70, -52), (-73, -40), (-75, -20),
     (-80, -5), (-80, 5)],
    # Europe
    [(-10, 36), (-10, 43), (-2, 48), (0, 51), (5, 53), (8, 57), (10, 59),
     (18, 56), (21, 55), (28, 59), (30, 60), (25, 65), (20, 70), (12, 70),
     (5, 60), (-5, 50), (-9, 43)],
    # Africa
    [(-17, 15), (-10, 30), (0, 36), (10, 37), (20, 32), (32, 31), (35, 28),
     (40, 15), (43, 11), (48, 10), (51, 12), (40, 0), (35, -10), (30, -20),
     (25, -30), (20, -35), (15, -30), (12, -18), (8, -2), (9, 4), (-8, 4),
     (-13, 8)],
    # Asia
    [(30, 36), (40, 40), (50, 40), (60, 25), (65, 25), (70, 20), (75, 10),
     (80, 8), (85, 15), (90, 22), (95, 16), (100, 8), (105, 2), (110, 10),
     (115, 20), (120, 30), (122, 38), (127, 40), (130, 42), (135, 44),
     (140, 40), (142, 50), (140, 60), (160, 62), (170, 66), (180, 65),
     (170, 60), (160, 55), (150, 60), (140, 65), (130, 72), (120, 73),
     (110, 74), (100, 77), (90, 75), (80, 73), (70, 72), (60, 69),
     (50, 68), (40, 67), (35, 65), (30, 60), (28, 55), (30, 50), (30, 45)],
    # Australia
    [(113, -22), (114, -30), (115, -35), (120, -34), (130, -32), (135, -35),
     (140, -38), (145, -38), (150, -37), (153, -27), (150, -22), (145, -15),
     (142, -11), (137, -12), (135, -15), (130, -13), (126, -14), (122, -17),
     (118, -20)],
]
# (lon, lat) map markers: Samara, Jiuquan, Canberra, Tokyo, Gaza City,
# Cartagena, Dhaka, Ras Tanura, Bogor, Shanghai, Washington DC
MARKERS = [(51.5, 53.2), (98.5, 40.9), (149.1, -35.3), (139.7, 35.7),
           (34.5, 31.5), (-75.5, 10.4), (90.4, 23.8), (50.1, 26.6),
           (106.8, -6.6), (121.5, 31.2), (-77.0, 38.9)]


def illustration(draw, kind, x0, y0, w, h):
    """Flat illustration band inside a hero/panel (x0,y0,w,h)."""
    if kind == "putin":
        vgrad(draw, (x0, y0, x0 + w, y0 + h), (60, 72, 92), (40, 52, 72))
        # refinery towers with flame
        draw_skyline(draw, x0 + 8, y0, w - 16, y0 + h - 4,
                     (28, 38, 52), [16, 22, 14, 24, 18, 20, 15])
        draw.polygon([(x0 + 176, y0 + h - 4), (x0 + 196, y0 + h - 24),
                      (x0 + 216, y0 + h - 4)], fill=(220, 100, 40))
        draw.ellipse([x0 + 182, y0 + h - 28, x0 + 210, y0 + h - 10],
                     fill=(242, 168, 29))
        for cx, cy, r in [(x0 + 196, y0 + 8, 8), (x0 + 212, y0 + 5, 9)]:
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(130, 128, 122))
    elif kind == "space":
        vgrad(draw, (x0, y0, x0 + w, y0 + h), (28, 42, 72), (14, 24, 48))
        # stars
        for sx, sy in [(x0 + 30, y0 + 10), (x0 + 90, y0 + 18),
                       (x0 + 150, y0 + 8), (x0 + 240, y0 + 14),
                       (x0 + 280, y0 + 30), (x0 + 60, y0 + 34)]:
            draw.ellipse([sx - 1, sy - 1, sx + 1, sy + 1], fill=WHITE)
        # rocket
        rx = x0 + w // 2
        draw.polygon([(rx - 8, y0 + 8), (rx, y0 - 2), (rx + 8, y0 + 8)],
                     fill=RED)
        draw.rectangle([rx - 8, y0 + 8, rx + 8, y0 + h - 12],
                       fill=(246, 241, 229))
        draw.polygon([(rx - 8, y0 + h - 12), (rx - 16, y0 + h - 4),
                      (rx - 8, y0 + h - 6)], fill=RED)
        draw.polygon([(rx + 8, y0 + h - 12), (rx + 16, y0 + h - 4),
                      (rx + 8, y0 + h - 6)], fill=RED)
        draw.polygon([(rx - 5, y0 + h - 4), (rx, y0 + h + 2),
                      (rx + 5, y0 + h - 4)], fill=(242, 168, 29))
    elif kind == "pact":
        vgrad(draw, (x0, y0, x0 + w, y0 + h), (200, 212, 225), (170, 190, 210))
        # two flags: Australia (blue w/ stars) and Solomon Islands
        # (blue/green/yellow)
        for fx, stripes in ((x0 + 62, [(38, 74, 140), (38, 74, 140)]),
                            (x0 + w - 126, [(38, 74, 140), (60, 140, 70)])):
            draw.line([fx, y0 + 4, fx, y0 + h - 2], fill=(70, 66, 60), width=2)
            fw, fh = 62, 26
            sy = y0 + 5
            for j, col in enumerate(stripes):
                sh = fh // len(stripes)
                draw.rectangle([fx + 2, sy + j * sh,
                                fx + 2 + fw, sy + (j + 1) * sh], fill=col)
        # yellow stars on the Solomon flag
        for sx, sy in [(x0 + w - 120, y0 + 10), (x0 + w - 100, y0 + 20),
                       (x0 + w - 80, y0 + 12)]:
            draw.ellipse([sx - 2, sy - 2, sx + 2, sy + 2],
                         fill=(238, 198, 60))
        draw.line([x0 + 10, y0 + h - 2, x0 + w - 10, y0 + h - 2],
                  fill=(120, 112, 98), width=1)
    elif kind == "markets":
        vgrad(draw, (x0, y0, x0 + w, y0 + h), (228, 208, 205), (212, 188, 185))
        draw.line([(x0 + 12, y0 + 6), (x0 + w * 0.4, y0 + 12),
                   (x0 + w * 0.6, y0 + 22), (x0 + w - 12, y0 + h - 6)],
                  fill=RED, width=3, joint="curve")
        draw.polygon([(x0 + w - 26, y0 + h - 8), (x0 + w - 10, y0 + h - 8),
                      (x0 + w - 10, y0 + h - 24)], fill=RED)
    elif kind == "gaza":
        vgrad(draw, (x0, y0, x0 + w, y0 + h), (60, 72, 92), (40, 52, 72))
        draw_skyline(draw, x0 + 8, y0, w - 16, y0 + h - 4,
                     (28, 38, 52), [16, 22, 14, 24, 18, 20, 15])
        for wx, wy in [(x0 + 40, y0 + h - 18), (x0 + 120, y0 + h - 22),
                       (x0 + 210, y0 + h - 16)]:
            draw.rectangle([wx, wy, wx + 4, wy + 5], fill=(200, 150, 40))
        draw.polygon([(x0 + 150, y0 + h - 4), (x0 + 168, y0 + h - 22),
                      (x0 + 186, y0 + h - 4)], fill=(220, 100, 40))
        draw.ellipse([x0 + 156, y0 + h - 26, x0 + 180, y0 + h - 10],
                     fill=(242, 168, 29))
    elif kind == "cartagena":
        vgrad(draw, (x0, y0, x0 + w, y0 + h), (40, 52, 72), (28, 38, 52))
        # storefront with awning
        draw.rectangle([x0 + 30, y0 + 12, x0 + w - 30, y0 + h - 4],
                       fill=(120, 110, 95))
        for i in range(5):
            col = RED if i % 2 == 0 else WHITE
            draw.rectangle([x0 + 34 + i * 24, y0 + 12,
                            x0 + 34 + i * 24 + 24, y0 + 20], fill=col)
        draw.rectangle([x0 + 50, y0 + 22, x0 + w - 50, y0 + h - 4],
                       fill=(200, 180, 120))
        # flashing lights
        for lx, col in [(x0 + 14, RED), (x0 + w - 22, BLUE)]:
            draw.ellipse([lx, y0 + 6, lx + 8, y0 + 14], fill=col)
    elif kind == "wage":
        vgrad(draw, (x0, y0, x0 + w, y0 + h), (210, 222, 205), (185, 205, 180))
        f = fit_font("Tk17,000", BOLD, 22, w - 20)
        draw.text((x0 + 10, y0 + 6), "Tk17,000", font=f, fill=AMBER)
        draw.text((x0 + w - 60, y0 + h - 16), "+36%",
                  font=font(BOLD, 13), fill=GREEN)
    elif kind == "houthis":
        vgrad(draw, (x0, y0, x0 + w, y0 + h), (222, 208, 188), (205, 188, 165))
        draw_skyline(draw, x0 + 8, y0, w - 16, y0 + h - 4,
                     (140, 125, 105), [14, 18, 12, 20, 15])
        draw.polygon([(x0 + 120, y0 + h - 4), (x0 + 138, y0 + h - 22),
                      (x0 + 156, y0 + h - 4)], fill=(220, 100, 40))
        draw.ellipse([x0 + 126, y0 + h - 26, x0 + 150, y0 + h - 10],
                     fill=(242, 168, 29))
        for cx, cy, r in [(x0 + 138, y0 + 8, 8), (x0 + 154, y0 + 5, 9)]:
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(150, 146, 138))
    elif kind == "mine":
        vgrad(draw, (x0, y0, x0 + w, y0 + h), (60, 72, 92), (40, 52, 72))
        # shaft opening
        draw.rectangle([x0 + w // 2 - 30, y0 + 6, x0 + w // 2 + 30, y0 + h - 4],
                       fill=(20, 28, 40))
        # water line
        draw.rectangle([x0 + 8, y0 + h - 10, x0 + w - 8, y0 + h - 4],
                       fill=(60, 110, 150))
        # helmet lamp
        draw.ellipse([x0 + w // 2 - 6, y0 + 12, x0 + w // 2 + 6, y0 + 24],
                     fill=(242, 168, 29))
    elif kind == "probe":
        vgrad(draw, (x0, y0, x0 + w, y0 + h), (210, 222, 232), (185, 205, 220))
        # document with red seal
        draw.rectangle([x0 + w // 2 - 40, y0 + 4, x0 + w // 2 + 40, y0 + h - 4],
                       fill=WHITE, outline=BORDER)
        for i in range(3):
            draw.line([x0 + w // 2 - 32, y0 + 10 + i * 7,
                       x0 + w // 2 + 32, y0 + 10 + i * 7],
                      fill=MUTED, width=1)
        draw.ellipse([x0 + w // 2 + 18, y0 + h - 16,
                      x0 + w // 2 + 34, y0 + h], fill=RED)
    elif kind == "tariffs":
        vgrad(draw, (x0, y0, x0 + w, y0 + h), (210, 222, 205), (185, 205, 180))
        # stacked containers
        for cx, cy, col in [(x0 + 20, y0 + h - 22, (180, 90, 50)),
                            (x0 + 70, y0 + h - 22, (60, 110, 70)),
                            (x0 + 45, y0 + h - 34, (58, 108, 178))]:
            draw.rectangle([cx, cy, cx + 44, cy + 12], fill=col)
        f = fit_font("20%", BOLD, 22, 50)
        draw.text((x0 + w - 52, y0 + 6), "20%", font=f, fill=AMBER)
    elif kind == "gdp":
        vgrad(draw, (x0, y0, x0 + w, y0 + h), (205, 222, 205), (175, 200, 180))
        draw.line([(x0 + 12, y0 + h - 8), (x0 + w * 0.38, y0 + h - 22),
                   (x0 + w * 0.62, y0 + h - 14), (x0 + w - 12, y0 + 6)],
                  fill=GREEN, width=3, joint="curve")
        draw.polygon([(x0 + w - 28, y0 + 4), (x0 + w - 10, y0 + 4),
                      (x0 + w - 10, y0 + 20)], fill=GREEN)
        f = fit_font("4.3%", BOLD, 20, 60)
        draw.text((x0 + 10, y0 + 4), "4.3%", font=f, fill=AMBER)
    elif kind == "asteroid":
        vgrad(draw, (x0, y0, x0 + w, y0 + h), (28, 42, 72), (14, 24, 48))
        for sx, sy in [(x0 + 20, y0 + 8), (x0 + 60, y0 + 16),
                       (x0 + 150, y0 + 10)]:
            draw.ellipse([sx - 1, sy - 1, sx + 1, sy + 1], fill=WHITE)
        # cratered asteroid
        ax, ay, ar = x0 + w // 2, y0 + h // 2 + 4, 15
        draw.ellipse([ax - ar, ay - ar, ax + ar, ay + ar],
                     fill=(150, 140, 125))
        draw.ellipse([ax - 6, ay - 4, ax + 4, ay + 6], fill=(110, 100, 88))
        draw.ellipse([ax + 6, ay - 8, ax + 12, ay - 2], fill=(120, 110, 96))
        # boulders
        for bx, by, br in [(x0 + 30, y0 + h - 10, 4), (x0 + w - 34, y0 + 8, 3),
                           (x0 + w - 24, y0 + h - 8, 4)]:
            draw.ellipse([bx - br, by - br, bx + br, by + br],
                         fill=(150, 140, 125))


def draw_map(draw, x0, y0, w, h):
    """Simplified equirectangular world map with red markers."""
    draw.rectangle([x0, y0, x0 + w, y0 + h], fill=PANEL_DARK,
                   outline=BORDER)
    lat_top, lat_bot = 85.0, -55.0

    def proj(lon, lat):
        return (x0 + (lon + 180.0) / 360.0 * w,
                y0 + (lat_top - lat) / (lat_top - lat_bot) * h)

    for poly in CONTINENTS:
        pts = [proj(lon, lat) for lon, lat in poly]
        draw.polygon(pts, fill=(172, 164, 138), outline=(140, 130, 105))
    for lon, lat in MARKERS:
        mx, my = proj(lon, lat)
        draw.ellipse([mx - 5, my - 5, mx + 5, my + 5], fill=RED,
                     outline=WHITE, width=1)


def draw_also_on_item(draw, num, text, region, flag, x, y, w):
    """One numbered one-liner, wrapped to at most 2 lines, region in blue."""
    num_f = font(BOLD, 12)
    txt_f = font(REG, 11)
    reg_f = font(BOLD, 10)
    flag_col = RED if flag == "CLAIM" else BLUE
    tokens = [(wd, txt_f, INK) for wd in text.split()]
    tokens.append(("—", reg_f, BLUE))
    tokens += [(wd, reg_f, BLUE) for wd in region.split()]
    if flag:
        tokens.append(("·", reg_f, flag_col))
        tokens += [(wd, reg_f, flag_col) for wd in flag.split()]
    lines, cur, cur_w = [], [], 0.0
    num_w = num_f.getlength(f"{num}. ")
    avail = w - num_w
    for wd, fnt, fill in tokens:
        ww = fnt.getlength(wd + " ")
        if cur_w + ww <= avail or not cur:
            cur.append((wd, fnt, fill))
            cur_w += ww
        else:
            lines.append(cur)
            cur = [(wd, fnt, fill)]
            cur_w = ww
    if cur:
        lines.append(cur)
    lines = lines[:2]
    # Draw
    draw.text((x, y), f"{num}. ", font=num_f, fill=AMBER)
    yy = y
    for ln in lines:
        xx = x + num_w
        for wd, fnt, fill in ln:
            draw.text((xx, yy), wd + " ", font=fnt, fill=fill)
            xx += fnt.getlength(wd + " ")
        yy += 14
    return yy


def render():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- Banner ------------------------------------------------------
    d.rectangle([0, 0, W, 58], fill=BANNER_BG)
    cx, cy, r = 40, 29, 17
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=AMBER, width=2)
    d.ellipse([cx - 7, cy - r, cx + 7, cy + r], outline=AMBER, width=1)
    d.line([cx - r, cy, cx + r, cy], fill=AMBER, width=1)
    title_f = fit_font("25 NOVEMBER 2026", BOLD, 44, 560)
    d.text((66, 7), "25 NOVEMBER 2026", font=title_f, fill=INK)
    d.text((W - 12 - font(REG, 14).getlength("ONE DAY OF WORLD NEWS · 33 STORIES"),
            21), "ONE DAY OF WORLD NEWS · 33 STORIES",
           font=font(REG, 14), fill=MUTED)
    d.rectangle([0, 58, W, 61], fill=AMBER)

    # ---- Big-numbers strip -------------------------------------------
    bn_f = fit_font(BIG_NUMBERS, BOLD, 19, W - 24)
    d.text(((W - bn_f.getlength(BIG_NUMBERS)) / 2, 65), BIG_NUMBERS,
           font=bn_f, fill=AMBER)

    # ---- Heroes (3) ----------------------------------------------------
    hx = [12, 352, 692]
    hy0, hy1, hw = 90, 240, 320
    for i, (kick, label, sub, chp, kind, desc) in enumerate(HEROES):
        x0 = hx[i]
        d.rectangle([x0, hy0, x0 + hw, hy1], fill=PANEL, outline=BORDER)
        illustration(d, kind, x0 + 1, hy0 + 1, hw - 2, 50)
        kf = fit_font(kick, BOLD, 10, hw - 100)
        d.text((x0 + 10, hy0 + 54), kick, font=kf, fill=BLUE)
        chip(d, x0 + hw - 78, hy0 + 52, chp, size=9)
        lab_f = fit_font(label, BOLD, 19, hw - 20)
        d.text((x0 + 10, hy0 + 68), label, font=lab_f, fill=INK)
        sub_lines = wrap_text(sub, font(REG, 12), hw - 20)
        yy = hy0 + 90
        for ln in sub_lines[:1]:
            d.text((x0 + 10, yy), ln, font=font(REG, 12), fill=BODY)
            yy += 14
        desc_lines = wrap_text(desc, font(REG, 11), hw - 20)
        yy = hy0 + 106
        for ln in desc_lines[:2]:
            d.text((x0 + 10, yy), ln, font=font(REG, 11), fill=BODY)
            yy += 13

    # ---- Grid 2 rows x 5 ----------------------------------------------
    gx = [12, 213, 414, 615, 816]
    gy = [246, 420]
    pw, ph = 193, 168
    for i, (kick, label, sub, chp, kind, desc) in enumerate(PANELS):
        x0 = gx[i % 5]
        y0 = gy[i // 5]
        d.rectangle([x0, y0, x0 + pw, y0 + ph], fill=PANEL, outline=BORDER)
        illustration(d, kind, x0 + 1, y0 + 1, pw - 2, 34)
        # chip sits on the kicker row (right); label gets the full row below
        chip(d, x0 + pw - 66, y0 + 36, chp, size=8)
        kf = fit_font(kick, BOLD, 8, pw - 20 - 70)
        d.text((x0 + 8, y0 + 38), kick, font=kf, fill=BLUE)
        lab_f = fit_font(label, BOLD, 14, pw - 16)
        d.text((x0 + 8, y0 + 52), label, font=lab_f, fill=INK)
        sub_lines = wrap_text(sub, font(REG, 11), pw - 16)
        yy = y0 + 70
        for ln in sub_lines[:2]:
            d.text((x0 + 8, yy), ln, font=font(REG, 11), fill=BODY)
            yy += 13
        desc_lines = wrap_text(desc, font(REG, 10), pw - 16)
        yy = y0 + 98
        for ln in desc_lines[:5]:
            d.text((x0 + 8, yy), ln, font=font(REG, 10), fill=BODY)
            yy += 12

    # ---- ALSO ON strip -------------------------------------------------
    ay = 594
    d.text((12, ay), "ALSO ON WEDNESDAY 25 NOVEMBER",
           font=font(BOLD, 20), fill=AMBER)
    right = "20 MORE STORIES · 6 REGIONS · 11 FIELDS"
    d.text((W - 12 - font(REG, 13).getlength(right), ay + 4), right,
           font=font(REG, 13), fill=MUTED)
    d.rectangle([12, ay + 26, W - 12, ay + 28], fill=BORDER)
    col_x = [12, 264, 516, 768]
    col_w = 244
    row_y = ay + 32
    row_h = 28
    for i, (text, region, flag) in enumerate(ALSO_ON):
        col = i % 4
        row = i // 4
        draw_also_on_item(d, i + 14, text, region, flag,
                          col_x[col], row_y + row * row_h, col_w)

    # ---- Bottom band: map + DATE CHECK + legend ------------------------
    by = 772
    d.text((12, by), "WHERE IT HAPPENED",
           font=font(BOLD, 14), fill=AMBER)
    draw_map(d, 12, by + 20, 428, 150)
    rx = 456
    # DATE CHECK box
    d.rectangle([rx, by + 20, W - 12, by + 88], fill=PANEL, outline=AMBER)
    d.text((rx + 12, by + 26), "DATE CHECK",
           font=font(BOLD, 15), fill=AMBER)
    dc_lines = wrap_text(
        "All 33 stories verified as 25 Nov 2026 events. Item 18 (Hormuz) "
        "is a CLAIM; item 11 is proposed, not in effect. OUT: Huawei "
        "verdict, Nvidia −7%, Dell earnings, WHO bird flu, Dow 50,000 — "
        "all 24 Nov.",
        font(REG, 12), W - 12 - rx - 24)
    yy = by + 44
    for ln in dc_lines:
        d.text((rx + 12, yy), ln, font=font(REG, 12), fill=BODY)
        yy += 15
    # Legend
    ly = by + 94
    d.text((rx, ly), "CERTAINTY",
           font=font(BOLD, 13), fill=AMBER)
    leg = ("CONFIRMED = fact certain · OFFICIAL = official statement · "
           "REPORTED = confirmed by named outlets · CLAIM = one side's "
           "claim, unverified · PROPOSAL = announced plan, not yet done")
    yy = ly + 16
    for ln in wrap_text(leg, font(REG, 11), W - 12 - rx):
        d.text((rx, yy), ln, font=font(REG, 11), fill=MUTED)
        yy += 13
    # UTC timeline
    ut_y = ly + 62
    d.text((rx, ut_y), "THE DAY IN UTC",
           font=font(BOLD, 13), fill=AMBER)
    yy = ut_y + 16
    for ln in wrap_text(UTC_LINE, font(REG, 11), W - 12 - rx):
        d.text((rx, yy), ln, font=font(REG, 11), fill=BODY)
        yy += 13
    # Region counts
    rc_y = ut_y + 48
    d.text((rx, rc_y), "REGIONS: " + REGION_COUNTS,
           font=font(BOLD, 11), fill=BLUE)
    src = ("Sources: Reuters · AP · Xinhua · AFP · pm.gov.au · BBC · CNN · "
           "BEA · ESA · One Turn · Open Chronicle")
    d.text((12, 1006), src, font=font(REG, 10), fill=MUTED)

    return img


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img = render()
    img.save(out, "PNG", optimize=True)
    print(out)


if __name__ == "__main__":
    main()
