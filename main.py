#!/usr/bin/env python3
"""ONE DAY ON EARTH - Friday 20 November 2026.
A one-page newspaper front page summing up the world's news of
Friday 20 November 2026 in a single 1024x1024 image.

Deterministic: stdlib + Pillow only, no network, no randomness, no clock.
Running `python3 main.py` twice produces byte-identical entry.png.

All 40 stories were checked against wire reporting of the day
(Reuters, AP, BBC, Al Jazeera, IMD, Xinhua, PTI, Sky News, UKMTO).
Every story happened, or was first reported, on Friday 20 November 2026.
"""
import hashlib
import os
import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
M = 26                      # outer margin
CW = W - 2 * M              # content width = 972

PAPER = (246, 241, 229)
INK = (22, 22, 22)
NAVY = (22, 35, 63)
RED = (179, 39, 30)
TEAL = (15, 118, 110)
GOLD = (185, 138, 29)
SLATE = (71, 85, 105)
LIGHT_LINE = (190, 180, 160)
PANEL = (255, 253, 247)
GREEN = (21, 128, 61)

REGION_COLORS = {
    "Europe": (29, 78, 216),
    "Asia": (179, 39, 30),
    "Americas": (15, 118, 110),
    "Africa": (180, 83, 9),
    "Middle East": (124, 58, 237),
    "Oceania": (2, 132, 199),
    "Global": (71, 85, 105),
}

FDIR = "/usr/share/fonts/truetype/noto"


def F(name, size):
    return ImageFont.truetype(os.path.join(FDIR, name), size)


def fonts():
    return {
        "mast": F("NotoSerifDisplay-Black.ttf", 57),
        "serif_b": F("NotoSerif-Bold.ttf", 17),
        "serif": F("NotoSerif-Regular.ttf", 12),
        "serif_i": F("NotoSerif-Italic.ttf", 16),
        "serif_sm": F("NotoSerif-Regular.ttf", 11),
        "sans_b": F("NotoSans-Bold.ttf", 11),
        "sans": F("NotoSans-Regular.ttf", 11),
        "sans_sm": F("NotoSans-Regular.ttf", 9),
        "sans_xs": F("NotoSans-Regular.ttf", 8),
        "kpi": F("NotoSerifDisplay-Black.ttf", 24),
    }


# ---------------------------------------------------------------- text tools
def wrap(draw, text, font, max_w):
    """Greedy word wrap measured with the real font. Returns lines."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


TRUNCATED = []


def draw_wrapped(draw, x, y, text, font, max_w, fill=INK, leading=None, max_lines=None):
    """Draw wrapped text; returns (lines_drawn, height_used)."""
    if leading is None:
        leading = font.size + 2
    lines = wrap(draw, text, font, max_w)
    if max_lines is not None and len(lines) > max_lines:
        TRUNCATED.append(text)
        lines = lines[:max_lines]
    for ln in lines:
        draw.text((x, y), ln, font=font, fill=fill)
        y += leading
    return len(lines), len(lines) * leading


def check_fit(draw, text, font, max_w, what):
    """Fail loudly if a single line would overflow its box."""
    if draw.textlength(text, font=font) > max_w:
        raise SystemExit(f"OVERFLOW in {what}: {text!r} "
                         f"({draw.textlength(text, font=font):.0f} > {max_w})")


# ---------------------------------------------------------------- data
# (number, region, place, headline, dek, source)
HEROES = [
    (1, "Europe", "KYIV, UKRAINE · WAR",
     "Russian missiles hit three Kyiv bridges",
     "About 110 missiles and 400 drones hit Ukraine; at least eight killed, "
     "power and water cut in Kyiv.",
     "Kyiv Independent · BBC · Reuters"),
    (2, "Asia", "ODISHA, INDIA · CYCLONE",
     "Cyclone Akvan comes ashore in eastern India",
     "The storm crossed near Gopalpur at 70–80 km/h after 372,000 were moved "
     "to shelters. No deaths reported.",
     "IMD · The Hindu"),
    (3, "Asia", "TAIPEI · SEOUL · TOKYO · MARKETS",
     "AI sell-off sinks Asia's stock markets",
     "Taiwan fell 6.2% to end its worst week since 1991; Seoul \u20135.2%, "
     "Tokyo \u20135.1% as chips led the slide.",
     "Reuters · Al Jazeera"),
]

# (number, region, place, tag, headline, dek, source, pictogram key)
FEATURES = [
    (4, "Europe", "EASTERN POLAND · CONFLICT", "POLAND: MISSILE",
     "Russian cruise missile lands in Poland",
     "It fell in a field in Lublin; NATO calls it a grave violation.",
     "Reuters", "missile"),
    (5, "Europe", "BRUSSELS · DIPLOMACY", "EUROPE: TALKS",
     "European leaders ready to negotiate with Russia",
     "Zelensky\u2019s reply: \u201cPutin is a killer.\u201d",
     "Reuters", "talks"),
    (6, "Europe", "BRUSSELS · SUMMIT", "UK–EU: DEAL",
     "UK and EU seal a \u201creset\u201d deal",
     "Food trade, carbon markets, youth visas.",
     "Reuters", "flags"),
    (7, "Asia", "THE HAGUE · COURT", "MYANMAR: COURT",
     "Myanmar rejects world court's genocide ruling",
     "Calls it \u201cunfair\u201d; rights groups urge sanctions.",
     "Reuters · AP", "court"),
    (8, "Americas", "NEW YORK · TECH", "ANTHROPIC: IPO",
     "Anthropic slides on day two after record IPO",
     "Shares fell after hours on an Apple rival report.",
     "Bloomberg", "ipo"),
    (9, "Asia", "ANTALYA · CLIMATE", "COP31: NO DEAL",
     "COP31 runs into overtime with no deal",
     "Draft drops fossil fuels and the $120bn target.",
     "BBC · AP", "cop"),
    (10, "Middle East", "RIYADH · CONFLICT", "RIYADH: STRIKE",
     "Houthi strike damages tower in Riyadh",
     "Riyadh downs 3 missiles; coalition hits Hodeidah.",
     "Reuters", "tower"),
    (11, "Europe", "KERCH STRAIT · CONFLICT", "KERCH: BRIDGE",
     "Third strike this week hits Crimea Bridge",
     "Rail traffic halted; Putin vows a painful response.",
     "Reuters", "bridge"),
    (12, "Middle East", "STRAIT OF HORMUZ · ENERGY", "HORMUZ: TANKER",
     "Oil tanker catches fire near Hormuz",
     "US sanctions four Iranian oil trustees the same day.",
     "Reuters", "tanker"),
    (13, "Africa", "NAIROBI · HEALTH", "KENYA: EBOLA",
     "Kenya starts 42-day Ebola-free countdown",
     "No new cases as the watch for a clean declaration begins.",
     "AP", "shield"),
    (14, "Americas", "WASHINGTON · POLITICS", "SENATE: VOTE",
     "US Senate passes permitting overhaul 62–33",
     "Energy projects get faster approvals.",
     "Reuters", "dome"),
    (15, "Americas", "PORT-AU-PRINCE · SECURITY", "HAITI: RAID",
     "Police say 34 gang suspects killed in raid",
     "Thursday's Martissant operation retakes the Route 2 corridor.",
     "AP", "raid"),
]

# (number, place, text, source) — one line each
ALSO = [
    (16, "TOKYO", "Japan's core inflation rises 2.2%; a December rate rise firms", "Reuters"),
    (17, "MUMBAI", "Sensex rises 1.1%, bucking Asia's slide", "Reuters"),
    (18, "TOKYO", "SoftBank shares fall more than 14% in a day", "Al Jazeera"),
    (19, "SEOUL", "Kospi ends the week 7.9% lower", "Anadolu"),
    (20, "BEIJING", "China holds loan rates for an 18th month", "Xinhua"),
    (21, "GANJAM", "209 mm of rain falls as Akvan crosses Odisha", "PTI"),
    (22, "SYDNEY", "Australian shares fall 1.8% in the sell-off", "Reuters"),
    (23, "COOK ISLANDS", "Emergency declared ahead of Cyclone Xavier", "Wire reports"),
    (24, "GOLD", "Gold falls almost 4%; Bitcoin down 24% in a month", "Reuters"),
    (25, "WASHINGTON", "Justice Dept clears the $66.8bn NextEra–Dominion deal", "Reuters"),
    (26, "WASHINGTON", "SEC proposes taking direct control of the audit trail", "Reuters"),
    (27, "WASHINGTON", "Trump names Kirsten Davies national cyber director", "AP"),
    (28, "WASHINGTON", "Judge says she will block Trump's 250-foot arch", "AP"),
    (29, "MIAMI", "Priest gets life for plot to kill Haiti's Moïse", "AP"),
    (30, "WASHINGTON", "Congress risks a pre-Christmas shutdown over Iran war funds", "AP"),
    (31, "HOUSTON", "Stroud throws three TDs as Texans rout Colts 26–3", "AP"),
    (32, "LVIV", "Strike on a railway station kills two", "BBC"),
    (33, "BERLIN", "School pupils strike against military service", "Al Jazeera"),
    (34, "LONDON", "General says UK runs cyber attacks abroad", "Sky News"),
    (35, "MOSCOW", "Russia declines Estonia's border closure", "Reuters"),
    (36, "ANTALYA", "EU official calls the climate draft \u201cunacceptable\u201d", "RTE"),
    (37, "KAMPALA", "Police told to enforce Ebola ban on rallies", "allAfrica"),
    (38, "LILONGWE", "Fuel crisis brings night-long petrol queues", "Al Jazeera"),
    (39, "ABIDJAN", "AfDB: 22 countries are in debt distress", "allAfrica"),
    (40, "OFF YEMEN", "Gunmen fire on a cargo ship off the coast", "UKMTO"),
]

KPI = [
    ("400", "drones in the overnight barrage"),
    ("372,000", "people moved to shelters"),
    ("–6.2%", "Taiwan's Taiex, Friday"),
    ("–3.7%", "S&P 500, into correction"),
    ("100,000", "youth visas a year"),
    ("62–33", "Senate permitting vote"),
]

REGIONS = [("Europe", 10), ("Asia", 10), ("Americas", 10), ("Africa", 4),
           ("Middle East", 3), ("Oceania", 2), ("Global", 1)]

MARKETS = [("Taiex", "–6.2%"), ("Kospi", "–5.2%"), ("Nikkei", "–5.1%"),
           ("Hang Seng", "–1.9%"), ("S&P 500", "–3.7%"), ("Nasdaq", "–5.3%"),
           ("Sensex", "+1.1%")]

TIMELINE = [
    ("01:25", "KYIV", "Barrage begins: missiles and drones hit the capital"),
    ("07:30", "GOPALPUR", "Cyclone Akvan makes landfall on the Odisha coast"),
    ("11:20", "GOPALPUR", "Landfall complete; storm weakens to a deep depression"),
    ("15:00", "ANTALYA", "COP31 deadline passes with no deal; talks run overtime"),
    ("21:00", "NEW YORK", "Wall Street closes: S&P 500 down 3.7%, in correction"),
]

# story number -> (lon, lat, dx, dy) on the stylised map
PINS = {
    1: (30.5, 50.5, 0, -9), 2: (84.9, 19.3, 0, 0), 3: (121.5, 25.0, 0, -8),
    4: (22.5, 51.2, 7, -8), 5: (4.4, 50.8, 13, 9), 6: (-0.1, 51.5, 0, 0),
    7: (96.2, 19.8, 0, 9), 8: (-122.4, 37.8, 0, 0), 9: (30.7, 36.9, 0, 8),
    10: (46.7, 24.6, 0, 0), 11: (36.4, 45.3, 9, 3), 12: (56.5, 26.6, 0, 0),
    13: (36.8, -1.3, 0, 0), 14: (-77.0, 38.9, 0, -8), 15: (-72.3, 18.5, 0, 8),
}

CONTINENTS = {
    "NA": [(-168, 66), (-140, 70), (-125, 72), (-110, 73), (-95, 80), (-85, 70),
           (-75, 62), (-60, 55), (-55, 47), (-65, 44), (-75, 35), (-80, 26),
           (-90, 21), (-97, 16), (-105, 20), (-115, 28), (-125, 40),
           (-140, 60), (-165, 60)],
    "SA": [(-80, 10), (-75, 5), (-60, 0), (-50, -5), (-35, -8), (-40, -20),
           (-50, -30), (-60, -38), (-68, -52), (-70, -40), (-75, -25),
           (-80, -15)],
    "EU": [(-10, 36), (-9, 43), (-2, 48), (0, 50), (5, 58), (10, 58),
           (18, 56), (21, 55), (24, 60), (30, 70), (40, 68), (45, 60),
           (40, 50), (30, 46), (23, 40), (19, 42), (12, 44), (8, 38),
           (3, 38), (-2, 37)],
    "AF": [(-17, 15), (-10, 30), (0, 36), (10, 37), (20, 32), (32, 31),
           (35, 28), (43, 12), (51, 11), (48, 0), (40, -12), (35, -25),
           (28, -33), (20, -35), (15, -27), (12, -18), (9, -2), (9, 4),
           (-8, 5), (-13, 8)],
    "AS": [(40, 68), (50, 70), (60, 70), (70, 72), (80, 73), (90, 75),
           (110, 76), (130, 72), (150, 70), (170, 67), (178, 65),
           (170, 60), (160, 55), (155, 50), (142, 45), (140, 38),
           (135, 35), (130, 32), (127, 35), (122, 38), (120, 30),
           (115, 22), (108, 18), (105, 10), (100, 8), (97, 15), (92, 20),
           (88, 22), (80, 15), (77, 8), (72, 20), (66, 25), (60, 25),
           (55, 26), (50, 28), (48, 30), (43, 35), (40, 40), (38, 45),
           (40, 50)],
    "OC": [(113, -22), (114, -30), (115, -35), (124, -33), (130, -32),
           (137, -35), (140, -38), (145, -38), (150, -37), (153, -27),
           (150, -22), (146, -19), (142, -11), (136, -12), (132, -11),
           (126, -14), (122, -17), (118, -20)],
}


# ---------------------------------------------------------------- illustrations
def hero_kyiv(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(16, 24, 48))
    for sx, sy, r in [(14, 12, 1), (60, 22, 1), (120, 8, 1), (180, 18, 1),
                      (240, 10, 1), (290, 26, 1), (40, 34, 1), (200, 34, 1)]:
        d.ellipse([x + sx - r, y + sy - r, x + sx + r, y + sy + r], fill=(240, 230, 180))
    # river
    d.rectangle([x, y + h - 26, x + w, y + h], fill=(30, 58, 96))
    d.line([x, y + h - 26, x + w, y + h - 26], fill=(90, 140, 190), width=1)
    # skyline
    for bx, bw, bh in [(8, 26, 30), (40, 18, 42), (64, 30, 26), (100, 20, 48),
                       (126, 34, 32), (168, 22, 44), (196, 28, 28), (230, 24, 40),
                       (260, 30, 34), (292, 18, 26)]:
        d.rectangle([x + bx, y + h - 26 - bh, x + bx + bw, y + h - 26], fill=(10, 16, 34))
        d.rectangle([x + bx + 4, y + h - 26 - bh + 6, x + bx + 8, y + h - 26 - bh + 10],
                    fill=(250, 200, 90))
    # three bridges across the river
    for bx in (30, 140, 250):
        d.line([x + bx, y + h - 24, x + bx + 52, y + h - 24], fill=(235, 235, 240), width=4)
        d.arc([x + bx + 8, y + h - 36, x + bx + 44, y + h - 12], 180, 360, fill=(235, 235, 240), width=2)
        d.line([x + bx + 12, y + h - 32, x + bx + 12, y + h - 24], fill=(235, 235, 240), width=2)
        d.line([x + bx + 40, y + h - 32, x + bx + 40, y + h - 24], fill=(235, 235, 240), width=2)
    # fires on two bridges
    for fx in (52, 268):
        d.ellipse([x + fx - 5, y + h - 32, x + fx + 5, y + h - 22], fill=(255, 140, 40))
        d.ellipse([x + fx - 2, y + h - 29, x + fx + 2, y + h - 25], fill=(255, 220, 120))
    # missile arcs (dashed red)
    for ax0, ay0, ax1, ay1 in [(20, 8, 150, 66), (180, 4, 290, 60)]:
        for t in range(0, 11, 2):
            px = ax0 + (ax1 - ax0) * t / 10
            py = ay0 + (ay1 - ay0) * (t / 10) ** 0.6
            d.ellipse([x + px - 2, y + py - 2, x + px + 2, y + py + 2], fill=(255, 90, 70))
    d.ellipse([x + 148, y + 64, x + 152, y + 68], fill=(255, 220, 120))


def hero_cyclone(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(23, 84, 120))
    # land: simplified east coast of India (right side)
    land = [(x + w - 8, y + 8), (x + w - 8, y + h - 8), (x + w - 46, y + h - 8),
            (x + w - 58, y + h - 40), (x + w - 84, y + h - 58), (x + w - 66, y + h - 82),
            (x + w - 96, y + 40), (x + w - 72, y + 8)]
    d.polygon(land, fill=(196, 164, 110))
    d.line(land + [land[0]], fill=(140, 110, 70), width=1)
    # cyclone spiral centred left of the coast
    cx, cy = x + w // 2 - 42, y + h // 2 + 4
    for r, col in [(46, (255, 255, 255)), (36, (220, 235, 245)),
                   (26, (255, 255, 255)), (16, (220, 235, 245))]:
        d.arc([cx - r, cy - r, cx + r, cy + r], 20, 300, fill=col, width=4)
    d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=(179, 39, 30))
    # track dots approaching the coast
    for i, (tx, ty) in enumerate([(cx - 120, cy - 26), (cx - 88, cy - 14),
                                  (cx - 56, cy - 4), (cx - 26, cy + 2)]):
        d.ellipse([x + tx - 3, y + ty - 3, x + tx + 3, y + ty + 3],
                  fill=(255, 220, 120) if i < 3 else (255, 90, 70))
    # rain streaks
    for rx, ry in [(30, 12), (52, 30), (80, 8), (110, 26), (250, 70), (280, 40)]:
        d.line([x + rx, y + ry, x + rx - 5, y + ry + 12], fill=(200, 225, 240), width=2)
    # landfall marker
    lx, ly = x + w - 84, y + h - 60
    d.ellipse([lx - 5, ly - 5, lx + 5, ly + 5], outline=(179, 39, 30), width=2)
    d.ellipse([lx - 2, ly - 2, lx + 2, ly + 2], fill=(179, 39, 30))


def hero_markets(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(20, 26, 34))
    # grid
    for gy in range(1, 4):
        yy = y + h * gy // 4
        d.line([x + 8, yy, x + w - 8, yy], fill=(60, 70, 82), width=1)
    # descending bars
    vals = [0.92, 0.80, 0.86, 0.62, 0.70, 0.44, 0.52]
    bw = (w - 24) // len(vals)
    for i, v in enumerate(vals):
        bx = x + 12 + i * bw
        bh = int((h - 34) * v)
        col = (46, 160, 90) if i == len(vals) - 1 else (200, 60, 50)
        d.rectangle([bx + 3, y + h - 16 - bh, bx + bw - 3, y + h - 16], fill=col)
    # falling line with arrow
    pts = [(x + 14 + i * bw, y + 14 + int(i * (h - 44) / (len(vals) - 1)))
           for i in range(len(vals))]
    d.line(pts, fill=(255, 90, 70), width=3, joint="curve")
    ex, ey = pts[-1]
    d.polygon([(ex, ey + 2), (ex - 12, ey - 4), (ex - 4, ey + 10)], fill=(255, 90, 70))
    d.text((x + 10, y + 6), "TAIPEI –6.2%   SEOUL –5.2%   TOKYO –5.1%",
           font=F("NotoSans-Bold.ttf", 10), fill=(255, 255, 255))


def pictogram(d, x, y, w, h, key):
    """Small original icon-scene for a feature tile (56x56 box)."""
    d.rectangle([x, y, x + w, y + h], fill=(232, 226, 208))
    d.rectangle([x, y, x + w, y + h], outline=LIGHT_LINE)
    cx, cy = x + w // 2, y + h // 2
    if key == "missile":
        d.rectangle([x, y + 34, x + w, y + h], fill=(120, 170, 90))
        d.polygon([(cx - 4, cy - 16), (cx + 4, cy - 16), (cx + 10, cy + 2),
                   (cx - 10, cy + 2)], fill=(179, 39, 30))
        d.line([cx, cy + 2, cx, cy + 16], fill=(255, 140, 40), width=3)
    elif key == "talks":
        for i, col in enumerate([(29, 78, 216), (179, 39, 30), (15, 118, 110)]):
            d.ellipse([x + 8 + i * 15, cy - 8, x + 20 + i * 15, cy + 4], fill=col)
        d.line([x + 8, cy + 12, x + w - 8, cy + 12], fill=INK, width=2)
    elif key == "flags":
        d.rectangle([x + 8, cy - 12, x + 24, cy + 10], fill=(29, 78, 216))
        d.line([x + 8, cy - 12, x + 24, cy + 10], fill=(255, 255, 255), width=2)
        d.line([x + 24, cy - 12, x + 8, cy + 10], fill=(255, 255, 255), width=2)
        d.rectangle([x + 30, cy - 12, x + 46, cy + 10], fill=(22, 35, 63))
        for sx, sy in [(38, cy - 8), (33, cy - 3), (43, cy - 3), (35, cy + 4), (41, cy + 4)]:
            d.ellipse([sx - 1, sy - 1, sx + 1, sy + 1], fill=(255, 220, 90))
    elif key == "court":
        d.rectangle([x + 10, cy - 14, x + w - 10, cy - 10], fill=INK)
        for px in (14, 24, 34):
            d.rectangle([x + px, cy - 10, x + px + 4, cy + 8], fill=INK)
        d.rectangle([x + 8, cy + 8, x + w - 8, cy + 12], fill=INK)
    elif key == "ipo":
        d.rectangle([x + 8, cy + 6, x + 16, cy + 14], fill=(179, 39, 30))
        d.rectangle([x + 20, cy - 2, x + 28, cy + 14], fill=(179, 39, 30))
        d.rectangle([x + 32, cy - 10, x + 40, cy + 14], fill=(179, 39, 30))
        d.line([x + 8, cy - 14, x + 46, cy - 18], fill=INK, width=2)
        d.polygon([(x + 46, cy - 18), (x + 38, cy - 20), (x + 42, cy - 10)], fill=INK)
    elif key == "cop":
        d.ellipse([cx - 13, cy - 13, cx + 13, cy + 13], fill=(46, 140, 190))
        d.arc([cx - 13, cy - 13, cx + 13, cy + 13], 200, 340, fill=(120, 200, 120), width=5)
        d.line([cx + 16, cy - 14, cx + 16, cy + 6], fill=(179, 39, 30), width=3)
        d.ellipse([cx + 13, cy + 3, cx + 19, cy + 9], fill=(179, 39, 30))
    elif key == "tower":
        d.polygon([(cx - 8, cy + 16), (cx - 4, cy - 16), (cx + 4, cy - 16),
                   (cx + 8, cy + 16)], fill=(40, 50, 70))
        d.line([cx - 2, cy - 16, cx - 2, cy + 16], fill=(255, 220, 90), width=1)
        d.line([x + 6, cy - 14, cx - 2, cy - 6], fill=(255, 90, 70), width=2)
    elif key == "bridge":
        d.rectangle([x, cy + 8, x + w, y + h], fill=(90, 140, 190))
        d.line([x + 6, cy - 2, x + w - 6, cy - 2], fill=INK, width=3)
        d.line([x + 14, cy - 2, x + 14, cy + 8], fill=INK, width=2)
        d.line([x + w - 14, cy - 2, x + w - 14, cy + 8], fill=INK, width=2)
        d.line([cx - 8, cy - 2, cx + 8, cy - 2], fill=(179, 39, 30), width=3)
    elif key == "tanker":
        d.rectangle([x, y + 30, x + w, y + h], fill=(60, 110, 160))
        d.polygon([(x + 8, cy + 8), (x + 46, cy + 8), (x + 42, cy + 16),
                   (x + 12, cy + 16)], fill=(120, 60, 40))
        d.rectangle([x + 30, cy - 2, x + 38, cy + 8], fill=(200, 200, 210))
        d.ellipse([cx - 4, cy - 14, cx + 4, cy - 6], fill=(255, 140, 40))
        d.ellipse([cx - 2, cy - 11, cx + 2, cy - 7], fill=(255, 220, 120))
    elif key == "shield":
        d.polygon([(cx, cy - 15), (cx + 12, cy - 9), (cx + 12, cy + 4),
                   (cx, cy + 15), (cx - 12, cy + 4), (cx - 12, cy - 9)], fill=(15, 118, 110))
        d.line([cx - 5, cy, cx - 1, cy + 5, cx + 6, cy - 5], fill=(255, 255, 255), width=2)
    elif key == "dome":
        d.rectangle([x + 8, cy + 8, x + w - 8, cy + 12], fill=INK)
        d.pieslice([cx - 12, cy - 12, cx + 12, cy + 8], 180, 360, fill=INK)
        d.rectangle([cx - 1, cy - 18, cx + 1, cy - 12], fill=INK)
    elif key == "raid":
        d.ellipse([cx - 13, cy - 13, cx + 13, cy + 13], outline=INK, width=2)
        d.polygon([(cx, cy - 9), (cx + 3, cy - 2), (cx + 9, cy - 2), (cx + 4, cy + 3),
                   (cx + 6, cy + 9), (cx, cy + 5), (cx - 6, cy + 9), (cx - 4, cy + 3),
                   (cx - 9, cy - 2), (cx - 3, cy - 2)], fill=(179, 39, 30))


# ---------------------------------------------------------------- build
def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    f = fonts()
    sans_b = f["sans_b"]
    sans = f["sans"]
    sans_sm = f["sans_sm"]
    sans_xs = f["sans_xs"]

    y = 14
    # ---- top bar
    d.text((M, y), "ONE DAY ON EARTH", font=F("NotoSans-Bold.ttf", 13), fill=RED)
    right = "40 STORIES  ·  7 REGIONS  ·  ALL DATED FRIDAY 20 NOVEMBER 2026"
    check_fit(d, right, F("NotoSans-Bold.ttf", 11), CW - 220, "top bar right")
    d.text((W - M - d.textlength(right, font=F("NotoSans-Bold.ttf", 11)), y),
           right, font=F("NotoSans-Bold.ttf", 11), fill=INK)
    y += 20
    d.line([M, y, W - M, y], fill=INK, width=2)
    y += 8

    # ---- masthead
    title = "Friday 20 November 2026"
    check_fit(d, title, f["mast"], CW, "masthead")
    d.text((M, y), title, font=f["mast"], fill=INK)
    y += 64
    deck = ("Russian missiles hit Kyiv\u2019s bridges  ·  Cyclone Akvan strikes India  ·  "
            "An AI sell-off sinks Asia\u2019s markets  ·  UK and EU seal a deal")
    check_fit(d, deck, f["serif_i"], CW, "deck")
    d.text((M, y), deck, font=f["serif_i"], fill=INK)
    y += 24
    d.line([M, y, W - M, y], fill=INK, width=1)

    # ---- KPI strip: THE DAY IN NUMBERS
    y += 6
    d.text((M, y), "THE DAY IN NUMBERS", font=sans_b, fill=RED)
    y += 13
    box_w = (CW - 5 * 6) // 6
    for i, (val, lab) in enumerate(KPI):
        bx = M + i * (box_w + 6)
        d.rectangle([bx, y, bx + box_w, y + 46], fill=PANEL, outline=LIGHT_LINE)
        d.rectangle([bx, y, bx + box_w, y + 3], fill=RED)
        check_fit(d, val, f["kpi"], box_w - 12, f"kpi {val}")
        d.text((bx + 6, y + 5), val, font=f["kpi"], fill=INK)
        draw_wrapped(d, bx + 6, y + 33, lab, sans_xs, box_w - 12, fill=SLATE,
                     leading=9, max_lines=1)
    y += 46

    # ---- region chips
    y += 6
    cx = M
    for name, n in REGIONS:
        col = REGION_COLORS[name]
        label = f"{name.upper()} {n}"
        tw = d.textlength(label, font=sans_b) + 16
        d.rounded_rectangle([cx, y, cx + tw, y + 18], radius=3, fill=col)
        d.text((cx + 8, y + 3), label, font=sans_b, fill=(255, 255, 255))
        cx += tw + 6
    d.text((cx + 4, y + 3), "STORIES BY REGION", font=sans_b, fill=SLATE)
    y += 24

    # ---- heroes
    col_w = (CW - 2 * 12) // 3
    hero_top = y
    hero_draw = [hero_kyiv, hero_cyclone, hero_markets]
    for i, (num, region, place, head, dek, src) in enumerate(HEROES):
        hx = M + i * (col_w + 12)
        d.rectangle([hx, y, hx + col_w, y + 92], outline=LIGHT_LINE)
        hero_draw[i](d, hx + 1, y + 1, col_w - 2, 90)
        tag = f"{num}  {place}"
        tag_w = d.textlength(tag, font=sans_b) + 12
        d.rectangle([hx, y + 92 - 18, hx + tag_w, y + 92], fill=RED)
        d.text((hx + 6, y + 92 - 15), tag, font=sans_b, fill=(255, 255, 255))
        _od = "ORIGINAL DRAWING"
        d.text((hx + col_w - 4 - d.textlength(_od, font=sans_xs), y + 92 - 15),
               _od, font=sans_xs, fill=(255, 255, 255))
        ty = y + 98
        nlines, _ = draw_wrapped(d, hx, ty, head, f["serif_b"], col_w, leading=18, max_lines=2)
        ty += nlines * 18 + 2
        nlines, _ = draw_wrapped(d, hx, ty, dek, f["serif_sm"], col_w, leading=12, max_lines=2)
        ty += nlines * 12 + 2
        d.text((hx, ty), f"({src})", font=sans_xs, fill=SLATE)
    y = hero_top + 171

    # ---- markets strip
    d.rectangle([M, y, W - M, y + 28], fill=NAVY)
    d.text((M + 8, y + 8), "MARKETS AT THE CLOSE — FRIDAY",
           font=sans_b, fill=(255, 255, 255))
    mx = M + 218
    cell_w = (W - M - mx - 8) // len(MARKETS)
    for name, val in MARKETS:
        col = GREEN if val.startswith("+") else (255, 120, 100)
        txt = f"{name} {val}"
        check_fit(d, txt, sans_b, cell_w - 4, f"market {name}")
        d.text((mx + 4, y + 8), txt, font=sans_b, fill=col)
        mx += cell_w
    y += 32

    # ---- timeline strip
    d.text((M, y), "THE DAY AS IT HAPPENED", font=sans_b, fill=RED)
    d.line([M + 172, y + 6, W - M, y + 6], fill=LIGHT_LINE, width=1)
    y += 15
    tw_cell = CW // len(TIMELINE)
    for i, (t, place, ev) in enumerate(TIMELINE):
        tx = M + i * tw_cell
        d.ellipse([tx, y + 2, tx + 7, y + 9], fill=RED)
        d.text((tx + 11, y), f"{t}  {place}", font=sans_b, fill=INK)
        draw_wrapped(d, tx + 11, y + 13, ev, sans_xs, tw_cell - 16, fill=SLATE,
                     leading=10, max_lines=2)
    y += 34

    # ---- features: 12 tiles, 4 x 3
    tile_w = (CW - 3 * 8) // 4
    tile_h = 64
    for r in range(3):
        for c in range(4):
            num, region, place, tag, head, dek, src, key = FEATURES[r * 4 + c]
            tx = M + c * (tile_w + 8)
            ty = y + r * (tile_h + 5)
            d.rectangle([tx, ty, tx + tile_w, ty + tile_h], fill=PANEL, outline=LIGHT_LINE)
            d.rectangle([tx, ty, tx + 3, ty + tile_h], fill=REGION_COLORS[region])
            pictogram(d, tx + 8, ty + 4, 52, tile_h - 8, key)
            vx = tx + 66
            vw = tile_w - 66 - 6
            d.text((vx, ty + 3), f"{num}  {tag}", font=F("NotoSans-Bold.ttf", 9),
                   fill=REGION_COLORS[region])
            nlines, _ = draw_wrapped(d, vx, ty + 14, head, F("NotoSerif-Bold.ttf", 12),
                                     vw, leading=12, max_lines=2)
            dy = ty + 14 + nlines * 12 + 1
            draw_wrapped(d, vx, dy, dek + f" ({src})", F("NotoSerif-Regular.ttf", 10),
                         vw, leading=11, max_lines=2)
    y += 3 * tile_h + 2 * 5 + 4

    # ---- map row
    map_x, map_y, map_w, map_h = M, y, 620, 130
    d.text((map_x, map_y), "WHERE IT HAPPENED", font=sans_b, fill=RED)
    d.text((map_x + 150, map_y), "— pins show stories 1–15 · stylised map, not to scale",
           font=sans_xs, fill=SLATE)
    my = map_y + 16
    d.rectangle([map_x, my, map_x + map_w, my + map_h - 16], fill=(233, 240, 244),
                outline=LIGHT_LINE)
    lon0, lon1, lat0, lat1 = -180, 180, 78, -42

    def proj(lon, lat):
        px = map_x + (lon - lon0) / (lon1 - lon0) * map_w
        py = my + (lat0 - lat) / (lat0 - lat1) * (map_h - 16)
        return px, py

    for pts in CONTINENTS.values():
        d.polygon([proj(lo, la) for lo, la in pts], fill=(214, 196, 158),
                  outline=(160, 140, 110))
    for num, (lon, lat, dx, dy) in PINS.items():
        px, py = proj(lon, lat)
        qx, qy = px + dx, py + dy
        if dx or dy:
            d.line([px, py, qx, qy], fill=RED, width=1)
        d.ellipse([qx - 7, qy - 7, qx + 7, qy + 7], fill=RED, outline=(255, 255, 255))
        tw = d.textlength(str(num), font=F("NotoSans-Bold.ttf", 8))
        d.text((qx - tw / 2, qy - 5), str(num), font=F("NotoSans-Bold.ttf", 8),
               fill=(255, 255, 255))
    # right column: quote + date check
    rx = map_x + map_w + 12
    rw = W - M - rx
    qy = map_y
    d.rectangle([rx, qy, rx + rw, qy + 56], fill=PANEL, outline=LIGHT_LINE)
    d.rectangle([rx, qy, rx + 3, qy + 56], fill=RED)
    d.text((rx + 10, qy + 5), "QUOTE OF THE DAY", font=sans_b, fill=RED)
    d.text((rx + 10, qy + 19), "\u201cPutin is a killer.\u201d",
           font=F("NotoSerif-Bold.ttf", 15), fill=INK)
    d.text((rx + 10, qy + 40),
           "— Volodymyr Zelenskyy, replying to the Shenzhen declaration",
           font=sans_xs, fill=SLATE)
    dy = qy + 62
    d.rectangle([rx, dy, rx + rw, dy + 56], fill=(255, 245, 240), outline=RED)
    d.text((rx + 10, dy + 5), "DATE CHECK — LEFT OUT ON PURPOSE", font=sans_b, fill=RED)
    for i, line in enumerate([
            "ICJ's Myanmar verdict — delivered Thu 19 Nov.",
            "Anthropic's Nasdaq debut — Thu 19 Nov.",
            "The Shenzhen declaration — signed Thu 19 Nov.",
            "GTA VI's launch — Thu 19 Nov."]):
        d.text((rx + 10, dy + 19 + i * 10), "·  " + line, font=sans_xs, fill=INK)
    y = my + map_h + 4

    # ---- also on: 25 more stories, 2 columns
    d.text((M, y), "ALSO ON FRIDAY 20 NOVEMBER — 25 MORE STORIES",
           font=sans_b, fill=RED)
    d.line([M + 330, y + 6, W - M, y + 6], fill=LIGHT_LINE, width=1)
    y += 16
    col2_w = (CW - 20) // 2
    also_font = F("NotoSerif-Regular.ttf", 10)
    also_b = F("NotoSans-Bold.ttf", 10)
    for side in range(2):
        items = ALSO[side * 13:(side + 1) * 13]
        ax = M + side * (col2_w + 20)
        ay = y
        for num, place, text, src in items:
            head = f"{num}  {place} — "
            tw = d.textlength(head, font=also_b)
            check_fit(d, head + text, also_font, col2_w, f"also {num}")
            d.text((ax, ay), head, font=also_b, fill=RED)
            d.text((ax + tw, ay), text, font=also_font, fill=INK)
            sw = d.textlength(f" ({src})", font=sans_xs)
            d.text((ax + col2_w - sw, ay), f" ({src})", font=sans_xs, fill=SLATE)
            ay += 11
    y += 13 * 11 + 4

    # ---- footer
    d.line([M, y, W - M, y], fill=INK, width=1)
    y += 4
    foot = ("Every story here happened, or was first reported, on Friday 20 November 2026. "
            "Counts are officials' figures, as reported.  ·  Sources named beside each story  ·  "
            "All drawings original")
    check_fit(d, foot, sans_xs, CW, "footer")
    d.text((M, y), foot, font=sans_xs, fill=SLATE)
    y += 10

    if TRUNCATED:
        raise SystemExit(f"TEXT TRUNCATED ({len(TRUNCATED)}): {TRUNCATED}")
    if y > H - 8:
        raise SystemExit(f"LAYOUT OVERFLOW: content ends at y={y}")
    print(f"layout ok, content ends y={y}")
    return img


def main():
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img = build()
    img.save(out, "PNG")
    h = hashlib.md5(open(out, "rb").read()).hexdigest()
    print(f"wrote {out}  {os.path.getsize(out)} bytes  md5={h}")


if __name__ == "__main__":
    main()
