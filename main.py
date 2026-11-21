#!/usr/bin/env python3
"""The World in One Day - Friday 20 November 2026.

Deterministic single-image newspaper: 58 verified stories, 10 regions.
Python standard library + Pillow only. All artwork is drawn with PIL;
no photographs or downloaded images are used. Running this file twice
produces a byte-identical entry.png (1024x1024, RGB).

Sources for every story are named beside the story. Every story
happened, or was first reported, on Friday 20 November 2026; items
from other dates are listed in the DATE CHECK box, not as stories.
"""
import hashlib
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = "entry.png"

PAPER = (247, 241, 227)
INK = (17, 17, 17)
RED = (178, 34, 34)
DARKRED = (139, 0, 0)
NAVY = (16, 32, 64)
BLUE = (31, 78, 150)
TEAL = (0, 110, 110)
GREY = (90, 86, 78)
LIGHT = (232, 224, 205)
GOLD = (201, 162, 39)
GREEN = (34, 110, 60)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def F(path, size):
    return ImageFont.truetype(path, size)


def wrap(d, text, fnt, maxw):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=fnt) <= maxw:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def para(d, x, y, text, fnt, maxw, max_lines, fill=INK, lh=None):
    """Draw wrapped text, truncating with an ellipsis. Returns bottom y."""
    if lh is None:
        lh = fnt.size + 3
    lines = wrap(d, text, fnt, maxw)[:max_lines]
    if len(wrap(d, text, fnt, maxw)) > max_lines and lines:
        last = lines[-1]
        while last and d.textlength(last + " ...", font=fnt) > maxw:
            last = last[:-1].strip()
        lines[-1] = last + " ..."
    for ln in lines:
        d.text((x, y), ln, font=fnt, fill=fill)
        y += lh
    return y


def trunc(d, text, fnt, maxw):
    while text and d.textlength(text, font=fnt) > maxw:
        text = text[:-1].rstrip()
    return text


# ---------------------------------------------------------------- stories
# (number, region, place, kicker, headline, body, source)
HERO = [
    (1, "Europe", "KYIV, UKRAINE",
     "WAR",
     "Russian missiles hit three Kyiv bridges",
     "An overnight barrage of 110+ missiles and 400+ drones kills at least "
     "nine across Ukraine and cuts power and water in the capital.",
     "BBC, Kyiv Independent"),
    (2, "South Asia", "ODISHA, INDIA",
     "CYCLONE",
     "Cyclone Akvan comes ashore in eastern India",
     "Landfall near Gopalpur from about 02:00 UTC, after 300,000+ people "
     "were moved to shelters. No deaths reported.",
     "IMD, Deccan Herald"),
    (3, "East Asia", "TAIPEI - SEOUL - TOKYO",
     "MARKETS",
     "AI sell-off sinks Asia's stock markets",
     "Taipei falls 6.2% to end its worst week since 1991. Seoul loses 5.2% "
     "and Tokyo 5.1% as chipmakers lead the slide.",
     "CNBC, Al Jazeera"),
]

MINI = [
    (4, "Europe", "BRUSSELS", "DIPLOMACY",
     "UK and EU seal a \u201creset\u201d deal",
     "Food trade, 100,000 youth visas a year and a carbon-market link from 2028.",
     "RTE"),
    (5, "Global", "ANTALYA", "CLIMATE",
     "COP31 reaches its last day with no deal",
     "The draft text leaves out fossil fuels. The EU calls it unacceptable.",
     "Anadolu, RTE"),
    (6, "Europe", "E. POLAND", "SECURITY",
     "Russian missile lands in Poland",
     "A Kh-101 cruise missile comes down near Nowy Lipowiec. No one is hurt.",
     "Reuters"),
    (7, "Middle East", "CENTRAL IRAQ", "SECURITY",
     "Iraqi army enters a militia stronghold",
     "Troops deploy to Jurf al-Sakhar and set up a joint command.",
     "Reuters"),
    (8, "Europe", "ITALY", "LABOUR",
     "General strike over Italy's budget",
     "Workers and students march in cities across the country.",
     "Reuters"),
    (9, "East Asia", "TOKYO", "ECONOMY",
     "Japan's inflation picks up to 2.3%",
     "Core inflation is 2.2%. A December rate rise stays in view.",
     "Reuters"),
    (10, "East Asia", "SEOUL", "POLITICS",
     "Korea's ruling party to impeach top judge",
     "The move follows an overturned conviction.",
     "Korea Herald"),
    (11, "Africa", "TURKANA, KENYA", "ENERGY",
     "Kenya starts drilling its first oil well",
     "The Amosing well is spudded; first crude is due 1 December.",
     "Business Daily"),
    (12, "Latin America", "SAN SALVADOR", "POLITICS",
     "Bukele files to run for a third term",
     "The vote is on 28 February 2027.",
     "AP"),
    (13, "Oceania", "WELLINGTON", "CRICKET",
     "Phillips hits 118 against India",
     "Nicholls makes 175 not out as New Zealand post 368.",
     "ICC"),
]

# (number, place, one-line story, source) -- stories 14-58
ALSO = [
    (14, "Lviv", "Rail station strike kills two", "BBC"),
    (15, "Senate", "Permitting bill passes 62-33", "OilPrice"),
    (16, "Tokyo", "SoftBank plunges 14.5%", "CNBC"),
    (17, "Wall St", "Nasdaq -5.3%; S&P corrects", "Reuters"),
    (18, "Nvidia", "-14% on SEC probe report", "Reuters"),
    (19, "Anthropic", "Shares fall 9% on day two", "CNN"),
    (20, "Oil", "Brent near $91, -5% on week", "OilPrice"),
    (21, "Hormuz", "Tanker ablaze off Oman", "UKMTO"),
    (22, "Riyadh", "Houthi strike hits Riyadh", "PiQ"),
    (23, "Haiti", "Anti-gang op kills dozens", "NewsPoint"),
    (24, "Trump", "'Tremendous tax' on data centres", "CNN"),
    (25, "Brussels", "EU-UK carbon link, 2028", "OilPrice"),
    (26, "Beijing", "China holds loan rates", "Xinhua"),
    (27, "Estonia", "To shut Russia border 1 Dec", "Reuters"),
    (28, "Berlin", "Pupils strike over army service", "AJ"),
    (29, "London", "UK 'runs cyber attacks abroad'", "Sky"),
    (30, "Seoul", "Kospi ends week 7.9% lower", "Anadolu"),
    (31, "Ganjam", "209 mm rain as Akvan crosses", "PTI"),
    (32, "Lebanon", "Israeli strikes hit south", "Anadolu"),
    (33, "Yemen", "Gunmen fire on cargo ship", "UKMTO"),
    (34, "Abuja", "Court bars Tinubu evidence", "Channels"),
    (35, "Kampala", "Ebola rally ban enforced", "allAfrica"),
    (36, "Malawi", "Fuel crisis: night petrol queues", "AJ"),
    (37, "Africa", "22 states near debt distress", "AfDB"),
    (38, "Las Vegas", "Russell fastest, wet GP", "Autosport"),
    (39, "New York", "Nasdaq futures fall pre-bell", "24/7"),
    (40, "Washington", "Democrats query law firm", "AJ"),
    (41, "Sydney", "Australian shares fall 1.6%", "Reuters"),
    (42, "Antalya", "Panama asks COP31 oil cap", "Anadolu"),
    (43, "Turin", "ATP backs pay past $350m", "Anadolu"),
    (44, "New Delhi", "Pakistani PM visits", "PTI, Dawn"),
    (45, "Argentina", "Country risk jumps to 1,070", "JPM"),
    (46, "Health", "Cancer pill: 60.7% respond", "Trial"),
    (47, "Kryvyi Rih", "Strike kills 2 and injures 42", "PiQ"),
    (48, "Gaza", "Strikes kill six despite truce", "Rescuers"),
    (49, "Sudan", "Army claims West Kordofan gains", "PiQ"),
    (50, "Russia", "Fuel rationing widens", "OilPrice"),
    (51, "Mexico", "Sheinbaum leads Revolution parade", "AP"),
    (52, "Film", "Hunger Games prequel $21.25m", "Studio"),
    (53, "Florida", "Floods spread after 17 in rain", "NWS"),
    (54, "Dhaka", "New arson attacks, 124 held", "Police"),
    (55, "Myanmar", "Xi hails 'turnaround' in ties", "Xinhua"),
    (56, "US Fed", "Lisa Cook calls for rate hikes", "Fed"),
    (57, "Europe", "Shares: worst week in a year", "Reuters"),
    (58, "Gold", "Worst week in eight months", "Token Times"),
]

TIMELINE = [
    ("00:00", "Kyiv bridges hit"),
    ("02:00", "Akvan makes landfall"),
    ("05:40", "Kh-101 falls in Poland"),
    ("09:00", "Turkana drilling starts"),
    ("15:00", "COP31 runs past close"),
    ("16:00", "US close: S&P -3.7%"),
    ("21:00", "Nasdaq ends -5.3%"),
]

NUMBERS = [
    ("3", "bridges over the Dnipro damaged in Kyiv"),
    ("300,000+", "people moved to shelters before Akvan"),
    ("111 + 404", "missiles and drones fired at Ukraine"),
    ("100,000", "youth visas a year in the UK-EU deal"),
    ("-6.2%", "Taipei index, Friday's close"),
    ("-14%", "Nvidia, on the SEC probe report"),
]

MARKETS = ("MARKETS AT CLOSE  \u2014  Taipei -6.2%  \u00b7  Seoul -5.2%  \u00b7  "
           "Tokyo -5.1%  \u00b7  Nasdaq -5.3%  \u00b7  S&P 500 -3.7%  \u00b7  Dow -1.9%  "
           "\u00b7  Brent ~$91  \u00b7  Gold: worst week in 8 months")

QUOTE = ("\u201cIt\u2019s a meltdown.\u201d  \u2014  Arun Sundaram, CFRA Research, "
         "on Friday\u2019s AI sell-off (CNN)")

DATE_CHECK = ("DATE CHECK \u2014 Left out on purpose. Anthropic\u2019s $107bn IPO debut was "
              "Thursday 19 Nov (only its day-two slide is Friday\u2019s news). The EU\u2019s "
              "big-tech tax plan is dated Saturday 21 Nov. COP31\u2019s next draft is due "
              "Saturday, and the ATP Finals final is Sunday 22 Nov. BepiColombo\u2019s "
              "Mercury orbit entry has not happened yet.")

REGIONS = ["Europe", "East Asia", "South Asia", "Southeast Asia",
           "Middle East", "Africa", "North America", "Latin America",
           "Oceania", "Global"]

# ---------------------------------------------------------------- drawings
def burst(d, cx, cy, r, col):
    import math
    pts = []
    for i in range(16):
        a = math.pi * i / 8
        rr = r if i % 2 == 0 else r * 0.38
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(pts, fill=col)


def hero_kyiv(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=NAVY)
    for sx, sy, sr in [(20, 18, 2), (70, 30, 1), (120, 12, 2), (180, 26, 1),
                       (240, 14, 2), (290, 34, 1), (150, 40, 1), (40, 44, 1)]:
        d.ellipse([x + sx - sr, y + sy - sr, x + sx + sr, y + sy + sr], fill=(255, 255, 200))
    # skyline
    for bx, bw, bh in [(0, 34, 34), (40, 26, 48), (72, 30, 30), (108, 24, 44),
                       (138, 36, 28), (180, 26, 50), (212, 30, 32), (248, 28, 46),
                       (282, 40, 30)]:
        d.rectangle([x + bx, y + h - 46 - bh, x + bx + bw, y + h - 46], fill=(8, 16, 38))
        for wy in range(6, bh - 4, 9):
            for wx in range(5, bw - 3, 9):
                if (bx + wx) % 17 < 8:
                    d.rectangle([x + bx + wx, y + h - 46 - bh + wy,
                                 x + bx + wx + 3, y + h - 46 - bh + wy + 3],
                                fill=(255, 214, 90))
    # river
    d.rectangle([x, y + h - 46, x + w, y + h], fill=(13, 48, 92))
    # bridge: deck + 3 arches
    d.rectangle([x, y + h - 58, x + w, y + h - 52], fill=(40, 44, 58))
    for ax in (30, 130, 230):
        d.arc([x + ax, y + h - 58, x + ax + 70, y + h - 20], 180, 360,
              fill=(120, 130, 150), width=3)
        d.line([x + ax + 35, y + h - 58, x + ax + 35, y + h - 40],
               fill=(120, 130, 150), width=2)
    # dashed missile arcs
    for (x0, y0, x1, y1) in [(10, 8, 120, 52), (150, 4, 250, 48), (210, 10, 290, 60)]:
        for t in range(0, 11):
            tt = t / 10
            px = x + x0 + (x1 - x0) * tt
            py = y + y0 + (y1 - y0) * tt - 26 * (1 - (2 * tt - 1) ** 2)
            if t % 2 == 0:
                d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(255, 220, 120))
    burst(d, x + 120, y + h - 56, 13, (255, 170, 40))
    burst(d, x + 250, y + h - 56, 11, (255, 190, 60))
    burst(d, x + 60, y + h - 70, 8, (255, 200, 80))


def hero_cyclone(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(72, 132, 178))
    # land (India coast) top-left
    d.polygon([(x, y), (x + 120, y), (x + 108, y + 52), (x + 66, y + 66),
               (x + 40, y + 96), (x, y + 104)], fill=(214, 196, 150))
    d.polygon([(x + 250, y + h), (x + w, y + h), (x + w, y + 60),
               (x + 268, y + 78)], fill=(196, 178, 138))
    # spiral
    cx, cy = x + 205, y + 78
    for r in (52, 42, 32, 22, 12):
        d.arc([cx - r, cy - r, cx + r, cy + r], 20, 300, fill=(255, 255, 255), width=3)
    d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=(255, 255, 255))
    # landfall track
    for t in range(0, 11):
        tt = t / 10
        px = x + 60 + (cx - 14 - x - 60) * tt
        py = y + 118 + (cy - y - 118) * tt
        if t % 2 == 0:
            d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(255, 60, 60))
    d.ellipse([cx - 20, cy - 6, cx - 8, cy + 6], fill=RED)
    # rain
    for rx in range(20, w, 26):
        d.line([x + rx, y + 14, x + rx - 8, y + 34], fill=(220, 235, 245), width=2)
    d.text((x + 8, y + h - 18), "BAY OF BENGAL", font=F(SANS_B, 9), fill=(255, 255, 255))


def hero_market(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(12, 20, 36))
    for gy in range(18, h, 22):
        d.line([x + 8, y + gy, x + w - 8, y + gy], fill=(38, 52, 78), width=1)
    # falling bars
    bars = [62, 56, 58, 46, 40, 30, 34, 22, 14]
    bw = 24
    for i, bh in enumerate(bars):
        bx = x + 14 + i * (bw + 6)
        d.rectangle([bx, y + h - 18 - bh, bx + bw, y + h - 18], fill=(150, 40, 40))
    pts = [(x + 20, y + 26), (x + 70, y + 44), (x + 120, y + 38), (x + 170, y + 62),
           (x + 220, y + 70), (x + 270, y + 92), (x + w - 16, y + h - 26)]
    d.line(pts, fill=(255, 70, 70), width=4)
    d.polygon([(x + w - 16, y + h - 26), (x + w - 30, y + h - 30), (x + w - 22, y + h - 14)],
              fill=(255, 70, 70))
    d.text((x + 14, y + h - 16), "TAIPEI -6.2%   SEOUL -5.2%   TOKYO -5.1%",
           font=F(SANS_B, 10), fill=(255, 120, 120))


def label_banner(d, x, y, w, text, fnt):
    tw = d.textlength(text, font=fnt) + 16
    d.rectangle([x, y, x + min(tw, w), y + 18], fill=RED)
    d.text((x + 8, y + 3), text, font=fnt, fill=(255, 255, 255))


# mini icons, one per story 4-13 (original geometric drawings)
def icon(d, n, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=LIGHT, outline=(190, 180, 160))
    if n == 4:  # UK + EU flags, abstract
        d.rectangle([x, y, x + w // 2, y + h], fill=BLUE)
        for sx, sy in [(14, 12), (34, 10), (52, 20), (20, 32), (44, 34)]:
            d.ellipse([x + sx - 2, y + sy - 2, x + sx + 2, y + sy + 2], fill=GOLD)
        d.rectangle([x + w // 2, y, x + w, y + h], fill=(200, 30, 40))
        d.rectangle([x + w // 2 + 22, y, x + w // 2 + 34, y + h], fill=(255, 255, 255))
        d.rectangle([x + w // 2, y + 18, x + w, y + 30], fill=(255, 255, 255))
    elif n == 5:  # globe + clock
        d.ellipse([x + 14, y + 6, x + 62, y + 46], fill=(70, 140, 200))
        d.polygon([(x + 26, y + 14), (x + 44, y + 12), (x + 48, y + 26), (x + 30, y + 30)],
                  fill=GREEN)
        d.polygon([(x + 40, y + 34), (x + 56, y + 32), (x + 54, y + 42), (x + 42, y + 44)],
                  fill=GREEN)
        d.ellipse([x + w - 42, y + 6, x + w - 10, y + 38], fill=(255, 255, 255),
                  outline=INK)
        d.line([x + w - 26, y + 22, x + w - 26, y + 12], fill=INK, width=2)
        d.line([x + w - 26, y + 22, x + w - 18, y + 26], fill=INK, width=2)
    elif n == 6:  # missile over field
        d.rectangle([x, y + 30, x + w, y + h], fill=(120, 170, 90))
        d.polygon([(x + 20, y + 18), (x + 60, y + 10), (x + 66, y + 18),
                   (x + 60, y + 26), (x + 20, y + 26)], fill=(90, 90, 100))
        d.polygon([(x + 60, y + 10), (x + 74, y + 18), (x + 60, y + 26)], fill=RED)
        for t in range(5):
            d.ellipse([x + 84 + t * 12, y + 16, x + 88 + t * 12, y + 20], fill=RED)
    elif n == 7:  # convoy in desert
        d.rectangle([x, y + 28, x + w, y + h], fill=(222, 196, 140))
        for tx in (12, 48, 84):
            d.rectangle([x + tx, y + 14, x + tx + 30, y + 30], fill=(70, 90, 50))
            d.ellipse([x + tx + 6, y + 30, x + tx + 12, y + 36], fill=INK)
            d.ellipse([x + tx + 20, y + 30, x + tx + 26, y + 36], fill=INK)
        d.rectangle([x + 130, y + 8, x + 134, y + 30], fill=(120, 80, 40))
        d.ellipse([x + 122, y + 2, x + 142, y + 12], fill=GREEN)
    elif n == 8:  # crowd + placards
        for cx in range(10, w - 8, 22):
            d.ellipse([x + cx, y + 22, x + cx + 14, y + 36], fill=INK)
            d.rectangle([x + cx + 1, y + 36, x + cx + 13, y + h - 4], fill=(60, 60, 70))
        d.rectangle([x + 30, y + 4, x + 78, y + 18], fill=(255, 255, 255), outline=RED)
        d.text((x + 34, y + 6), "SCIOPERO", font=F(SANS_B, 8), fill=RED)
    elif n == 9:  # rising bars + red sun
        d.ellipse([x + w - 34, y + 4, x + w - 6, y + 32], fill=(200, 30, 40))
        for i, bh in enumerate([10, 18, 26, 34]):
            bx = x + 12 + i * 18
            d.rectangle([bx, y + h - 8 - bh, bx + 12, y + h - 8], fill=BLUE)
    elif n == 10:  # courthouse
        d.polygon([(x + 12, y + 8), (x + w // 2, y + 22), (x + w - 12, y + 8)],
                  fill=(120, 100, 70))
        for cx in range(22, w - 16, 24):
            d.rectangle([x + cx, y + 24, x + cx + 8, y + h - 6], fill=(200, 190, 170),
                        outline=(120, 110, 90))
        d.rectangle([x + 8, y + h - 8, x + w - 8, y + h - 4], fill=(120, 100, 70))
    elif n == 11:  # oil derrick at sunset
        d.ellipse([x + w - 40, y + 4, x + w - 8, y + 36], fill=(255, 170, 40))
        d.polygon([(x + 20, y + h - 4), (x + 44, y + 6), (x + 68, y + h - 4)],
                  fill=(40, 40, 48))
        d.rectangle([x + 40, y + 14, x + 48, y + h - 4], fill=(40, 40, 48))
    elif n == 12:  # ballot box
        d.rectangle([x + 20, y + 16, x + 76, y + h - 6], fill=(240, 235, 220),
                    outline=INK)
        d.rectangle([x + 36, y + 8, x + 60, y + 16], fill=(255, 255, 255), outline=INK)
        d.line([(x + 78, y + 8), (x + 90, y + 20), (x + 106, y + 4)], fill=RED, width=4)
        d.text((x + 30, y + 26), "VOTA", font=F(SANS_B, 10), fill=INK)
    elif n == 13:  # cricket
        d.rectangle([x, y, x + w, y + h], fill=(90, 160, 80))
        d.rectangle([x + 20, y + 8, x + 118, y + 30], fill=(240, 230, 200))
        d.text((x + 26, y + 10), "118", font=F(SANS_B, 18), fill=INK)
        d.line([(x + 130, y + 34), (x + 150, y + 14)], fill=(190, 140, 60), width=5)
        d.ellipse([x + 152, y + 10, x + 160, y + 18], fill=RED)


# simplified world map with numbered pins for stories 1-13
MAP_PINS = [(1, 172, 44), (2, 244, 98), (3, 290, 92), (4, 146, 54), (5, 190, 60),
            (6, 160, 30), (7, 208, 80), (8, 156, 70), (9, 304, 64), (10, 282, 76),
            (11, 196, 104), (12, 52, 92), (13, 306, 128)]


def world_map(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(214, 228, 238), outline=(150, 160, 170))
    land = (222, 205, 165)
    # North America, South America, Europe, Africa, Asia, Australia (abstract)
    d.polygon([(x + 8, y + 34), (x + 70, y + 18), (x + 108, y + 30), (x + 96, y + 58),
               (x + 60, y + 66), (x + 30, y + 56), (x + 10, y + 46)], fill=land)
    d.polygon([(x + 62, y + 76), (x + 92, y + 72), (x + 98, y + 96), (x + 80, y + 122),
               (x + 66, y + 100)], fill=land)
    d.polygon([(x + 148, y + 26), (x + 178, y + 20), (x + 190, y + 38), (x + 168, y + 52),
               (x + 150, y + 44)], fill=land)
    d.polygon([(x + 158, y + 58), (x + 192, y + 56), (x + 204, y + 78), (x + 190, y + 108),
               (x + 170, y + 96), (x + 158, y + 76)], fill=land)
    d.polygon([(x + 192, y + 22), (x + 260, y + 14), (x + 306, y + 30), (x + 300, y + 66),
               (x + 262, y + 84), (x + 226, y + 70), (x + 196, y + 48)], fill=land)
    d.polygon([(x + 268, y + 112), (x + 296, y + 110), (x + 300, y + 126),
               (x + 272, y + 130)], fill=land)
    d.text((x + 8, y + h - 14), "ATLANTIC", font=F(SANS, 8), fill=(90, 110, 130))
    d.text((x + w - 78, y + 12), "PACIFIC", font=F(SANS, 8), fill=(90, 110, 130))
    fnt = F(SANS_B, 9)
    for num, px, py in MAP_PINS:
        d.ellipse([x + px - 8, y + py - 8, x + px + 8, y + py + 8],
                  fill=RED, outline=(255, 255, 255), width=1)
        t = str(num)
        tw = d.textlength(t, font=fnt)
        d.text((x + px - tw / 2, y + py - 6), t, font=fnt, fill=(255, 255, 255))

# ---------------------------------------------------------------- layout
def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    M = 16
    CW = W - 2 * M
    y = 10

    # kicker
    d.text((M, y), "THE WORLD IN ONE DAY", font=F(SANS_B, 11), fill=RED)
    right = "58 STORIES  \u00b7  10 REGIONS  \u00b7  EVERY ONE DATED FRIDAY 20 NOVEMBER 2026"
    d.text((W - M - d.textlength(right, font=F(SANS_B, 11)), y), right,
           font=F(SANS_B, 11), fill=INK)
    y += 16
    d.line([M, y, W - M, y], fill=INK, width=2)
    y += 6

    # masthead
    title = "Friday 20 November 2026"
    tf = F(SERIF_B, 48)
    d.text(((W - d.textlength(title, font=tf)) / 2, y), title, font=tf, fill=INK)
    y += 56
    sub = ("Russian missiles hit Kyiv\u2019s bridges  \u00b7  Cyclone Akvan strikes India  "
           "\u00b7  An AI sell-off sinks world markets  \u00b7  UK and EU seal a deal")
    sf = F(SERIF, 15)
    d.text(((W - d.textlength(sub, font=sf)) / 2, y), sub, font=sf, fill=INK)
    y += 20
    d.line([M, y, W - M, y], fill=INK, width=1)
    y += 6

    # UTC timeline
    d.text((M, y), "THE DAY IN UTC", font=F(SANS_B, 10), fill=RED)
    y += 14
    tl_y = y + 4
    d.line([M + 130, tl_y, W - M - 30, tl_y], fill=(150, 140, 120), width=2)
    seg = (W - M - 30 - (M + 130)) / (len(TIMELINE) - 1)
    for i, (t, lab) in enumerate(TIMELINE):
        cx = M + 130 + i * seg
        d.ellipse([cx - 5, tl_y - 5, cx + 5, tl_y + 5], fill=RED,
                  outline=(255, 255, 255), width=1)
        d.text((cx - d.textlength(t, font=F(SANS_B, 10)) / 2, y - 12), t,
               font=F(SANS_B, 10), fill=INK)
        lf = F(SANS, 8)
        lw = d.textlength(lab, font=lf)
        lx = max(M, min(cx - lw / 2, W - M - lw))
        d.text((lx, tl_y + 8), lab, font=lf, fill=INK)
    y += 30
    d.line([M, y, W - M, y], fill=INK, width=1)
    y += 6

    # by the numbers
    bw = CW / 6
    for i, (num, lab) in enumerate(NUMBERS):
        x0 = M + i * bw
        if i:
            d.line([x0, y, x0, y + 50], fill=(190, 180, 160), width=1)
        nf = F(SANS_B, 21)
        d.text((x0 + 8, y), num, font=nf, fill=INK)
        para(d, x0 + 8, y + 26, lab, F(SANS, 9), bw - 14, 2, lh=11)
    y += 50
    d.line([M, y, W - M, y], fill=INK, width=1)
    y += 6

    # hero row (3 columns)
    colw = int((CW - 24) / 3)
    hero_top = y
    hero_draw = [hero_kyiv, hero_cyclone, hero_market]
    hero_lbl = ["KYIV \u2014 3 BRIDGES HIT", "CYCLONE AKVAN \u2014 LANDFALL 02:00 UTC",
                "AI SELL-OFF \u2014 ASIA, FRIDAY CLOSE"]
    for i, st in enumerate(HERO):
        x0 = M + i * (colw + 12)
        hero_draw[i](d, x0, y, colw, 116)
        label_banner(d, x0, y + 6, colw, hero_lbl[i], F(SANS_B, 10))
        ty = y + 122
        d.text((x0, ty), f"{st[0]}  {st[2]}  \u00b7  {st[3]}", font=F(SANS_B, 9), fill=RED)
        ty += 13
        ty = para(d, x0, ty, st[4], F(SERIF_B, 18), colw, 2, lh=21)
        ty = para(d, x0, ty + 2, st[5], F(SANS, 11), colw, 3, lh=13)
        d.text((x0, ty + 2), "Source: " + st[6], font=F(SANS, 8), fill=GREY)
    y = hero_top + 234
    d.line([M, y, W - M, y], fill=INK, width=1)
    y += 6

    # mini rows (stories 4-8, then 9-13)
    mini_w = int((CW - 40) / 5)
    for row in (MINI[:5], MINI[5:]):
        row_top = y
        for i, st in enumerate(row):
            x0 = M + i * (mini_w + 10)
            icon(d, st[0], x0, y, mini_w, 50)
            ty = y + 54
            d.text((x0, ty), f"{st[0]}  {st[2]}  \u00b7  {st[3]}", font=F(SANS_B, 8),
                   fill=RED)
            ty += 11
            ty = para(d, x0, ty, st[4], F(SERIF_B, 12), mini_w, 2, lh=14)
            ty = para(d, x0, ty + 1, st[5], F(SANS, 9), mini_w, 2, lh=11)
            d.text((x0, ty + 1), "Source: " + st[6], font=F(SANS, 7), fill=GREY)
        y = row_top + 126
        d.line([M, y, W - M, y], fill=(190, 180, 160), width=1)
        y += 5

    # markets strip
    d.rectangle([M, y, W - M, y + 30], fill=NAVY)
    mf = F(SANS_B, 10)
    txt = trunc(d, MARKETS, mf, CW - 16)
    d.text((M + 8, y + 8), txt, font=mf, fill=(255, 255, 255))
    y += 32

    # bottom: map + quote (left) | also-list (right)
    map_w = 300
    d.text((M, y), "WHERE IT HAPPENED \u2014 PINS 1\u201313", font=F(SANS_B, 10), fill=RED)
    y += 14
    bot_top = y
    world_map(d, M, y, map_w, 138)
    d.text((M, y + 142), "Each pin is the story with that number on this page.",
           font=F(SANS, 8), fill=GREY)
    qy = y + 156
    d.rectangle([M, qy, M + map_w, qy + 36], fill=(255, 255, 255),
                outline=(190, 180, 160))
    d.text((M + 6, qy + 3), "QUOTE OF THE DAY", font=F(SANS_B, 8), fill=RED)
    para(d, M + 6, qy + 13, QUOTE, F(SERIF, 10), map_w - 12, 2, lh=11)

    ax = M + map_w + 14
    aw = W - M - ax
    d.text((ax, bot_top - 14), "ALSO ON FRIDAY 20 NOVEMBER \u2014 45 MORE STORIES",
           font=F(SANS_B, 10), fill=RED)
    colw2 = int((aw - 20) / 3)
    lf = F(SANS, 8)
    for ci in range(3):
        cx = ax + ci * (colw2 + 10)
        for ri in range(15):
            item = ALSO[ci * 15 + ri]
            s = f"{item[0]} {item[1]}: {item[2]} ({item[3]})"
            s = trunc(d, s, lf, colw2)
            d.text((cx, bot_top + ri * 12), s, font=lf, fill=INK)
    y = bot_top + 196

    # date check
    d.rectangle([M, y, W - M, y + 38], outline=RED, width=2)
    d.text((M + 8, y + 4), "DATE CHECK", font=F(SANS_B, 10), fill=RED)
    para(d, M + 92, y + 4, DATE_CHECK, F(SANS, 10), CW - 100, 3, lh=12)
    y += 44

    # footer
    d.text((M, y), "Every story happened, or was first reported, on Friday 20 November 2026. "
                   "Officials' counts are attributed.",
           font=F(SANS, 8), fill=GREY)
    foot_r = "Sources named beside each story  \u00b7  Original drawings  \u00b7  58 stories, 10 regions"
    d.text((W - M - d.textlength(foot_r, font=F(SANS, 8)), y), foot_r,
           font=F(SANS, 8), fill=GREY)
    assert y + 12 <= H, f"layout overflow: y={y}"
    img.save(OUT, "PNG")
    return y


if __name__ == "__main__":
    end_y = build()
    n = len(HERO) + len(MINI) + len(ALSO)
    print(f"stories={n} regions={len(REGIONS)} end_y={end_y}")
    print("md5=" + hashlib.md5(open(OUT, "rb").read()).hexdigest())
