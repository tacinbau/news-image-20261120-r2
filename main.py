#!/usr/bin/env python3
"""
THE WORLD IN ONE DAY — Friday 20 November 2026.
One 1024x1024 front page: 78 stories, 15 regions, all dated Fri 20 Nov 2026.
Drawn entirely in code with PIL (stdlib + Pillow). No photos, no external
assets, no network, no clock, no randomness without a fixed seed:
two runs produce a byte-identical PNG.

Sources (wires of 20 Nov 2026, checked 21 Nov 2026):
Reuters / AP / Investopedia / IANS / UNFCCC / Open Chronicle / Zacks.
DATE CHECK: items dated 19 Nov (ICJ Myanmar ruling, Shenzhen summit,
Anthropic day-1 debut, Dutch embassy drone hit in Kyiv) and any 21/22 Nov
items were EXCLUDED. Only events/updates dated Fri 20 Nov 2026 appear.
"""
import hashlib
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = "entry.png"

FONT_DIR = "/usr/share/fonts/truetype/dejavu/"
def font(name, size):
    return ImageFont.truetype(FONT_DIR + name, size)

F_SERIF_B = lambda s: font("DejaVuSerif-Bold.ttf", s)
F_SANS = lambda s: font("DejaVuSans.ttf", s)
F_SANS_B = lambda s: font("DejaVuSans-Bold.ttf", s)

# ---------- palette ----------
PAPER   = (247, 243, 234)
INK     = (20, 20, 20)
MUTED   = (90, 88, 80)
RED     = (180, 35, 24)
NAVY    = (18, 44, 72)
NAVY_LT = (30, 64, 100)
GOLD    = (176, 132, 40)
LINE    = (200, 192, 172)
ALTROW  = (238, 232, 218)
OCEAN   = (214, 229, 238)
LAND    = (178, 196, 160)
LAND_LN = (120, 140, 108)
WHITE   = (255, 255, 255)
GREEN   = (30, 120, 60)

# ---------- data: (region, code, colour, headline) ----------
# 78 stories, 15 regions. Every headline is a Fri 20 Nov 2026 fact.
STORIES = [
    # EUROPE (9)
    ("Europe", "EU", (90, 60, 140), "Merz: no new Yalta — Europe must be at the table"),
    ("Europe", "EU", (90, 60, 140), "EU–UK hold 2nd summit in Brussels; youth mobility eyed"),
    ("Europe", "EU", (90, 60, 140), "Denmark OKs Greenland–US Arctic deal; Pituffik base"),
    ("Europe", "EU", (90, 60, 140), "Frankfurt: 2 Dutch men held over alleged bar bomb plot"),
    ("Europe", "EU", (90, 60, 140), "London: 4 convicted in Joanne Young drugging case"),
    ("Europe", "EU", (90, 60, 140), "Spain: Sanchez admits mistakes as election race tightens"),
    ("Europe", "EU", (90, 60, 140), "Cost-of-living protests planned across Europe"),
    ("Europe", "EU", (90, 60, 140), "EU Commission breached via AI tool; payroll hit"),
    ("Europe", "EU", (90, 60, 140), "Brussels shelters strain as housing crisis bites"),
    # UKRAINE WAR (5)
    ("Ukraine War", "UA", (180, 35, 24), "Kyiv: ~117-missile barrage hits 3 Dnipro bridges; 3 dead"),
    ("Ukraine War", "UA", (180, 35, 24), "Poland probes missile, drone incursion in border airspace"),
    ("Ukraine War", "UA", (180, 35, 24), "Ukraine drones hit Dorogobuzh chemical plant, Smolensk"),
    ("Ukraine War", "UA", (180, 35, 24), "Kramatorsk: bomb hits bus — 30 killed, 18 wounded"),
    ("Ukraine War", "UA", (180, 35, 24), "Dutch Destinus staff flew combat drones, probe finds"),
    # ASIA-PACIFIC (6)
    ("Asia-Pacific", "APAC", (20, 110, 130), "Russian Tu-95 bombers enter Taiwan ADIZ during APEC"),
    ("Asia-Pacific", "APAC", (20, 110, 130), "Taiwan flags ~2,700 China-linked accounts on Meta"),
    ("Asia-Pacific", "APAC", (20, 110, 130), "Japan core CPI 2.2% in Oct; rate debate heats up"),
    ("Asia-Pacific", "APAC", (20, 110, 130), "China holds lending rates for 18th straight month"),
    ("Asia-Pacific", "APAC", (20, 110, 130), "Japan–India expand defence industry cooperation"),
    ("Asia-Pacific", "APAC", (20, 110, 130), "Xi hails 'significant shift' in China–Australia ties"),
    # SOUTH ASIA (6)
    ("South Asia", "S-ASIA", (200, 110, 20), "Manipur toxic liquor kills 11+; 180+ fall ill"),
    ("South Asia", "S-ASIA", (200, 110, 20), "Cyclone Akvan makes landfall on India's east coast"),
    ("South Asia", "S-ASIA", (200, 110, 20), "India's US Treasury holdings rise to $228.2bn"),
    ("South Asia", "S-ASIA", (200, 110, 20), "IEA: India drives energy growth amid Hormuz crisis"),
    ("South Asia", "S-ASIA", (200, 110, 20), "Modi to open first SCO Civilisational Dialogue in Delhi"),
    ("South Asia", "S-ASIA", (200, 110, 20), "India Army chief meets Czech defence industry"),
    # MIDDLE EAST & GULF (6)
    ("Middle East & Gulf", "MIDEAST", (150, 90, 20), "Hormuz: US blockade holds; Iran threatens tankers"),
    ("Middle East & Gulf", "MIDEAST", (150, 90, 20), "Tanker hit by drone off Shinas, Oman"),
    ("Middle East & Gulf", "MIDEAST", (150, 90, 20), "Iraq deal with Kataib Hezbollah over Jurf al-Sakhar"),
    ("Middle East & Gulf", "MIDEAST", (150, 90, 20), "Saudi intercepts more Houthi missiles and drones"),
    ("Middle East & Gulf", "MIDEAST", (150, 90, 20), "Pentagon puts US Iran campaign cost at ~$48.3bn"),
    ("Middle East & Gulf", "MIDEAST", (150, 90, 20), "Gaza: 22,000+ children killed, health officials say"),
    # AFRICA (4)
    ("Africa", "AFRICA", (40, 130, 70), "Somalia orders UAE ambassador out within 72 hours"),
    ("Africa", "AFRICA", (40, 130, 70), "Sudan war grinds on; armed-group loyalties shift"),
    ("Africa", "AFRICA", (40, 130, 70), "Africa presses COP31 for faster climate finance"),
    ("Africa", "AFRICA", (40, 130, 70), "Nigeria moves to end jail for attempted suicide"),
    # NORTH AMERICA (8)
    ("North America", "N-AMER", (30, 64, 100), "Cairncross quits as US national cyber director"),
    ("North America", "N-AMER", (30, 64, 100), "Microsoft 365 down 9+ hrs; Outlook, Teams hit"),
    ("North America", "N-AMER", (30, 64, 100), "California subpoenas Nvidia over China chip risks"),
    ("North America", "N-AMER", (30, 64, 100), "Visa, Mastercard, JPMorgan disclose vendor breaches"),
    ("North America", "N-AMER", (30, 64, 100), "Trump: 'tremendous tax' on offshore data centres"),
    ("North America", "N-AMER", (30, 64, 100), "ICE, CBP handed $41.7bn a year in border contracts"),
    ("North America", "N-AMER", (30, 64, 100), "Democrats move to end old deportation orders"),
    ("North America", "N-AMER", (30, 64, 100), "ICE paid millions for empty beds, audit finds"),
    # LATIN AMERICA & CARIBBEAN (5)
    ("Latin America & Caribbean", "LATAM", (190, 60, 110), "Haiti police kill 34 suspected gang members"),
    ("Latin America & Caribbean", "LATAM", (190, 60, 110), "Bukele moves toward a third-term bid in El Salvador"),
    ("Latin America & Caribbean", "LATAM", (190, 60, 110), "Lula, Chief Raoni advance Indigenous land protection"),
    ("Latin America & Caribbean", "LATAM", (190, 60, 110), "Colombia protests flare over tax proposals"),
    ("Latin America & Caribbean", "LATAM", (190, 60, 110), "US: Chinese chemicals fuel Sinaloa cartel"),
    # OCEANIA (3)
    ("Oceania", "OCEANIA", (0, 130, 150), "Pacific islands press COP31 on drought, seas, water"),
    ("Oceania", "OCEANIA", (0, 130, 150), "Cyclone Xavier, Cat 4, tracked in South Pacific"),
    ("Oceania", "OCEANIA", (0, 130, 150), "Australia–Japan deepen Indo-Pacific security ties"),
    # MARKETS & ECONOMY (9)
    ("Markets & Economy", "MKT", (180, 35, 24), "Nasdaq -5.2% (-1,200 pts); S&P -3.7%; Dow -1.9%"),
    ("Markets & Economy", "MKT", (180, 35, 24), "Worst week since Apr 2025: Dow -8%, Nasdaq -10%"),
    ("Markets & Economy", "MKT", (180, 35, 24), "VIX jumps 26% to near 36 as fear spikes"),
    ("Markets & Economy", "MKT", (180, 35, 24), "Nvidia -14% to $125.53; AMD -13%; chips routed"),
    ("Markets & Economy", "MKT", (180, 35, 24), "Anthropic ANT -9% to ~$89 on second day of trade"),
    ("Markets & Economy", "MKT", (180, 35, 24), "Bitcoin ~$59,000, lowest since June"),
    ("Markets & Economy", "MKT", (180, 35, 24), "Gold -4% to $3,540; WTI oil +1.1% to $84.10"),
    ("Markets & Economy", "MKT", (180, 35, 24), "Nikkei -4.5%, Kospi -4.7% as Asia sinks"),
    ("Markets & Economy", "MKT", (180, 35, 24), "Intuit to sell Mailchimp for $3.68bn; shares -10%"),
    # TECH & AI (3)
    ("Tech & AI", "TECH", (90, 60, 140), "ARK buys 706k more Anthropic shares on day two"),
    ("Tech & AI", "TECH", (90, 60, 140), "US senators push AI disclosure bill for listed firms"),
    ("Tech & AI", "TECH", (90, 60, 140), "Google plans to send AI servers into orbit"),
    # CLIMATE & ENERGY (3)
    ("Climate & Energy", "CLIMATE", (40, 130, 70), "COP31 final day in Antalya ends with no deal"),
    ("Climate & Energy", "CLIMATE", (40, 130, 70), "COP31 draft drops fossil fuels, $120bn figure"),
    ("Climate & Energy", "CLIMATE", (40, 130, 70), "France–Panama bloc rejects COP31 draft"),
    # SCIENCE & SPACE (2)
    ("Science & Space", "SPACE", (20, 110, 130), "Voyager 1: radio signal now takes ~1 day each way"),
    ("Science & Space", "SPACE", (20, 110, 130), "SpaceX–China orbital data-centre race warned"),
    # SPORT (6)
    ("Sport", "SPORT", (30, 64, 100), "Al Ahli Jeddah 3–1 Al Nassr in Saudi League"),
    ("Sport", "SPORT", (30, 64, 100), "Bayern held 1–1 by Koln in Bundesliga"),
    ("Sport", "SPORT", (30, 64, 100), "Athletic Bilbao 0–1 Espanyol in LaLiga"),
    ("Sport", "SPORT", (30, 64, 100), "Bengaluru FC 2–0 Mumbai City, top of ISL"),
    ("Sport", "SPORT", (30, 64, 100), "Gokulam Kerala 4–1 Mohammedan, stay top of IFL"),
    ("Sport", "SPORT", (30, 64, 100), "India A thrash Nepal by 306 runs in Rising Stars Cup"),
    # CULTURE & SOCIETY (3)
    ("Culture & Society", "CULTURE", (176, 132, 40), "GTA VI early estimates top $2bn in revenue"),
    ("Culture & Society", "CULTURE", (176, 132, 40), "Cincinnati Zoo mourns Fiona the hippo"),
    ("Culture & Society", "CULTURE", (176, 132, 40), "Mayweather cheque case thrown out in Las Vegas"),
]

# Region order + tally (must sum to len(STORIES))
REGION_ORDER = ["Europe", "Ukraine War", "Asia-Pacific", "South Asia",
                "Middle East & Gulf", "Africa", "North America",
                "Latin America & Caribbean", "Oceania", "Markets & Economy",
                "Tech & AI", "Climate & Energy", "Science & Space", "Sport",
                "Culture & Society"]

# Map pins: (story_no, lat, lon)
PINS = [(10, 50.45, 30.52), (4, 50.11, 8.68), (2, 50.85, 4.35),
        (5, 51.50, -0.12), (22, 20.0, 86.0), (16, 25.03, 121.56),
        (17, 35.68, 139.69), (27, 26.50, 56.30), (45, 18.54, -72.34),
        (47, -15.79, -47.88), (52, -33.87, 151.21), (53, 40.71, -74.01),
        (65, 36.90, 30.71)]

TIMELINE = [
    ("~02:00", "OVERNIGHT", "Kyiv barrage: 3 Dnipro bridges hit"),
    ("~09:00", "ASIA CLOSE", "Nikkei -4.5%, Kospi -4.7%"),
    ("~12:00", "MIDDAY", "EU–UK summit opens in Brussels"),
    ("~14:00", "AFTERNOON", "COP31 final day: no deal, Antalya"),
    ("~16:00", "LATE", "Microsoft outage passes 9 hours"),
    ("~21:30", "US CLOSE", "Nasdaq -5.2%, worst week"),
]

# ---------- helpers ----------
def text_w(fnt, s):
    return fnt.getlength(s)

def fit(fnt, s, max_w):
    """Truncate with ellipsis so s fits max_w. Returns (text, truncated?)."""
    if text_w(fnt, s) <= max_w:
        return s, False
    ell = "…"
    lo, hi = 0, len(s)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if text_w(fnt, s[:mid] + ell) <= max_w:
            lo = mid
        else:
            hi = mid - 1
    return s[:lo] + ell, True

def draw_text(d, xy, s, fnt, fill):
    d.text(xy, s, font=fnt, fill=fill)

def lcg(seed, n):
    """Deterministic pseudo-random numbers in [0,1)."""
    out, x = [], seed
    for _ in range(n):
        x = (1103515245 * x + 12345) % (2 ** 31)
        out.append(x / (2 ** 31))
    return out

# ---------- world map polygons (lon, lat), stylised ----------
CONTINENTS = [
    # North America
    [(-168, 66), (-140, 70), (-125, 71), (-110, 68), (-95, 69), (-85, 66),
     (-75, 62), (-65, 60), (-55, 52), (-60, 45), (-70, 42), (-75, 35),
     (-80, 32), (-85, 30), (-90, 21), (-97, 16), (-105, 20), (-115, 28),
     (-125, 40), (-125, 49), (-140, 60), (-155, 58), (-168, 66)],
    # Greenland
    [(-58, 64), (-45, 60), (-40, 70), (-55, 76), (-68, 76), (-58, 64)],
    # South America
    [(-80, 10), (-75, 5), (-70, 0), (-60, -5), (-50, -5), (-40, -10),
     (-35, -20), (-40, -30), (-50, -35), (-60, -40), (-70, -50), (-75, -40),
     (-75, -20), (-80, -10), (-80, 10)],
    # Africa
    [(-10, 35), (0, 36), (10, 37), (20, 32), (30, 31), (35, 28), (40, 15),
     (48, 11), (51, 10), (48, 0), (40, -10), (35, -20), (30, -30), (20, -35),
     (15, -30), (12, -18), (8, -5), (0, 5), (-10, 15), (-17, 20), (-10, 35)],
    # Europe
    [(-10, 36), (-10, 44), (-2, 48), (0, 50), (5, 53), (8, 57), (10, 59),
     (18, 56), (21, 55), (28, 60), (30, 62), (25, 65), (20, 70), (15, 70),
     (10, 68), (5, 60), (0, 55), (-5, 50), (-10, 44)],
    # Asia
    [(30, 62), (40, 68), (50, 70), (60, 70), (70, 72), (80, 73), (90, 75),
     (110, 76), (130, 72), (150, 70), (160, 66), (170, 66), (178, 65),
     (170, 60), (160, 55), (150, 50), (140, 45), (135, 40), (130, 35),
     (127, 33), (122, 30), (120, 25), (110, 20), (108, 12), (105, 8),
     (100, 5), (98, 10), (95, 15), (90, 22), (85, 20), (80, 15), (77, 8),
     (75, 12), (70, 20), (65, 25), (60, 25), (55, 26), (50, 29), (48, 30),
     (45, 28), (40, 30), (36, 36), (30, 36), (30, 42), (30, 50), (30, 62)],
    # Australia
    [(113, -22), (114, -30), (120, -34), (130, -32), (140, -38), (150, -37),
     (153, -27), (150, -22), (146, -19), (142, -11), (136, -12), (132, -11),
     (126, -14), (122, -17), (118, -20), (113, -22)],
]

# ---------- heroes (original PIL-drawn scenes) ----------
def hero_kyiv(d, x, y, w, h):
    # Night sky over the Dnipro: 3 bridges, missile streaks, blasts.
    d.rectangle([x, y, x + w, y + h], fill=(14, 27, 46))
    rnd = lcg(20261120, 60)
    for i in range(30):
        sx = x + 6 + rnd[i * 2] * (w - 12)
        sy = y + 6 + rnd[i * 2 + 1] * (h * 0.45)
        r = 1 if rnd[i] < 0.7 else 2
        d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(220, 225, 235))
    # moon
    d.ellipse([x + w - 52, y + 10, x + w - 22, y + 40], fill=(235, 230, 200))
    # river
    d.rectangle([x, y + h - 26, x + w, y + h], fill=(28, 68, 110))
    d.line([x, y + h - 26, x + w, y + h - 26], fill=(90, 140, 190), width=2)
    # missile streaks
    for (sx, sy, ex, ey) in [(x + 40, y + 8, x + 90, y + 52),
                             (x + 150, y + 4, x + 185, y + 48),
                             (x + 250, y + 10, x + 285, y + 55)]:
        d.line([sx, sy, ex, ey], fill=(255, 200, 90), width=2)
        d.ellipse([ex - 3, ey - 3, ex + 3, ey + 3], fill=(255, 220, 120))
    # bridges: 3 arcs over the river
    for i, bx in enumerate([x + 18, x + 118, x + 218]):
        by = y + h - 26
        d.arc([bx, by - 34, bx + 78, by + 6], 180, 360, fill=(200, 205, 215), width=3)
        d.line([bx, by, bx + 78, by], fill=(200, 205, 215), width=3)
        for px in range(bx + 8, bx + 74, 11):
            d.line([px, by - 14, px, by], fill=(160, 165, 175), width=1)
    # blast glows on bridges 1 and 3
    for (cx, cy) in [(x + 55, y + h - 40), (x + 262, y + h - 42)]:
        for r, col in [(16, (255, 120, 40)), (10, (255, 190, 80)), (5, (255, 240, 160))]:
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)

def hero_markets(d, x, y, w, h):
    # Red Friday: plunging index line over a dark board.
    d.rectangle([x, y, x + w, y + h], fill=(16, 20, 28))
    for gy in range(y + 14, y + h - 18, 14):
        d.line([x + 8, gy, x + w - 8, gy], fill=(40, 48, 62), width=1)
    for gx in range(x + 28, x + w - 8, 34):
        d.line([gx, y + 10, gx, y + h - 22], fill=(40, 48, 62), width=1)
    # bars: down-trend
    bars = [62, 58, 60, 52, 48, 50, 40, 34, 36, 26, 18]
    bw = (w - 24) // len(bars)
    for i, v in enumerate(bars):
        bx = x + 12 + i * bw
        d.rectangle([bx, y + h - 22 - v, bx + bw - 3, y + h - 22],
                    fill=(150, 40, 30) if i % 2 else (190, 55, 40))
    # plunging line
    pts = [(x + 12 + i * ((w - 24) // 10), y + 16 + i * 7 + (3 if i % 3 == 0 else -2))
           for i in range(11)]
    d.line(pts, fill=(255, 70, 50), width=3, joint="curve")
    d.ellipse([pts[-1][0] - 4, pts[-1][1] - 4, pts[-1][0] + 4, pts[-1][1] + 4],
              fill=(255, 70, 50), outline=WHITE, width=1)
    d.text((x + 12, y + 6), "NASDAQ  −5.2%   ·   S&P 500  −3.7%",
           font=F_SANS_B(11), fill=(255, 120, 100))

def hero_cop(d, x, y, w, h):
    # Antalya: sun, sea, mountains, flags of the final day.
    d.rectangle([x, y, x + w, y + h], fill=(250, 214, 140))
    for i in range(6):  # sun rays
        d.line([x + w - 62, y + 34, x + w - 62 + (i - 2) * 16, y + 6],
               fill=(230, 170, 60), width=2)
    d.ellipse([x + w - 84, y + 12, x + w - 40, y + 56], fill=(240, 140, 40))
    # mountains
    d.polygon([(x, y + h - 26), (x + 70, y + 52), (x + 140, y + h - 26)],
              fill=(90, 110, 90))
    d.polygon([(x + 110, y + h - 26), (x + 190, y + 44), (x + 270, y + h - 26)],
              fill=(70, 95, 80))
    d.polygon([(x + 235, y + h - 26), (x + 285, y + 58), (x + w, y + h - 26)],
              fill=(90, 110, 90))
    # sea
    d.rectangle([x, y + h - 26, x + w, y + h], fill=(30, 110, 150))
    for wy in (y + h - 19, y + h - 10):
        for wx in range(x + 8, x + w - 20, 34):
            d.line([wx, wy, wx + 18, wy], fill=(180, 220, 240), width=2)
    # flags row
    cols = [(180, 35, 24), (30, 64, 100), (40, 130, 70), (200, 110, 20),
            (90, 60, 140), (20, 110, 130)]
    for i, c in enumerate(cols):
        fx = x + 14 + i * 20
        d.line([fx, y + 8, fx, y + 34], fill=(80, 70, 60), width=2)
        d.polygon([(fx, y + 8), (fx + 15, y + 13), (fx, y + 18)], fill=c)

# ---------- main render ----------
def render():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    truncations = []

    # ===== masthead =====
    d.rectangle([0, 0, W, 62], fill=NAVY)
    d.rectangle([0, 62, W, 65], fill=RED)
    draw_text(d, (16, 6), "ONE DAY · ONE PAGE · EVERY STORY DATED",
              F_SANS_B(9), (255, 200, 90))
    draw_text(d, (16, 18), "THE WORLD IN ONE DAY", F_SERIF_B(30), WHITE)
    right1 = "FRIDAY 20 NOVEMBER 2026"
    draw_text(d, (W - 16 - text_w(F_SANS_B(15), right1), 8), right1,
              F_SANS_B(15), WHITE)
    right2 = "78 STORIES  ·  15 REGIONS  ·  TOP 50 · $250"
    draw_text(d, (W - 16 - text_w(F_SANS_B(10), right2), 30), right2,
              F_SANS_B(10), (200, 215, 235))
    draw_text(d, (W - 16 - text_w(F_SANS(9), "make.fun · news-image-20261120"), 46),
              "make.fun · news-image-20261120", F_SANS(9), (160, 180, 200))

    # ===== hero band: 3 original drawn panels =====
    heroes = [
        ("KYIV — BRIDGES HIT", "Story 10 · ~117 missiles · 3 dead, 15 hurt", hero_kyiv),
        ("WALL STREET — RED FRIDAY", "Story 53 · Nasdaq -5.2%, worst week since Apr 2025", hero_markets),
        ("ANTALYA — COP31 FINAL DAY", "Story 65 · No deal; draft drops fossil fuels", hero_cop),
    ]
    hx, hy, hw, hh = 16, 70, 325, 120
    for i, (title, cap, fn) in enumerate(heroes):
        x = hx + i * (hw + 8)
        fn(d, x, hy, hw, hh)
        d.rectangle([x, hy, x + hw, hy + 20], fill=RED if i == 0 else
                    (NAVY if i == 1 else (40, 110, 60)))
        t, tr = fit(F_SANS_B(10), title, hw - 10)
        truncations.append(("hero title", tr))
        draw_text(d, (x + 5, hy + 4), t, F_SANS_B(10), WHITE)
        # caption strip
        d.rectangle([x, hy + hh - 20, x + hw, hy + hh], fill=(0, 0, 0))
        # semi-opaque look via dark fill is fine (deterministic)
        c, tr = fit(F_SANS(9), cap, hw - 10)
        truncations.append(("hero caption", tr))
        draw_text(d, (x + 5, hy + hh - 16), c, F_SANS(9), (240, 240, 240))

    # ===== world map with numbered pins =====
    my0, my1 = 196, 288
    d.rectangle([16, my0, W - 16, my1], fill=OCEAN)
    d.rectangle([16, my0, W - 16, my1], outline=NAVY, width=1)
    draw_text(d, (22, my0 + 3), "WHERE IT HAPPENED — 12 STORIES PINNED (numbers = story no.)",
              F_SANS_B(9), NAVY)
    mx0, mx1 = 16, W - 16
    def proj(lon, lat):
        px = mx0 + (lon + 180.0) / 360.0 * (mx1 - mx0)
        py = my0 + 16 + (72.0 - lat) / 122.0 * (my1 - my0 - 20)
        return px, py
    for poly in CONTINENTS:
        pts = [proj(lon, lat) for lon, lat in poly]
        d.polygon(pts, fill=LAND, outline=LAND_LN)
    # pins: small dot at the true location, numbered badge staggered
    # with a leader line so the 5-pin Europe cluster stays legible.
    PIN_OFF = {10: (0, -13), 2: (-18, -12), 4: (14, -13), 5: (-20, 10),
               65: (16, 10), 22: (0, -10), 16: (0, -10), 17: (0, -10),
               27: (0, -10), 45: (0, 10), 47: (0, 10), 52: (0, -10),
               53: (0, -11)}
    for (num, lat, lon) in PINS:
        px, py = proj(lon, lat)
        dx, dy = PIN_OFF.get(num, (0, -10))
        bx, by = px + dx, py + dy
        r = 8
        d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=RED)
        d.line([px, py, bx, by], fill=RED, width=1)
        d.ellipse([bx - r, by - r, bx + r, by + r], fill=RED, outline=WHITE, width=1)
        s = str(num)
        fw = text_w(F_SANS_B(8), s)
        draw_text(d, (bx - fw / 2, by - 6), s, F_SANS_B(8), WHITE)

    # ===== market strip =====
    ms_y0, ms_y1 = 292, 316
    d.rectangle([16, ms_y0, W - 16, ms_y1], fill=NAVY)
    strip = ("NASDAQ -5.2%  ·  S&P 500 -3.7%  ·  DOW -1.9%  ·  NIKKEI -4.5%  ·  "
             "KOSPI -4.7%  ·  NVDA -14%  ·  ANT -9%  ·  BTC $59,000  ·  GOLD $3,540 -4%  ·  "
             "WTI $84.10 +1.1%  ·  VIX ~36  ·  10Y 4.94%")
    for sz in (11, 10, 9):
        if text_w(F_SANS_B(sz), strip) <= (W - 32 - 16):
            break
    draw_text(d, (20, ms_y0 + (ms_y1 - ms_y0 - sz) / 2 - 1), strip,
              F_SANS_B(sz), WHITE)

    # ===== story grid: 3 columns x 26 rows =====
    gx0, gy0 = 16, 320
    col_w, gap = 324, 10
    row_h, rows = 21, 26
    d.line([16, gy0 - 2, W - 16, gy0 - 2], fill=RED, width=2)
    draw_text(d, (16, gy0 - 2 - 0), "", F_SANS(9), INK)  # no-op anchor
    f_num = F_SANS_B(10)
    f_tag = F_SANS_B(7)
    f_head = F_SANS(9)
    for idx, (region, code, colour, head) in enumerate(STORIES):
        col = idx // rows
        row = idx % rows
        x = gx0 + col * (col_w + gap)
        y = gy0 + row * row_h
        if row % 2 == 1:
            d.rectangle([x, y, x + col_w, y + row_h], fill=ALTROW)
        num_s = "%02d" % (idx + 1)
        draw_text(d, (x + 2, y + 4), num_s, f_num, RED)
        tag_w = text_w(f_tag, code) + 8
        tx = x + 24
        d.rounded_rectangle([tx, y + 4, tx + tag_w, y + 16], radius=3, fill=colour)
        draw_text(d, (tx + 4, y + 5), code, f_tag, WHITE)
        avail = col_w - (tx + tag_w - x) - 6
        htxt, tr = fit(f_head, head, avail)
        if tr:
            truncations.append(("story %02d" % (idx + 1), True))
        draw_text(d, (tx + tag_w + 4, y + 4), htxt, f_head, INK)
    grid_bottom = gy0 + rows * row_h  # 320 + 546 = 866

    # ===== region tally =====
    ty = grid_bottom + 6  # 872
    counts = {}
    for region, _, _, _ in STORIES:
        counts[region] = counts.get(region, 0) + 1
    d.rectangle([16, ty, W - 16, ty + 24], fill=(232, 226, 210))
    d.rectangle([16, ty, W - 16, ty + 24], outline=LINE, width=1)
    tally_parts = []
    code_of = {}
    for region, code, colour, _ in STORIES:
        code_of[region] = (code, colour)
    for region in REGION_ORDER:
        code, _ = code_of[region]
        tally_parts.append("%s %d" % (code, counts[region]))
    tally = "REGIONS  —  " + "  ·  ".join(tally_parts)
    for sz in (9, 8):
        if text_w(F_SANS_B(sz), tally) <= (W - 32 - 12):
            break
    draw_text(d, (22, ty + 6), tally, F_SANS_B(sz), NAVY)

    # ===== UTC timeline =====
    tl_y0 = 902
    draw_text(d, (16, tl_y0), "THE DAY IN UTC  (~ session times)",
              F_SANS_B(10), RED)
    d.line([16, tl_y0 + 16, W - 16, tl_y0 + 16], fill=NAVY, width=2)
    seg = (W - 32) / len(TIMELINE)
    for i, (t, lab, txt) in enumerate(TIMELINE):
        cx = 16 + seg * i + seg / 2
        d.ellipse([cx - 5, tl_y0 + 11, cx + 5, tl_y0 + 21], fill=RED,
                  outline=WHITE, width=1)
        tt, _ = fit(F_SANS_B(9), "%s  %s" % (t, lab), seg - 8)
        draw_text(d, (cx - text_w(F_SANS_B(9), tt) / 2, tl_y0 + 23), tt,
                  F_SANS_B(9), NAVY)
        et, tr = fit(F_SANS(8), txt, seg - 8)
        truncations.append(("timeline %d" % i, tr))
        draw_text(d, (cx - text_w(F_SANS(8), et) / 2, tl_y0 + 33), et,
                  F_SANS(8), INK)

    # ===== bottom band: Quote of the Day + DATE CHECK =====
    by0, by1 = 950, 1010
    # quote (left, ~58% width)
    qw = 590
    d.rectangle([16, by0, 16 + qw, by1], fill=WHITE, outline=NAVY, width=1)
    draw_text(d, (24, by0 + 4), "QUOTE OF THE DAY", F_SANS_B(9), RED)
    q1 = "\u201CA tremendous tax\u201D — Donald Trump, on US firms building"
    q2 = "data centres abroad; White House briefing, 20 Nov 2026."
    draw_text(d, (24, by0 + 18), q1, F_SERIF_B(11), INK)
    draw_text(d, (24, by0 + 33), q2, F_SERIF_B(11), INK)
    draw_text(d, (24, by0 + 47), "The day's sharpest line, from the day's own briefing.",
              F_SANS(8), MUTED)
    # date check (right)
    dx0 = 16 + qw + 8
    d.rectangle([dx0, by0, W - 16, by1], fill=(255, 238, 235), outline=RED, width=1)
    draw_text(d, (dx0 + 8, by0 + 4), "DATE CHECK — 20 NOV 2026 ONLY",
              F_SANS_B(9), RED)
    dc = [
        "Excluded (19 Nov): ICJ Myanmar ruling · Shenzhen summit ·",
        "Anthropic day-1 debut · Dutch embassy hit, Kyiv. No 21/22 Nov items.",
        "Every story on this page is dated Fri 20 Nov 2026.",
    ]
    for i, line in enumerate(dc):
        draw_text(d, (dx0 + 8, by0 + 18 + i * 12), line, F_SANS(9), INK)

    # ===== footer =====
    foot = ("THE WORLD IN ONE DAY  ·  Drawn entirely in code (PIL) — no photos  ·  "
            "78 stories · 15 regions  ·  Sources: Reuters · AP · Investopedia · IANS · "
            "UNFCCC · Open Chronicle  ·  tacinbau")
    for sz in (8, 7):
        if text_w(F_SANS(sz), foot) <= (W - 32):
            break
    draw_text(d, ((W - text_w(F_SANS(sz), foot)) / 2, 1013), foot,
              F_SANS(sz), MUTED)

    img.save(OUT, format="PNG")
    return truncations

def verify():
    assert len(STORIES) == 78, "story count %d" % len(STORIES)
    regions = []
    for r, _, _, _ in STORIES:
        if r not in regions:
            regions.append(r)
    assert len(regions) == 15, "region count %d" % len(regions)
    assert set(regions) == set(REGION_ORDER)
    counts = {}
    for r, _, _, _ in STORIES:
        counts[r] = counts.get(r, 0) + 1
    assert sum(counts.values()) == 78
    print("stories=78 regions=15 counts=%s" % counts)

if __name__ == "__main__":
    verify()
    trunc = render()
    bad = [t for t in trunc if t[1]]
    print("truncations:", bad if bad else "none")
    with open(OUT, "rb") as f:
        print("md5:", hashlib.md5(f.read()).hexdigest())
    print("saved", OUT)
