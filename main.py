#!/usr/bin/env python3
"""The World in One Day - Friday 20 November 2026.

Builds entry.png (1024x1024, RGB) from real news dated Friday 20 November
2026 only. Pure Python stdlib + Pillow. Fully deterministic: no clocks, no
network, no unseeded randomness - running it twice yields a byte-identical
PNG.

Design (original): a one-page broadsheet built around a single continuous
triptych panorama (Kyiv night / Cyclone Akvan / falling markets), a UTC
timeline of the day, three lead columns, a twelve-front grid with small
original pictograms, a numbered world map, and a 52-item "also on Friday"
index. 67 stories across 12 regions.
"""

import math
import os
import random
import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MARGIN = 24
CONTENT_W = W - 2 * MARGIN

# ---------------------------------------------------------------- palette
PAPER = (247, 243, 232)
PAPER_DARK = (238, 232, 216)
INK = (20, 20, 20)
INK_SOFT = (70, 66, 58)
GREY = (120, 116, 106)
RED = (176, 30, 36)
RED_DARK = (140, 22, 28)
NAVY = (27, 42, 74)
NAVY_DARK = (14, 24, 48)
GOLD = (184, 138, 44)
TEAL = (31, 110, 110)
GREEN = (46, 110, 62)
RULE = (180, 172, 154)
CARD_BG = (255, 252, 244)
SEA = (46, 110, 142)

# ---------------------------------------------------------------- fonts
FONT_DIR_SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif"
FONT_DIR_SANS = "/usr/share/fonts/truetype/liberation/LiberationSans"
FONT_DIR_DEJA = "/usr/share/fonts/truetype/dejavu/DejaVuSans"


def _load(path, size):
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def serif(size, bold=False):
    name = "LiberationSerif-Bold.ttf" if bold else "LiberationSerif-Regular.ttf"
    return _load(os.path.join(FONT_DIR_SERIF, name), size)


def sans(size, bold=False):
    name = "LiberationSans-Bold.ttf" if bold else "LiberationSans-Regular.ttf"
    return _load(os.path.join(FONT_DIR_SANS, name), size)


def deja(size, bold=False):
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    return _load(os.path.join(FONT_DIR_DEJA, name), size)


# ---------------------------------------------------------------- text utils
def tw(draw, text, font):
    return draw.textlength(text, font=font)


def wrap(draw, text, font, width):
    """Greedy word wrap; returns a list of lines that fit `width`."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = word if not cur else cur + " " + word
        if draw.textlength(trial, font=font) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_lines(draw, lines, x, y, font, fill, leading):
    for i, line in enumerate(lines):
        draw.text((x, y + i * leading), line, font=font, fill=fill)
    return y + len(lines) * leading


def fit_font(draw, text, width, start, minimum, bold=False, mono=False):
    """Largest sans size in [minimum, start] that fits `text` in `width`."""
    size = start
    while size > minimum:
        if draw.textlength(text, font=sans(size, bold)) <= width:
            return size
        size -= 1
    return minimum


# ---------------------------------------------------------------- data
# Every story below happened, or was first reported, on Friday 20 Nov 2026.
LEADS = [
    {
        "num": 1, "kicker": "KYIV, UKRAINE  ·  WAR", "region": "E. Europe",
        "head": "Russian missiles hit three Kyiv bridges",
        "deck": ("Overnight, 111 missiles and 404 drones hit Ukraine. Three "
                 "Dnipro bridges were struck, at least eight were killed, "
                 "and power and water were cut in the capital."),
        "source": "Reuters, Kyiv Independent, ISW",
    },
    {
        "num": 2, "kicker": "ODISHA, INDIA  ·  CYCLONE", "region": "S. Asia",
        "head": "Cyclone Akvan comes ashore in eastern India",
        "deck": ("The storm crossed the coast near Gopalpur from 02:00 UTC "
                 "with 70-80 km/h winds. More than 370,000 people were "
                 "moved to shelters; no deaths were reported."),
        "source": "IMD, PTI, The Hindu BusinessLine",
    },
    {
        "num": 3, "kicker": "TAIPEI  ·  SEOUL  ·  TOKYO  ·  MARKETS",
        "region": "E. Asia",
        "head": "AI sell-off sinks Asia's stock markets",
        "deck": ("Taiwan's index fell 6.2% to end its worst week since 1991. "
                 "Seoul lost 5.2% and Tokyo 5.1% as chipmakers led the "
                 "slide; Wall Street followed."),
        "source": "Al Jazeera, Anadolu",
    },
]

# kind -> pictogram drawn in the card's art strip
CARDS = [
    {"num": 4, "kicker": "BRUSSELS  ·  DIPLOMACY", "region": "W. Europe",
     "kind": "flags", "bg": (27, 42, 74),
     "head": "UK and EU seal a \u201creset\u201d deal",
     "deck": "Food trade, youth visas, carbon link.",
     "source": "Reuters"},
    {"num": 5, "kicker": "ANTALYA  ·  CLIMATE", "region": "Global",
     "kind": "globe", "bg": (31, 110, 110),
     "head": "COP31 reaches its last day with no deal",
     "deck": "Draft text leaves out fossil fuels.",
     "source": "UN News, Carbon Brief"},
    {"num": 6, "kicker": "EASTERN POLAND  ·  SECURITY", "region": "E. Europe",
     "kind": "missile", "bg": (70, 66, 58),
     "head": "Russian cruise missile lands in Poland",
     "deck": "It fell in a field; two airports paused.",
     "source": "Reuters"},
    {"num": 7, "kicker": "CENTRAL IRAQ  ·  SECURITY", "region": "Mid. East",
     "kind": "tank", "bg": (110, 96, 58),
     "head": "Iraqi army enters a militia stronghold",
     "deck": "Troops deploy to Jurf al-Sakhar.",
     "source": "Reuters"},
    {"num": 8, "kicker": "ITALY  ·  LABOUR", "region": "W. Europe",
     "kind": "crowd", "bg": (140, 22, 28),
     "head": "General strike over Italy's budget",
     "deck": "Workers and students march.",
     "source": "Reuters"},
    {"num": 9, "kicker": "TOKYO  ·  ECONOMY", "region": "E. Asia",
     "kind": "chartup", "bg": (27, 42, 74),
     "head": "Japan's inflation picks up to 2.3%",
     "deck": "A December rate rise stays in view.",
     "source": "Reuters"},
    {"num": 10, "kicker": "SEOUL  ·  POLITICS", "region": "E. Asia",
     "kind": "gavel", "bg": (96, 62, 32),
     "head": "Korea's ruling party to impeach top judge",
     "deck": "It follows an overturned conviction.",
     "source": "Korea Herald"},
    {"num": 11, "kicker": "TURKANA, KENYA  ·  ENERGY", "region": "Africa",
     "kind": "derrick", "bg": (184, 138, 44),
     "head": "Kenya starts drilling its first oil well",
     "deck": "First crude is due on 1 December.",
     "source": "allAfrica"},
    {"num": 12, "kicker": "SAN SALVADOR  ·  POLITICS", "region": "C. America",
     "kind": "ballot", "bg": (31, 110, 110),
     "head": "Bukele files to run for a third term",
     "deck": "The vote is on 28 February 2027.",
     "source": "AP"},
    {"num": 13, "kicker": "WELLINGTON  ·  CRICKET", "region": "Oceania",
     "kind": "cricket", "bg": (46, 110, 62),
     "head": "Phillips hits 118 against India",
     "deck": "Nicholls 175* in a stand of 216.",
     "source": "ICC"},
    {"num": 14, "kicker": "NEW YORK  ·  TECH", "region": "N. America",
     "kind": "chip", "bg": (20, 20, 20),
     "head": "Nvidia sinks 14% on SEC probe report",
     "deck": "S&P 500 enters a correction, -3.7%.",
     "source": "Reuters"},
    {"num": 15, "kicker": "HORMUZ  ·  SHIPPING", "region": "Mid. East",
     "kind": "tanker", "bg": (46, 110, 142),
     "head": "Tanker set ablaze off Oman near Hormuz",
     "deck": "No casualties; Iran's Guards blame a mine.",
     "source": "UKMTO"},
]

# (number, one-line text, source, region) - kept short so each fits one line
ALSO = [
    (16, "Lviv: rail station strike kills 2", "BBC", "E. Europe"),
    (17, "Moscow: Estonia border closure", "Reuters", "E. Europe"),
    (18, "Berlin: pupils strike over conscription", "AJ", "W. Europe"),
    (19, "London: UK runs cyber attacks abroad", "Sky", "W. Europe"),
    (20, "Beijing holds loan rates, 18th month", "Xinhua", "E. Asia"),
    (21, "Tokyo: SoftBank shares fall 14% in a day", "AJ", "E. Asia"),
    (22, "Seoul: Kospi ends week 7.9% lower", "Anadolu", "E. Asia"),
    (23, "Ganjam: 209 mm of rain as Akvan crosses", "PTI", "S. Asia"),
    (24, "Lebanon: Israeli strikes hit south", "Anadolu", "Mid. East"),
    (25, "Yemen: gunmen fire on cargo ship", "UKMTO", "Mid. East"),
    (26, "Abuja: court bars new evidence vs Tinubu", "CTV", "Africa"),
    (27, "Kampala: Ebola rally ban enforced", "allAfrica", "Africa"),
    (28, "Malawi: night-long queues at petrol stations", "AJ", "Africa"),
    (29, "Africa: AfDB: 22 states in debt distress", "allAfrica", "Africa"),
    (30, "Las Vegas: Russell fastest in wet GP", "Autosport", "N. America"),
    (31, "New York: Nasdaq futures fall 1.6% pre-bell", "24/7", "N. America"),
    (32, "Washington: Democrats query law firm free work", "AJ", "N. America"),
    (33, "Sydney: shares fall 1.6% in the sell-off", "Reuters", "Oceania"),
    (34, "Antalya: Panama asks COP31 to cap oil", "Anadolu", "C. America"),
    (35, "Antalya: EU official slams climate draft", "RTE", "W. Europe"),
    (36, "Turin: ATP backs pay plan past $350m", "Anadolu", "W. Europe"),
    (37, "New Delhi: Pakistani minister visits", "PTI, Dawn", "S. Asia"),
    (38, "Estonia: Russia road border to shut 1 Dec", "Reuters", "E. Europe"),
    (39, "Gaza: Israeli strikes kill 6 despite truce", "Reuters", "Mid. East"),
    (40, "Yemen: coalition strikes Houthi Hodeidah", "Reuters", "Mid. East"),
    (41, "Sudan: army claims gains in West Kordofan", "Reuters", "Africa"),
    (42, "Japan: core inflation rises to 2.2%", "Reuters", "E. Asia"),
    (43, "Bangladesh: arson attacks; 124 held", "Reuters", "S. Asia"),
    (44, "Myanmar: World Court ruling called unfair", "Reuters", "SE Asia"),
    (45, "Australia: Xi hails China ties turnaround", "Reuters", "Oceania"),
    (46, "Wall St: Anthropic falls 8.6% on day two", "Reuters", "N. America"),
    (47, "US: Florida floods spread north", "Reuters", "N. America"),
    (48, "US: 2nd judge blocks Trump's 250-ft arch", "Reuters", "N. America"),
    (49, "US Fed: Cook calls for rate hikes now", "Reuters", "N. America"),
    (50, "Mexico: Sheinbaum leads Revolution parade", "Reuters", "N. America"),
    (51, "Film: Hunger Games prequel takes $21.25m", "Reuters", "N. America"),
    (52, "Europe: shares end worst week in a year", "Reuters", "W. Europe"),
    (53, "Argentina: country risk jumps to 1,070", "JPM", "S. America"),
    (54, "Kyiv: Podilsko bridge traffic restored", "ICBrief", "E. Europe"),
    (55, "Warsaw: Moscow fired into Polish airspace", "ISW", "E. Europe"),
    (56, "Bhubaneswar: Assembly adjourned till 23 Nov", "PTI", "S. Asia"),
    (57, "Odisha: 47 trains cancelled, 28 rescheduled", "IE", "S. Asia"),
    (58, "Puri: Gundicha Temple shut until 21 Nov", "PTI", "S. Asia"),
    (59, "Antalya: third COP31 draft due Saturday", "CB", "Global"),
    (60, "Antalya: seven nations publish exit plans", "CB", "Global"),
    (61, "Antalya: France, Panama refuse draft", "AInvest", "Global"),
    (62, "Kyiv: air force says 462 targets downed", "Air Force", "E. Europe"),
    (63, "Kharkiv: drones hit a hospital; four hurt", "Reuters", "E. Europe"),
    (64, "Dnipro: five hurt as drones hit flats", "Reuters", "E. Europe"),
    (65, "Antalya: missing-cat protest", "AsiaToday", "Global"),
    (66, "Addis Ababa: next climate summit 2027", "AsiaToday", "Africa"),
    (67, "Antalya: COP31 dubbed worst COP in history", "CB", "Global"),
]

STATS = [
    ("111", "missiles fired at Ukraine overnight"),
    ("404", "drones in the same barrage"),
    ("3", "bridges over the Dnipro damaged"),
    ("370,000", "people moved to shelters before Akvan"),
    ("-6.2%", "Taiwan's share index, Friday's close"),
    ("100,000", "youth visas a year in the UK-EU deal"),
]

TIMELINE = [
    ("00:30", "Kyiv bridges hit"),
    ("02:00", "Akvan makes landfall"),
    ("05:30", "Taiwan ends -6.2%"),
    ("06:00", "Missile lands in Poland"),
    ("09:00", "Kenya drills first oil"),
    ("15:00", "COP31 runs past close"),
    ("19:10", "Report of Nvidia probe"),
    ("21:00", "S&P 500 ends -3.7%"),
]

REGIONS = ["E. Europe", "W. Europe", "E. Asia", "S. Asia", "SE Asia",
           "Mid. East", "Africa", "N. America", "S. America", "C. America",
           "Oceania", "Global"]

# Map dots for the 15 front-page stories: (lon, lat)
MAP_DOTS = [
    (30.5, 50.4), (84.9, 19.3), (121.5, 25.0), (4.35, 50.85),
    (30.7, 36.9), (22.5, 50.6), (44.2, 32.9), (12.5, 41.9),
    (139.7, 35.7), (127.0, 37.5), (36.0, 3.0), (-89.2, 13.7),
    (174.8, -41.3), (-74.0, 40.7), (56.5, 26.5),
]

TOTAL_STORIES = 3 + len(CARDS) + len(ALSO)   # 67

# ---------------------------------------------------------------- art
def _bezier(p0, p1, p2, t):
    x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t ** 2 * p2[0]
    y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t ** 2 * p2[1]
    return x, y


def draw_panorama(draw, x, y, w, h):
    """One continuous scene in three movements, joined by a gold horizon."""
    # sky / sea gradient, left (night) to right (pale market panel)
    for i in range(h):
        t = i / max(1, h - 1)
        r = int(16 + (214 - 16) * t * 0.55)
        g = int(26 + (226 - 26) * t * 0.55)
        b = int(48 + (210 - 48) * t * 0.55)
        draw.line([(x, y + i), (x + w, y + i)], fill=(r, g, b))
    # right third: dark market panel over the gradient
    rx = x + int(w * 0.66)
    draw.rectangle([rx, y, x + w, y + h], fill=(20, 32, 46))
    draw.rectangle([rx, y, x + w, y + h], outline=(120, 116, 106))

    # ---- scene 1: Kyiv at night (left third)
    rng = random.Random(7)
    for _ in range(46):
        sx = x + rng.randint(4, int(w * 0.30))
        sy = y + rng.randint(4, int(h * 0.45))
        draw.ellipse([sx, sy, sx + 1, sy + 1], fill=(240, 236, 210))
    # skyline
    base = y + h - 26
    draw.rectangle([x, base, x + int(w * 0.33), y + h], fill=(10, 16, 32))
    for bx, bw, bh in [(8, 26, 34), (42, 18, 52), (70, 30, 28), (108, 16, 44),
                       (132, 24, 30), (164, 18, 48), (196, 26, 26),
                       (230, 20, 40), (258, 24, 30), (288, 18, 36)]:
        draw.rectangle([x + bx, base - bh, x + bx + bw, base], fill=(16, 24, 46))
        for wy in range(base - bh + 6, base - 4, 10):
            draw.rectangle([x + bx + 4, wy, x + bx + 7, wy + 3],
                           fill=(232, 190, 90))
    # bridge: deck + three arches
    draw.line([(x + 6, base + 8), (x + int(w * 0.33) - 4, base + 8)],
              fill=(200, 196, 180), width=3)
    for cx in (70, 160, 250):
        draw.arc([x + cx - 34, base - 22, x + cx + 34, base + 14],
                 180, 360, fill=(200, 196, 180), width=2)
    # missile trails: dashed quadratic arcs with burst heads
    for (p0, p1, p2) in [((x + 40, y + 18), (x + 120, y + 58), (x + 150, base - 6)),
                         ((x + 210, y + 10), (x + 250, y + 44), (x + 262, base - 12))]:
        for k in range(0, 21):
            if k % 2 == 0:
                px, py = _bezier(p0, p1, p2, k / 20.0)
                draw.ellipse([px - 1, py - 1, px + 1, py + 1],
                             fill=(245, 200, 90))
        bx, by = _bezier(p0, p1, p2, 1.0)
        for ang in range(0, 360, 45):
            ex = bx + 7 * math.cos(math.radians(ang))
            ey = by + 7 * math.sin(math.radians(ang))
            draw.line([(bx, by), (ex, ey)], fill=(245, 160, 60), width=2)
        draw.ellipse([bx - 3, by - 3, bx + 3, by + 3], fill=(255, 220, 120))

    # ---- scene 2: Bay of Bengal cyclone (middle third)
    mx0 = x + int(w * 0.335)
    mx1 = x + int(w * 0.655)
    # coastline: tan landmass upper-left of the middle panel
    coast = [(mx0, y + 8), (mx0 + 60, y + 6), (mx0 + 96, y + 30),
             (mx0 + 108, y + 62), (mx0 + 88, y + 96), (mx0 + 40, y + h - 8),
             (mx0, y + h - 8)]
    draw.polygon(coast, fill=(216, 196, 150))
    draw.line(coast + [coast[0]], fill=(150, 128, 88), width=2)
    # cyclone spiral: concentric dashed rings around the eye
    cx, cy = mx0 + 148, y + 56
    for r in (10, 18, 26, 34):
        draw.arc([cx - r, cy - r, cx + r, cy + r], 20, 300,
                 fill=(255, 255, 255), width=2)
    draw.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=(255, 255, 255))
    draw.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=RED)
    # rain streaks
    for sx, sy in [(mx0 + 30, y + 40), (mx0 + 52, y + 70), (mx0 + 20, y + 82),
                   (mx0 + 200, y + 30), (mx0 + 220, y + 80), (mx0 + 180, y + 82)]:
        draw.line([(sx, sy), (sx - 3, sy + 9)], fill=(230, 240, 245), width=2)
    # Gopalpur marker
    gx, gy = mx0 + 92, y + 58
    draw.ellipse([gx - 5, gy - 5, gx + 5, gy + 5], fill=RED)
    draw.ellipse([gx - 2, gy - 2, gx + 2, gy + 2], fill=(255, 255, 255))

    # ---- scene 3: falling markets (right third)
    # descending bars
    bw = 18
    heights = [62, 56, 48, 52, 40, 34, 26, 30, 18]
    for i, hh in enumerate(heights):
        bx0 = rx + 14 + i * (bw + 6)
        draw.rectangle([bx0, y + h - 18 - hh, bx0 + bw, y + h - 18],
                       fill=(150, 40, 44) if i > 4 else (90, 90, 96))
    # red falling line with arrowhead
    pts = [(rx + 14, y + 26), (rx + 70, y + 40), (rx + 120, y + 34),
           (rx + 175, y + 58), (rx + 225, y + 66), (rx + 285, y + 92)]
    draw.line(pts, fill=(235, 70, 70), width=3, joint="curve")
    draw.polygon([(rx + 285, y + 92), (rx + 268, y + 86), (rx + 272, y + 100)],
                 fill=(235, 70, 70))
    draw.text((rx + 14, y + 4), "TAIPEI -6.2%   SEOUL -5.2%   TOKYO -5.1%",
              font=deja(10, True), fill=(255, 220, 120))

    # gold horizon joining all three scenes
    hy = y + h - 26
    draw.line([(x, hy), (x + w, hy)], fill=GOLD, width=2)

    # scene label chips
    def chip(cx0, text):
        f = sans(9, True)
        twd = draw.textlength(text, font=f)
        draw.rectangle([cx0, y + h - 20, cx0 + twd + 12, y + h - 4],
                       fill=(20, 20, 20))
        draw.text((cx0 + 6, y + h - 19), text, font=f, fill=(255, 255, 255))

    chip(x + 8, "KYIV  ·  00:30 UTC")
    chip(mx0 + 8, "GOPALPUR  ·  02:00 UTC")
    chip(rx + 8, "TAIPEI  ·  05:30 UTC")


def draw_card_art(draw, kind, x, y, w, h, bg):
    """Small original pictogram for one front-grid card."""
    draw.rectangle([x, y, x + w, y + h], fill=bg)
    cx, cy = x + w // 2, y + h // 2
    if kind == "flags":
        # Union Jack (simplified) + EU circle of stars
        draw.rectangle([x + 4, cy - 12, x + 22, cy + 12], fill=(28, 48, 110))
        draw.line([(x + 4, cy - 12), (x + 22, cy + 12)], fill=(255, 255, 255), width=2)
        draw.line([(x + 4, cy + 12), (x + 22, cy - 12)], fill=(255, 255, 255), width=2)
        draw.line([(x + 13, cy - 12), (x + 13, cy + 12)], fill=(200, 30, 40), width=3)
        draw.line([(x + 4, cy), (x + 22, cy)], fill=(200, 30, 40), width=3)
        draw.rectangle([x + 26, cy - 12, x + 42, cy + 12], fill=(20, 40, 120))
        for k in range(12):
            ang = math.radians(k * 30)
            draw.ellipse([x + 34 + 6 * math.cos(ang) - 1, cy + 6 * math.sin(ang) - 1,
                          x + 34 + 6 * math.cos(ang) + 1, cy + 6 * math.sin(ang) + 1],
                         fill=(255, 220, 80))
    elif kind == "globe":
        draw.ellipse([cx - 14, cy - 14, cx + 14, cy + 14], fill=(90, 160, 200))
        draw.ellipse([cx - 8, cy - 12, cx + 2, cy - 2], fill=(80, 160, 90))
        draw.ellipse([cx - 2, cy + 2, cx + 10, cy + 12], fill=(80, 160, 90))
        draw.line([(cx + 16, cy - 16), (cx + 20, cy + 16)], fill=RED, width=3)
        draw.line([(cx + 16, cy - 16), (cx + 20, cy + 16)], fill=(255, 255, 255), width=1)
    elif kind == "missile":
        draw.polygon([(cx - 14, cy + 4), (cx + 10, cy + 4), (cx + 18, cy - 2),
                      (cx + 10, cy - 8), (cx - 14, cy - 8)], fill=(230, 230, 225))
        draw.polygon([(cx + 10, cy - 8), (cx + 18, cy - 2), (cx + 10, cy + 4)],
                     fill=RED)
        draw.line([(cx - 20, cy + 10), (cx - 8, cy + 2)], fill=(245, 200, 90), width=2)
        draw.line([(cx - 20, cy - 12), (cx - 8, cy - 4)], fill=(245, 200, 90), width=2)
    elif kind == "tank":
        draw.rectangle([x + 5, cy + 2, x + 41, cy + 12], fill=(40, 60, 40))
        draw.rectangle([x + 12, cy - 8, x + 30, cy + 2], fill=(52, 74, 52))
        draw.line([(x + 30, cy - 4), (x + 43, cy - 4)], fill=(52, 74, 52), width=3)
        for wx in (10, 20, 30):
            draw.ellipse([x + wx, cy + 12, x + wx + 6, cy + 18], fill=(20, 20, 20))
    elif kind == "crowd":
        for i, hx in enumerate((8, 18, 28, 38)):
            draw.ellipse([x + hx, cy - 12, x + hx + 7, cy - 5], fill=(240, 230, 210))
            draw.rectangle([x + hx - 1, cy - 4, x + hx + 8, cy + 12],
                           fill=(240, 230, 210))
        draw.rectangle([x + 6, cy - 20, x + 40, cy - 13], fill=(255, 255, 255))
        draw.line([(x + 22, cy - 13), (x + 22, cy - 6)], fill=(120, 100, 60), width=2)
    elif kind == "chartup":
        for i, hh in enumerate((8, 14, 12, 20, 26)):
            bx0 = x + 6 + i * 7
            draw.rectangle([bx0, cy + 14 - hh, bx0 + 5, cy + 14],
                           fill=(120, 180, 130))
        draw.line([(x + 6, cy - 12), (x + 18, cy - 2), (x + 28, cy - 8),
                   (x + 40, cy - 18)], fill=(235, 90, 90), width=2)
        draw.polygon([(x + 40, cy - 18), (x + 33, cy - 17), (x + 38, cy - 11)],
                     fill=(235, 90, 90))
    elif kind == "gavel":
        draw.line([(x + 12, cy + 12), (x + 36, cy - 12)], fill=(120, 82, 40), width=4)
        draw.rectangle([x + 26, cy - 16, x + 40, cy - 6], fill=(150, 105, 55))
        draw.rectangle([x + 8, cy + 12, x + 24, cy + 17], fill=(150, 105, 55))
    elif kind == "derrick":
        draw.line([(x + 12, cy + 16), (x + 20, cy - 16)], fill=(40, 32, 20), width=3)
        draw.line([(x + 34, cy + 16), (x + 26, cy - 16)], fill=(40, 32, 20), width=3)
        draw.line([(x + 14, cy + 4), (x + 32, cy + 4)], fill=(40, 32, 20), width=2)
        draw.line([(x + 20, cy - 16), (x + 38, cy - 10)], fill=(40, 32, 20), width=2)
        draw.ellipse([cx - 3, cy + 8, cx + 3, cy + 14], fill=(20, 20, 20))
    elif kind == "ballot":
        draw.rectangle([x + 8, cy - 4, x + 38, cy + 16], fill=(250, 248, 240))
        draw.rectangle([x + 16, cy - 4, x + 30, cy - 1], fill=(40, 40, 40))
        draw.polygon([(x + 18, cy - 14), (x + 26, cy - 20), (x + 30, cy - 12),
                      (x + 24, cy - 6)], fill=(255, 255, 255))
        draw.line([(x + 20, cy - 12), (x + 24, cy - 8), (x + 28, cy - 14)],
                  fill=RED, width=2)
    elif kind == "cricket":
        draw.rectangle([x + 6, cy - 14, x + 12, cy + 16], fill=(210, 180, 120))
        draw.rectangle([x + 6, cy + 10, x + 12, cy + 16], fill=(120, 82, 40))
        draw.ellipse([x + 30, cy - 4, x + 38, cy + 4], fill=RED)
        for sx in (20, 25, 30):
            draw.line([(x + sx, cy + 4), (x + sx, cy + 16)], fill=(240, 220, 140), width=2)
    elif kind == "chip":
        draw.rectangle([cx - 11, cy - 11, cx + 11, cy + 11], fill=(60, 120, 90))
        draw.rectangle([cx - 6, cy - 6, cx + 6, cy + 6], fill=(30, 60, 45))
        for px in (-8, 0, 8):
            draw.line([(cx + px, cy - 16), (cx + px, cy - 11)], fill=(200, 200, 190), width=2)
            draw.line([(cx + px, cy + 11), (cx + px, cy + 16)], fill=(200, 200, 190), width=2)
        draw.line([(cx + 12, cy + 12), (cx + 18, cy + 18)], fill=(235, 90, 90), width=2)
        draw.polygon([(cx + 18, cy + 18), (cx + 12, cy + 17), (cx + 17, cy + 12)],
                     fill=(235, 90, 90))
    elif kind == "tanker":
        draw.polygon([(x + 4, cy + 2), (x + 42, cy + 2), (x + 38, cy + 12),
                      (x + 8, cy + 12)], fill=(120, 50, 40))
        draw.rectangle([x + 26, cy - 8, x + 34, cy + 2], fill=(200, 200, 190))
        draw.polygon([(cx - 12, cy - 6), (cx - 8, cy - 14), (cx - 4, cy - 6),
                      (cx, cy - 14), (cx + 4, cy - 6)], fill=(245, 160, 60))
        draw.line([(x + 4, cy + 16), (x + 42, cy + 16)], fill=(220, 230, 235), width=2)


# simplified continent outlines (lon, lat), equirectangular
CONTINENTS = [
    [(-168, 66), (-140, 70), (-120, 72), (-95, 80), (-85, 66), (-75, 62),
     (-60, 47), (-70, 42), (-75, 35), (-80, 25), (-85, 20), (-95, 18),
     (-105, 22), (-115, 30), (-125, 40), (-125, 50), (-150, 60)],
    [(-55, 60), (-40, 65), (-30, 70), (-20, 74), (-35, 78), (-55, 75), (-60, 68)],
    [(-80, 10), (-75, 5), (-60, 0), (-50, -5), (-35, -8), (-40, -20),
     (-50, -30), (-60, -40), (-70, -50), (-75, -40), (-75, -20), (-80, -5)],
    [(-15, 15), (-10, 30), (0, 35), (10, 37), (20, 32), (30, 31), (35, 28),
     (40, 15), (48, 11), (45, 0), (40, -10), (35, -20), (30, -30),
     (20, -35), (15, -30), (12, -18), (8, -5), (0, 5), (-8, 5), (-15, 10)],
    [(-10, 36), (-10, 43), (-5, 48), (0, 50), (5, 55), (10, 58), (15, 55),
     (20, 60), (25, 65), (30, 70), (40, 68), (55, 70), (70, 72), (90, 75),
     (110, 75), (130, 72), (150, 70), (170, 66), (178, 65), (170, 60),
     (160, 55), (150, 45), (140, 40), (130, 35), (120, 30), (110, 20),
     (105, 10), (100, 8), (95, 15), (90, 22), (85, 20), (80, 10), (75, 8),
     (70, 20), (60, 25), (55, 28), (48, 30), (45, 25), (40, 20), (35, 15),
     (30, 12), (25, 10), (20, 12), (15, 15), (10, 20), (5, 25), (0, 30),
     (-5, 35)],
    [(113, -22), (120, -15), (130, -12), (140, -17), (147, -19), (153, -27),
     (150, -37), (140, -38), (130, -32), (120, -34), (113, -30)],
    [(-5, 50), (-3, 53), (-5, 56), (-2, 58), (0, 53), (1, 51), (-3, 50)],
    [(130, 31), (133, 34), (137, 35), (140, 38), (142, 42), (144, 44),
     (141, 40), (138, 36), (134, 33)],
    [(167, -45), (171, -41), (174, -38), (177, -37), (174, -41), (170, -44)],
]


def draw_map(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(214, 228, 232))
    draw.rectangle([x, y, x + w, y + h], outline=RULE)

    def proj(lon, lat):
        px = x + (lon + 170.0) / 360.0 * w
        py = y + (78.0 - lat) / 140.0 * h
        return px, py

    for poly in CONTINENTS:
        pts = [proj(lon, lat) for lon, lat in poly]
        draw.polygon(pts, fill=(222, 204, 160))
        draw.line(pts + [pts[0]], fill=(150, 128, 88), width=1)
    # numbered dots for the 15 front-page stories; small nudges keep the
    # crowded Europe / East Asia clusters legible
    f = deja(8, True)
    nudges = {1: (0, -7), 4: (-11, 3), 5: (9, 9), 6: (3, -13), 8: (-9, 11),
              9: (9, -5), 10: (-9, 5)}
    for i, (lon, lat) in enumerate(MAP_DOTS, start=1):
        px, py = proj(lon, lat)
        dx, dy = nudges.get(i, (0, 0))
        px, py = px + dx, py + dy
        r = 8
        draw.ellipse([px - r, py - r, px + r, py + r], fill=RED,
                     outline=(255, 255, 255), width=1)
        label = str(i)
        lw = draw.textlength(label, font=f)
        draw.text((px - lw / 2, py - 5), label, font=f, fill=(255, 255, 255))
    return y + h


# ---------------------------------------------------------------- build
def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- top kicker bar
    d.rectangle([0, 0, W, 24], fill=INK)
    d.text((MARGIN, 5), "THE WORLD IN ONE DAY", font=sans(11, True),
           fill=(255, 255, 255))
    right = "%d STORIES  ·  %d REGIONS  ·  EVERY STORY DATED FRIDAY 20 NOVEMBER 2026" % (
        TOTAL_STORIES, len(REGIONS))
    d.text((W - MARGIN - d.textlength(right, font=sans(10, True)), 6),
           right, font=sans(10, True), fill=(232, 220, 190))

    # ---- masthead
    title = "The World in One Day"
    tf = serif(56, True)
    d.text(((W - d.textlength(title, font=tf)) / 2, 30), title,
           font=tf, fill=INK)
    sub = ("Friday 20 November 2026  —  Kyiv's bridges, Cyclone Akvan, an AI sell-off, "
           "and a climate summit that ran out of time")
    sf = serif(15, False)
    d.text(((W - d.textlength(sub, font=sf)) / 2, 92), sub, font=sf,
           fill=INK_SOFT)
    d.line([(MARGIN, 112), (W - MARGIN, 112)], fill=INK, width=2)

    # ---- stats band: THE DAY IN NUMBERS
    y = 120
    d.text((MARGIN, y), "THE DAY IN NUMBERS", font=sans(10, True), fill=RED)
    y += 16
    cell_w = CONTENT_W / 6.0
    for i, (num, cap) in enumerate(STATS):
        cx = MARGIN + i * cell_w
        if i:
            d.line([(cx - 6, y), (cx - 6, y + 40)], fill=RULE, width=1)
        nf = serif(24, True)
        d.text((cx, y - 2), num, font=nf, fill=INK)
        lines = wrap(d, cap, sans(9), cell_w - 12)
        draw_lines(d, lines[:2], cx, y + 26, sans(9), INK_SOFT, 11)
    y += 46
    d.line([(MARGIN, y), (W - MARGIN, y)], fill=RULE, width=1)

    # ---- UTC timeline
    y += 8
    ty = y + 22
    d.text((MARGIN, ty - 5), "THE DAY IN UTC", font=sans(10, True), fill=RED)
    line_x0 = MARGIN + 108
    d.line([(line_x0, ty), (W - MARGIN - 8, ty)], fill=INK, width=2)
    slot = (W - MARGIN - 8 - line_x0) / len(TIMELINE)
    for i, (t, label) in enumerate(TIMELINE):
        cx = line_x0 + slot * (i + 0.5)
        d.ellipse([cx - 4, ty - 4, cx + 4, ty + 4], fill=RED,
                  outline=(255, 255, 255), width=1)
        tf2 = sans(10, True)
        d.text((cx - d.textlength(t, font=tf2) / 2, ty - 16), t, font=tf2,
               fill=INK)
        lines = wrap(d, label, sans(8, False), slot - 8)
        ly = ty + 8
        for li, line in enumerate(lines[:2]):
            d.text((cx - d.textlength(line, font=sans(8)) / 2, ly + li * 10),
                   line, font=sans(8), fill=INK_SOFT)
    y = ty + 30
    d.line([(MARGIN, y), (W - MARGIN, y)], fill=RULE, width=1)

    # ---- triptych panorama (one continuous illustration)
    y += 8
    pano_h = 94
    draw_panorama(d, MARGIN, y, CONTENT_W, pano_h)
    y += pano_h + 10

    # ---- three lead columns
    col_w = (CONTENT_W - 2 * 16) / 3.0
    lead_top = y
    for i, lead in enumerate(LEADS):
        cx = MARGIN + i * (col_w + 16)
        num_f = serif(20, True)
        d.text((cx, lead_top), "%d" % lead["num"], font=num_f, fill=RED)
        kf = sans(10, True)
        d.text((cx + 24, lead_top + 6), lead["kicker"], font=kf, fill=RED)
        hy = lead_top + 26
        head_lines = wrap(d, lead["head"], serif(19, True), col_w)
        hy = draw_lines(d, head_lines[:2], cx, hy, serif(19, True), INK, 22)
        deck_lines = wrap(d, lead["deck"], sans(11), col_w)
        hy = draw_lines(d, deck_lines[:3], cx, hy + 4, sans(11), INK_SOFT, 14)
        d.text((cx, hy + 4), lead["source"], font=serif(10, False),
               fill=GREY)
        if i < 2:
            d.line([(cx + col_w + 8, lead_top),
                    (cx + col_w + 8, lead_top + 124)], fill=RULE, width=1)
    y = lead_top + 132
    d.line([(MARGIN, y), (W - MARGIN, y)], fill=INK, width=2)

    # ---- twelve more fronts
    y += 8
    d.text((MARGIN, y), "TWELVE MORE FRONTS", font=sans(11, True), fill=RED)
    note = "Each with its own drawing  ·  sources named beside every story"
    d.text((W - MARGIN - d.textlength(note, font=sans(9)), y + 1), note,
           font=sans(9), fill=GREY)
    y += 20
    card_w = (CONTENT_W - 3 * 8) / 4.0
    card_h = 56
    for idx, card in enumerate(CARDS):
        row, col = divmod(idx, 4)
        cx = MARGIN + col * (card_w + 8)
        cy = y + row * (card_h + 4)
        d.rectangle([cx, cy, cx + card_w, cy + card_h], fill=CARD_BG,
                    outline=RULE)
        draw_card_art(d, card["kind"], cx + 1, cy + 1, 44, card_h - 2,
                      card["bg"])
        tx = cx + 50
        twd = card_w - 56
        d.text((tx, cy + 4), card["kicker"], font=sans(8, True), fill=RED)
        head_lines = wrap(d, card["head"], sans(11, True), twd)
        hy2 = draw_lines(d, head_lines[:2], tx, cy + 16, sans(11, True),
                         INK, 13)
        d.text((tx, hy2 + 1), card["deck"], font=sans(9), fill=INK_SOFT)
    y += 3 * card_h + 2 * 4 + 8
    d.line([(MARGIN, y), (W - MARGIN, y)], fill=RULE, width=1)

    # ---- region tally strip
    y += 7
    counts = {r: 0 for r in REGIONS}
    for lead in LEADS:
        counts[lead["region"]] += 1
    for card in CARDS:
        counts[card["region"]] += 1
    for _, _, _, region in ALSO:
        counts[region] += 1
    assert sum(counts.values()) == TOTAL_STORIES, counts
    chip_w = CONTENT_W / len(REGIONS)
    for i, region in enumerate(REGIONS):
        cx = MARGIN + i * chip_w
        label = "%s %d" % (region, counts[region])
        f = sans(9, True)
        lw = d.textlength(label, font=f)
        if i % 2 == 0:
            d.rectangle([cx + 2, y, cx + chip_w - 2, y + 16], fill=PAPER_DARK)
        d.text((cx + (chip_w - lw) / 2, y + 3), label, font=f, fill=INK)
    y += 24

    # ---- bottom zone: map + also index
    d.text((MARGIN, y), "WHERE IT HAPPENED", font=sans(11, True), fill=RED)
    d.text((MARGIN + 296, y), "ALSO ON FRIDAY  —  %d MORE STORIES" % len(ALSO),
           font=sans(11, True), fill=RED)
    y += 18
    map_w, map_h = 280, 184
    draw_map(d, MARGIN, y, map_w, map_h)
    d.text((MARGIN, y + map_h + 4),
           "Each number is the story with that number on this page.",
           font=serif(10, False), fill=GREY)
    d.text((MARGIN, y + map_h + 17),
           "Dots mark stories 1-15; the full index runs to 67.",
           font=serif(10, False), fill=GREY)

    # also index: 3 columns, one line per story, font auto-fits the column
    list_x = MARGIN + 296
    list_w = CONTENT_W - 296
    col_w2 = (list_w - 2 * 10) / 3.0
    per_col = (len(ALSO) + 2) // 3
    row_h = 12
    for ci in range(3):
        chunk = ALSO[ci * per_col:(ci + 1) * per_col]
        cx = list_x + ci * (col_w2 + 10)
        for ri, (num, text, source, _region) in enumerate(chunk):
            full = "%d  %s  (%s)" % (num, text, source)
            size = fit_font(d, full, col_w2, 10, 8)
            assert d.textlength(full, font=sans(size)) <= col_w2, full
            d.text((cx, y + ri * row_h), full, font=sans(size), fill=INK)
    y += map_h + 30
    d.line([(MARGIN, y), (W - MARGIN, y)], fill=RULE, width=1)

    # ---- date-check footer
    y += 6
    box_h = 38
    d.rectangle([MARGIN, y, W - MARGIN, y + box_h], outline=RED, width=2)
    d.text((MARGIN + 8, y + 5), "DATE CHECK", font=sans(10, True), fill=RED)
    check = ("Left out as Thursday 19 November's news: the World Court's Myanmar "
             "ruling, the three-leader declaration in Shenzhen, Tonga's drought "
             "emergency and the migrant boat lost off Senegal. Not yet happened: "
             "BepiColombo's Mercury orbit capture, any final COP31 text, the ATP "
             "Finals final (Sun 22) and Estonia's border closure (1 Dec).")
    lines = wrap(d, check, sans(9), CONTENT_W - 108)
    draw_lines(d, lines[:3], MARGIN + 96, y + 5, sans(9), INK_SOFT, 11)
    y += box_h + 6
    foot = ("Every story here happened, or was first reported, on Friday 20 November 2026. "
            "Official counts are attributed. Sources named beside each story - original drawings.")
    d.text((MARGIN, y), foot, font=serif(9, False), fill=GREY)

    assert y + 12 <= H, "layout overflow: %d" % y
    return img


def main():
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img = build()
    assert img.size == (1024, 1024) and img.mode == "RGB"
    img.save(out, format="PNG")
    print("wrote %s (%dx%d %s)" % (out, img.size[0], img.size[1], img.mode))


if __name__ == "__main__":
    main()
