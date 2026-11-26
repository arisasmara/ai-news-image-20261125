#!/usr/bin/env python3
"""Render the make.fun news-image-20261125 entry, v2: one dense broadsheet
of 25 November 2026 world news (3 heroes + 10 grid panels + 37 ALSO ON
one-liners = 50 stories). Deterministic: fixed palette, fixed fonts, no
randomness, no timestamps.
v2: denser 50-story layout following the rank-1 format (3 heroes with a
WHY IT MATTERS line, 10 panels, 37 supporting one-liners, world map,
big-numbers strip, UTC timeline, region counts, DATE CHECK, 5-label
certainty legend, sources). Wall Street close CORRECTED (Dow +0.33% to
50,182.95, S&P -0.25%, Nasdaq -0.62% -- the v1 S&P -2.2% was not the
close). No EUR 650bn figure (unverified). Houthi panel upgraded with the
confirmed Saudi intercept angle. Readability first: heroes and panels
stay legible at 300px; the supporting strip is the most compact tier.
Run: python3 draw_image.py [out_path]  (default: entry.png next to this file)
"""
import os
import sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
FONT_DIR = "/usr/share/fonts/truetype/dejavu"
BOLD = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")
REG = os.path.join(FONT_DIR, "DejaVuSans.ttf")

# Palette -- dull newspaper paper (as approved for v1)
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
INK = (27, 26, 23)           # #1B1A17 ink text

_cache = {}


def font(path, size):
    if (path, size) not in _cache:
        _cache[(path, size)] = ImageFont.truetype(path, size)
    return _cache[(path, size)]


def fit_font(text, path, max_size, max_w, min_size=8):
    """Largest size <= max_size whose rendered width fits max_w."""
    size = max_size
    while size > min_size:
        f = font(path, size)
        if f.getlength(text) <= max_w:
            return f
        size -= 1
    return font(path, min_size)


def wrap(text, fnt, max_w):
    """Greedy word wrap; returns a list of lines."""
    lines, cur = [], ""
    for w in text.split():
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


def chip(draw, x, y, text, bg=BLUE, fg=WHITE, size=11):
    f = font(BOLD, size)
    tw = f.getlength(text)
    pad = 6
    draw.rounded_rectangle([x, y, x + tw + 2 * pad, y + size + 8],
                           radius=4, fill=bg)
    draw.text((x + pad, y + 4), text, font=f, fill=fg)
    return x + tw + 2 * pad


def skyline(draw, x0, base_y, w, color, heights):
    """Flat building silhouettes."""
    n = len(heights)
    bw = w // n
    for i, hh in enumerate(heights):
        bx = x0 + i * bw
        draw.rectangle([bx + 1, base_y - hh, bx + bw - 1, base_y], fill=color)


# ---------------------------------------------------------------- data
# Heroes: (kicker, label, sub, chip, kind, description, why-it-matters)
HEROES = [
    ("EUROPE · WAR", "PUTIN: RETALIATION INEVITABLE",
     "Ukraine hits Samara refineries — Kyiv claims Baltic ship strike",
     "CONFIRMED", "putin",
     "Putin tells oil executives retaliation is inevitable as Ukrainian "
     "drones hit Samara refineries.",
     "Kyiv's energy war widens; Moscow vows to answer"),
    ("CHINA · SPACE", "PAKISTAN REACHES SPACE",
     "First foreign astronaut aboard China's Tiangong",
     "CONFIRMED", "space",
     "Shenzhou-24 launches at 00:18 UTC and docks at 03:56 UTC with "
     "Pakistan's first astronaut aboard.",
     "China's station takes its first foreign astronaut"),
    ("PACIFIC · DIPLOMACY", "PACIFIC PACT SIGNED",
     "Solomons choose Australia — no foreign bases",
     "CONFIRMED", "pact",
     "Australia and Solomon Islands sign a treaty in Canberra; no foreign "
     "military base may be built.",
     "Canberra locks in the Pacific as Beijing's pact lapses"),
]

# Panels: (kicker, label, sub, chip, kind, description)
# 5 retained v1 panels (AI corrected) + 5 new panels (Cairo, UK energy,
# Russian strikes/ZNPP, Nigeria meth, FCC SpaceX).
PANELS = [
    ("ASIA · MARKETS", "AI SELL-OFF DEEPENS",
     "Dow erases 1,100-pt drop — Nasdaq −0.6%", "CONFIRMED", "markets",
     "Nikkei −2.76%, Kospi −6.2%, SK hynix −11.1% on AI doubts. Dow "
     "recovers +0.33% to 50,182.95."),
    ("GLOBAL · TRADE", "TARIFFS HIT 14 NATIONS",
     "China 20% — Vietnam up to 35% — proposed", "CONFIRMED", "tariffs",
     "The US proposes duties on 14 partners: China 20%, Vietnam 20–35%, "
     "EU 15%. Brazil Embraer 10% too. Hearing 25 January."),
    ("US · ECONOMY", "US GROWTH 4.3%",
     "GDP surges — core inflation 3.3%", "CONFIRMED", "gdp",
     "US Q3 GDP revised up to 4.3%, fastest in three years, above the "
     "3.5% consensus. Core PCE 3.3% y/y, largest since Nov 2023."),
    ("S. ASIA · LABOUR", "GARMENT PAY +36%",
     "Minimum wage Tk17,000 after weeks of protests", "CONFIRMED", "wage",
     "Bangladesh approves a 36% garment wage rise to Tk17,000 from 1 Dec. "
     "Workers wanted a doubling; protests cost $428m."),
    ("SPACE · SCIENCE", "ASTEROID'S NEW CRATER",
     "Hera sees DART's stadium-sized scar", "CONFIRMED", "asteroid",
     "ESA unveils Hera's first images of Dimorphos: the 2022 DART impact "
     "left a crater spanning its width."),
    ("EGYPT · DISASTER", "CAIRO: 30+ DEAD IN FIRE",
     "Tanker explodes on ring road — 15 hurt", "CONFIRMED", "cairo",
     "A fuel tanker overturns and explodes on a Cairo ring road, killing "
     "at least 30 and injuring 15."),
    ("EUROPE · ENERGY", "UK ENERGY CAP +26%",
     "Typical bill £1,723 → £2,166 from 1 Jan", "CONFIRMED", "energy",
     "Ofgem raises the UK energy price cap 25.7% from 1 January. The "
     "typical annual bill rises £443 to £2,166."),
    ("EUROPE · WAR", "RUSSIAN STRIKES: 5 KILLED",
     "Zaporizhzhia nuclear plant on diesel again", "CONFIRMED", "nuclear",
     "Russian strikes kill 5 and cut power in five regions. The "
     "Zaporizhzhia nuclear plant loses external power and runs on diesel."),
    ("AFRICA · CRIME", "NIGERIA SEIZES $227M METH",
     "5 Mexicans held in industrial lab raid", "CONFIRMED", "seizure",
     "Nigeria seizes 1,512 kg of meth worth $227m from an industrial lab "
     "and arrests five Mexican specialists."),
    ("US · TECH", "FCC CLEARS 1M SATELLITES",
     "SpaceX wins orbit data-centre approval", "CONFIRMED", "satellites",
     "The FCC approves SpaceX's Starmind constellation of up to one "
     "million satellites for AI data centres in orbit."),
]

# ALSO ON (37 items, numbered 14-50): (text, region, flag)
# flag "" | "PROPOSAL" | "CLAIM"
ALSO_ON = [
    # v1 supporting (20)
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
    ("North Korea expels Swiss envoy, gives 48 hours to leave", "ASIA", ""),
    ("Venezuela discloses ~$237.5bn public debt", "AMERICAS", ""),
    ("Argentina enters technical recession", "AMERICAS", ""),
    ("Australia inflation rises to 4.9%", "OCEANIA", ""),
    ("Chile teachers join nationwide strike", "AMERICAS", ""),
    ('Trump pardons turkeys "Freedom and Feathers"', "AMERICAS", ""),
    ("Ronaldo scores 987th career goal for Al Nassr", "ASIA", ""),
    # demoted v1 panels (5) -- Gaza, Cartagena, Houthi (upgraded with
    # the confirmed Saudi intercept), Bogor, Shanghai chief
    ("Israeli strike kills Hamas security chief Abuelouf, family dead",
     "MIDDLE EAST", ""),
    ("Cartagena: all hostages freed after 17-hour siege", "AMERICAS", ""),
    ("Houthis claim Ras Tanura hit; Saudis down 4 drones, no casualties",
     "MIDDLE EAST", "CLAIM"),
    ("Bogor: 9 dead, 17 still trapped in flooded mine", "ASIA", ""),
    ("China probes Shanghai party chief Chen Jining", "ASIA", ""),
    # new additions (11)
    ("Ukraine claims 5 Russian jets hit at Savasleyka base",
     "EUROPE", "CLAIM"),
    ("Karachi building collapse kills 3, injures 14", "ASIA", ""),
    ("Mississippi: 6 bodies recovered from plane crash", "AMERICAS", ""),
    ("Paraná storms kill 6, affect ~10,000 people", "AMERICAS", ""),
    ("Gaza winter rains threaten 1,000 shelter sites", "MIDDLE EAST", ""),
    ("Court kills 'Farmgate' threat to Ramaphosa", "AFRICA", ""),
    ("Judges urge dropping Netanyahu graft charges", "MIDDLE EAST", ""),
    ("Amnesty urges ICC probe into Gaza births", "MIDDLE EAST", ""),
    ("34 countries tell Russia to stop riot gas in Ukraine", "EUROPE", ""),
    ("Knesset advances Oct 7 inquiry bill, 65–50", "MIDDLE EAST", ""),
    ("Malaysia sues Google for $146m over YouTube", "ASIA", ""),
    # reserve R7 (1) -- Sydney ex-cop guilty; fills the 50th slot
    ("Sydney: ex-cop guilty of Baird & Davies murders", "OCEANIA", ""),
]

BIG_NUMBERS = ("30+ DEAD  ·  +26% ENERGY CAP  ·  $227M METH  ·  "
               "1M SATELLITES  ·  36% WAGE  ·  4.3% GDP")

UTC_LINE = ("00:18 Shenzhou launches  ·  02:12 Samara hit  ·  03:56 Tiangong "
            "docks  ·  06:00 Cartagena freed  ·  13:30 US GDP 4.3%  ·  "
            "Canberra treaty signed")

REGION_COUNTS = ("EUROPE 13  ·  AMERICAS 10  ·  ASIA 10  ·  MIDDLE EAST 10  ·  "
                 "AFRICA 4  ·  OCEANIA 3")

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
# Cartagena, Dhaka, Ras Tanura, Bogor, Shanghai, Washington DC, Cairo,
# London, Kyiv, Lagos, Florida (SpaceX)
MARKERS = [(51.5, 53.2), (98.5, 40.9), (149.1, -35.3), (139.7, 35.7),
           (34.5, 31.5), (-75.5, 10.4), (90.4, 23.8), (50.1, 26.6),
           (106.8, -6.6), (121.5, 31.2), (-77.0, 38.9), (31.2, 30.0),
           (-0.1, 51.5), (30.5, 50.4), (3.4, 6.5), (-80.6, 28.4)]


def illustration(draw, kind, x0, y0, w, h):
    """Flat illustration band inside a hero/panel (x0,y0,w,h)."""
    if kind == "putin":
        vgrad(draw, (x0, y0, x0 + w, y0 + h), (60, 72, 92), (40, 52, 72))
        skyline(draw, x0 + 8, y0 + h - 4, w - 16, (28, 38, 52),
                [16, 22, 14, 24, 18, 20, 15])
        # flame
        draw.polygon([(x0 + 176, y0 + h - 4), (x0 + 196, y0 + h - 24),
                      (x0 + 216, y0 + h - 4)], fill=(220, 100, 40))
        draw.ellipse([x0 + 182, y0 + h - 28, x0 + 210, y0 + h - 10],
                     fill=(242, 168, 29))
        for cx, cy, r in [(x0 + 196, y0 + 8, 8), (x0 + 212, y0 + 5, 9)]:
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(130, 128, 122))
    elif kind == "space":
        vgrad(draw, (x0, y0, x0 + w, y0 + h), (28, 42, 72), (14, 24, 48))
        for sx, sy in [(x0 + 30, y0 + 10), (x0 + 90, y0 + 18),
                       (x0 + 150, y0 + 8), (x0 + 240, y0 + 14),
                       (x0 + 280, y0 + 30), (x0 + 60, y0 + 34)]:
            draw.ellipse([sx - 1, sy - 1, sx + 1, sy + 1], fill=WHITE)
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
        for fx, stripes in ((x0 + 62, [(38, 74, 140), (38, 74, 140)]),
                            (x0 + w - 126, [(38, 74, 140), (60, 140, 70)])):
            draw.line([fx, y0 + 4, fx, y0 + h - 2], fill=(70, 66, 60), width=2)
            fw, fh = 62, 26
            sy = y0 + 5
            for j, col in enumerate(stripes):
                sh = fh // len(stripes)
                draw.rectangle([fx + 2, sy + j * sh,
                                fx + 2 + fw, sy + (j + 1) * sh], fill=col)
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
    elif kind == "tariffs":
        vgrad(draw, (x0, y0, x0 + w, y0 + h), (210, 222, 205), (185, 205, 180))
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
    elif kind == "wage":
        vgrad(draw, (x0, y0, x0 + w, y0 + h), (210, 222, 205), (185, 205, 180))
        f = fit_font("Tk17,000", BOLD, 22, w - 20)
        draw.text((x0 + 10, y0 + 6), "Tk17,000", font=f, fill=AMBER)
        draw.text((x0 + w - 60, y0 + h - 16), "+36%",
                  font=font(BOLD, 13), fill=GREEN)
    elif kind == "asteroid":
        vgrad(draw, (x0, y0, x0 + w, y0 + h), (28, 42, 72), (14, 24, 48))
        for sx, sy in [(x0 + 20, y0 + 8), (x0 + 60, y0 + 16),
                       (x0 + 150, y0 + 10)]:
            draw.ellipse([sx - 1, sy - 1, sx + 1, sy + 1], fill=WHITE)
        ax, ay, ar = x0 + w // 2, y0 + h // 2 + 4, 15
        draw.ellipse([ax - ar, ay - ar, ax + ar, ay + ar],
                     fill=(150, 140, 125))
        draw.ellipse([ax - 6, ay - 4, ax + 4, ay + 6], fill=(110, 100, 88))
        draw.ellipse([ax + 6, ay - 8, ax + 12, ay - 2], fill=(120, 110, 96))
        for bx, by, br in [(x0 + 30, y0 + h - 10, 4), (x0 + w - 34, y0 + 8, 3),
                           (x0 + w - 24, y0 + h - 8, 4)]:
            draw.ellipse([bx - br, by - br, bx + br, by + br],
                         fill=(150, 140, 125))
    elif kind == "cairo":
        # night sky, overturned tanker, big flame column
        vgrad(draw, (x0, y0, x0 + w, y0 + h), (52, 48, 60), (28, 26, 36))
        draw.rectangle([x0 + 8, y0 + h - 8, x0 + w - 8, y0 + h - 4],
                       fill=(90, 85, 78))
        # tanker body on its side
        draw.rectangle([x0 + 30, y0 + h - 16, x0 + 130, y0 + h - 8],
                       fill=(170, 160, 145))
        draw.ellipse([x0 + 44, y0 + h - 14, x0 + 54, y0 + h - 4],
                     fill=(60, 55, 50))
        draw.ellipse([x0 + 100, y0 + h - 14, x0 + 110, y0 + h - 4],
                     fill=(60, 55, 50))
        # flame column
        cx = x0 + w // 2 + 20
        draw.polygon([(cx - 22, y0 + h - 6), (cx, y0 + 4),
                      (cx + 22, y0 + h - 6)], fill=(220, 100, 40))
        draw.polygon([(cx - 12, y0 + h - 6), (cx, y0 + 12),
                      (cx + 12, y0 + h - 6)], fill=(242, 168, 29))
        # smoke
        for sx, sy, r in [(cx - 8, y0 + 8, 7), (cx + 10, y0 + 5, 8)]:
            draw.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(110, 106, 100))
    elif kind == "energy":
        # meter dial with a rising needle + £ figure
        vgrad(draw, (x0, y0, x0 + w, y0 + h), (215, 222, 210), (190, 205, 185))
        cx, cy, r = x0 + w // 2 - 20, y0 + h // 2 + 6, 13
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=AMBER, width=3)
        draw.line([cx, cy, cx + 9, cy - 9], fill=RED, width=3)
        draw.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=AMBER)
        f = fit_font("£2,166", BOLD, 20, w - 20)
        draw.text((x0 + w - 62, y0 + 4), "£2,166", font=f, fill=AMBER)
        draw.text((x0 + 10, y0 + h - 15), "+26%",
                  font=font(BOLD, 12), fill=RED)
    elif kind == "nuclear":
        # cooling towers + warning triangle
        vgrad(draw, (x0, y0, x0 + w, y0 + h), (205, 215, 222), (180, 195, 208))
        for tx in (x0 + 30, x0 + 90):
            draw.polygon([(tx, y0 + h - 4), (tx + 8, y0 + 8),
                          (tx + 28, y0 + 8), (tx + 36, y0 + h - 4)],
                         fill=(150, 155, 160))
            draw.rectangle([tx + 8, y0 + 4, tx + 28, y0 + 10],
                           fill=(120, 125, 130))
        # steam wisps
        for sx, sy, r in [(x0 + 48, y0 + 4, 5), (x0 + 108, y0 + 6, 6)]:
            draw.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(225, 228, 232))
        # warning triangle (power loss)
        wx = x0 + w - 42
        draw.polygon([(wx, y0 + h - 4), (wx + 16, y0 + h - 26),
                      (wx + 32, y0 + h - 4)], fill=(238, 198, 60),
                     outline=AMBER)
        draw.text((wx + 13, y0 + h - 18), "!", font=font(BOLD, 12),
                  fill=INK)
    elif kind == "seizure":
        # stacked seized packages + value tag
        vgrad(draw, (x0, y0, x0 + w, y0 + h), (222, 214, 200), (200, 188, 172))
        for px, py in [(x0 + 24, y0 + h - 20), (x0 + 64, y0 + h - 20),
                       (x0 + 104, y0 + h - 20), (x0 + 44, y0 + h - 32),
                       (x0 + 84, y0 + h - 32)]:
            draw.rectangle([px, py, px + 34, py + 12], fill=(150, 135, 110),
                           outline=(110, 95, 75))
        draw.rectangle([x0 + w - 78, y0 + 4, x0 + w - 6, y0 + 20],
                       fill=RED)
        draw.text((x0 + w - 74, y0 + 7), "$227m", font=font(BOLD, 11),
                  fill=WHITE)
    elif kind == "satellites":
        # orbit arc with satellite dots + one big satellite
        vgrad(draw, (x0, y0, x0 + w, y0 + h), (28, 42, 72), (14, 24, 48))
        for sx, sy in [(x0 + 16, y0 + 6), (x0 + 60, y0 + 14),
                       (x0 + 170, y0 + 8)]:
            draw.ellipse([sx - 1, sy - 1, sx + 1, sy + 1], fill=WHITE)
        # orbit ellipse
        draw.arc([x0 + 10, y0 - 6, x0 + w - 10, y0 + h + 14],
                 start=200, end=340, fill=(150, 165, 190), width=2)
        # satellites on the arc
        for sx, sy in [(x0 + 40, y0 + 12), (x0 + 96, y0 + 4),
                       (x0 + 150, y0 + 12)]:
            draw.rectangle([sx - 5, sy - 2, sx + 5, sy + 2], fill=WHITE)
            draw.line([sx - 8, sy, sx + 8, sy], fill=WHITE, width=1)


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
    num_f = font(BOLD, 11)
    txt_f = font(REG, 10)
    reg_f = font(BOLD, 9)
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
    draw.text((x, y), f"{num}. ", font=num_f, fill=AMBER)
    yy = y
    for ln in lines:
        xx = x + num_w
        for wd, fnt, fill in ln:
            draw.text((xx, yy), wd + " ", font=fnt, fill=fill)
            xx += fnt.getlength(wd + " ")
        yy += 12
    return yy


def render():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- Banner ------------------------------------------------------
    d.rectangle([0, 0, W, 56], fill=BANNER_BG)
    cx, cy, r = 40, 28, 17
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=AMBER, width=2)
    d.ellipse([cx - 7, cy - r, cx + 7, cy + r], outline=AMBER, width=1)
    d.line([cx - r, cy, cx + r, cy], fill=AMBER, width=1)
    title_f = fit_font("25 NOVEMBER 2026", BOLD, 44, 560)
    d.text((66, 6), "25 NOVEMBER 2026", font=title_f, fill=INK)
    d.text((W - 12 - font(REG, 14).getlength("ONE DAY OF WORLD NEWS · 50 STORIES"),
            20), "ONE DAY OF WORLD NEWS · 50 STORIES",
           font=font(REG, 14), fill=MUTED)
    d.rectangle([0, 56, W, 59], fill=AMBER)

    # ---- Big-numbers strip -------------------------------------------
    bn_f = fit_font(BIG_NUMBERS, BOLD, 19, W - 24)
    d.text(((W - bn_f.getlength(BIG_NUMBERS)) / 2, 63), BIG_NUMBERS,
           font=bn_f, fill=AMBER)

    # ---- Heroes (3) with WHY IT MATTERS -------------------------------
    hx = [12, 352, 692]
    hy0, hy1, hw = 88, 236, 320
    for i, (kick, label, sub, chp, kind, desc, why) in enumerate(HEROES):
        x0 = hx[i]
        d.rectangle([x0, hy0, x0 + hw, hy1], fill=PANEL, outline=BORDER)
        illustration(d, kind, x0 + 1, hy0 + 1, hw - 2, 38)
        kf = fit_font(kick, BOLD, 10, hw - 100)
        d.text((x0 + 10, hy0 + 43), kick, font=kf, fill=BLUE)
        chip(d, x0 + hw - 78, hy0 + 41, chp, size=9)
        lab_f = fit_font(label, BOLD, 19, hw - 20)
        d.text((x0 + 10, hy0 + 57), label, font=lab_f, fill=INK)
        sub_lines = wrap(sub, font(REG, 12), hw - 20)
        yy = hy0 + 79
        for ln in sub_lines[:1]:
            d.text((x0 + 10, yy), ln, font=font(REG, 12), fill=BODY)
            yy += 14
        desc_lines = wrap(desc, font(REG, 11), hw - 20)
        yy = hy0 + 93
        for ln in desc_lines[:2]:
            d.text((x0 + 10, yy), ln, font=font(REG, 11), fill=BODY)
            yy += 13
        # WHY IT MATTERS -- one short line, amber "WHY: " prefix
        why_f = font(REG, 10)
        why_b = font(BOLD, 10)
        why_text = "WHY: " + why
        why_lines = wrap(why_text, why_f, hw - 20)
        yy = hy0 + 121
        for ln in why_lines[:2]:
            # bold the "WHY: " prefix, regular for the rest
            d.text((x0 + 10, yy), "WHY: ", font=why_b, fill=AMBER)
            d.text((x0 + 10 + why_b.getlength("WHY: "), yy),
                   ln[5:], font=why_f, fill=MUTED)
            yy += 12

    # ---- Grid 2 rows x 5 ----------------------------------------------
    gx = [12, 213, 414, 615, 816]
    gy = [242, 388]
    pw, ph = 193, 140
    for i, (kick, label, sub, chp, kind, desc) in enumerate(PANELS):
        x0 = gx[i % 5]
        y0 = gy[i // 5]
        d.rectangle([x0, y0, x0 + pw, y0 + ph], fill=PANEL, outline=BORDER)
        illustration(d, kind, x0 + 1, y0 + 1, pw - 2, 27)
        chip(d, x0 + pw - 66, y0 + 29, chp, size=8)
        kf = fit_font(kick, BOLD, 8, pw - 20 - 70)
        d.text((x0 + 8, y0 + 31), kick, font=kf, fill=BLUE)
        lab_f = fit_font(label, BOLD, 14, pw - 16)
        d.text((x0 + 8, y0 + 45), label, font=lab_f, fill=INK)
        sub_lines = wrap(sub, font(REG, 11), pw - 16)
        yy = y0 + 63
        for ln in sub_lines[:2]:
            d.text((x0 + 8, yy), ln, font=font(REG, 11), fill=BODY)
            yy += 13
        desc_lines = wrap(desc, font(REG, 10), pw - 16)
        yy = y0 + 91
        for ln in desc_lines[:4]:
            d.text((x0 + 8, yy), ln, font=font(REG, 10), fill=BODY)
            yy += 12

    # ---- ALSO ON strip (37 items, 4 cols x 10 rows) --------------------
    ay = 534
    d.text((12, ay), "ALSO ON WEDNESDAY 25 NOVEMBER",
           font=font(BOLD, 20), fill=AMBER)
    right = "37 MORE STORIES · 6 REGIONS · 20 FIELDS"
    d.text((W - 12 - font(REG, 13).getlength(right), ay + 4), right,
           font=font(REG, 13), fill=MUTED)
    d.rectangle([12, ay + 26, W - 12, ay + 28], fill=BORDER)
    col_x = [12, 264, 516, 768]
    col_w = 244
    row_y = ay + 32
    row_h = 24
    for i, (text, region, flag) in enumerate(ALSO_ON):
        col = i % 4
        row = i // 4
        draw_also_on_item(d, i + 14, text, region, flag,
                          col_x[col], row_y + row * row_h, col_w)

    # ---- Bottom band: map + DATE CHECK + legend ------------------------
    by = 812
    d.text((12, by), "WHERE IT HAPPENED",
           font=font(BOLD, 14), fill=AMBER)
    draw_map(d, 12, by + 20, 428, 150)
    rx = 456
    # DATE CHECK box
    d.rectangle([rx, by + 20, W - 12, by + 84], fill=PANEL, outline=AMBER)
    d.text((rx + 12, by + 26), "DATE CHECK",
           font=font(BOLD, 15), fill=AMBER)
    dc_lines = wrap(
        "All 50 stories verified as 25 Nov 2026 events. Item 18 (Hormuz) "
        "is a CLAIM; item 11 proposed, not in effect. OUT: Huawei, Nvidia "
        "−7%, Dell, WHO bird flu, Dow 50,000, CIA breach, Mugabe warrant, "
        "Merkury, UK sabotage alert, Zelensky €115bn — all 24 Nov.",
        font(REG, 11), W - 12 - rx - 24)
    yy = by + 44
    for ln in dc_lines:
        d.text((rx + 12, yy), ln, font=font(REG, 11), fill=BODY)
        yy += 13
    # Legend
    ly = by + 90
    d.text((rx, ly), "CERTAINTY",
           font=font(BOLD, 13), fill=AMBER)
    leg = ("CONFIRMED = fact certain · OFFICIAL = official statement · "
           "REPORTED = confirmed by named outlets · CLAIM = one side's "
           "claim, unverified · PROPOSAL = announced plan, not yet done")
    yy = ly + 16
    for ln in wrap(leg, font(REG, 11), W - 12 - rx):
        d.text((rx, yy), ln, font=font(REG, 11), fill=MUTED)
        yy += 12
    # UTC timeline
    ut_y = ly + 46
    d.text((rx, ut_y), "THE DAY IN UTC",
           font=font(BOLD, 13), fill=AMBER)
    yy = ut_y + 16
    for ln in wrap(UTC_LINE, font(REG, 11), W - 12 - rx):
        d.text((rx, yy), ln, font=font(REG, 11), fill=BODY)
        yy += 12
    # Region counts
    rc_y = ut_y + 44
    rc_f = fit_font("REGIONS: " + REGION_COUNTS, BOLD, 11, W - 12 - rx)
    d.text((rx, rc_y), "REGIONS: " + REGION_COUNTS, font=rc_f, fill=BLUE)
    src = ("Sources: Reuters · AP · AFP · BBC · CNN · Xinhua · Ofgem · BEA · "
           "ESA · FCC · OPCW · Amnesty · Dawn · ABC · pm.gov.au · One Turn · "
           "Open Chronicle")
    d.text((12, 1012), src, font=font(REG, 10), fill=MUTED)

    return img


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img = render()
    img.save(out, "PNG", optimize=True)
    print(out)


if __name__ == "__main__":
    main()
