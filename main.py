#!/usr/bin/env python3
"""The World in One Day - Friday 20 November 2026. 52 stories, 7 regions.
Stdlib + Pillow only. Deterministic: no random, no clock, no network.
Run: python3 main.py  ->  entry.png (1024x1024, <1 MiB)."""
from PIL import Image, ImageDraw, ImageFont
import os
W, H = 1024, 1024
PAPER = (248, 242, 228); INK = (20, 33, 61); RED = (178, 34, 34)
BLUE = (29, 78, 137); GREY = (90, 90, 90); LINE = (20, 33, 61)
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANSB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
_fc = {}
def F(sz, b=False, s=False):
    k = (sz, b, s)
    if k not in _fc:
        _fc[k] = ImageFont.truetype(SERIF if s else (SANSB if b else SANS), sz)
    return _fc[k]
def wrap(t, f, w):
    out, cur = [], ""
    for wd in t.split(" "):
        t2 = (cur + " " + wd).strip()
        if f.getlength(t2) <= w or not cur:
            cur = t2
        else:
            out.append(cur); cur = wd
    if cur:
        out.append(cur)
    return out
def txt(d, x, y, t, f, fill=INK):
    d.text((x, y), t, font=f, fill=fill)
def ctr(d, cx, y, t, f, fill=INK):
    d.text((cx - f.getlength(t) / 2, y), t, font=f, fill=fill)
def rrect(d, x, y, w, h, fill, out=None):
    d.rectangle([x, y, x + w, y + h], fill=fill, outline=out)
# --- 52 stories, all dated Friday 20 Nov 2026 in their source (see DATE CHECK) ---
REGIONS = [
 ("NORTH AMERICA", BLUE, [
  "Senate blocks Iran war-powers bid, 51-48",
  "Trump: no rush on Iran - 'after Jan 1'",
  "Senate passes energy-permitting bill 62-33",
  "California subpoenas Nvidia over China risks",
  "SEC probes Nvidia books; shares fall 14%",
  "Visa, Mastercard, JPMorgan flag vendor breaches",
  "Canada's 2026 budget passes Commons 162-151",
  "Audit: ICE paid millions for empty beds"]),
 ("EUROPE", (123, 45, 139), [
  "Russian strikes hit 3 Kyiv bridges; 3 killed",
  "Poland airspace hit by 2 missiles and a drone",
  "Estonia to shut Russia border from Dec 1",
  "UK and EU agree post-Brexit reset deal",
  "EU approves 1bn military aid for Ukraine",
  "Feijoo beats Sanchez in Spain TV debate",
  "Eurozone confidence rises to -16.9 in Nov",
  "France probes leak to far-right RN party"]),
 ("ASIA-PACIFIC", (180, 83, 9), [
  "Trump, Xi, Putin meet in Shenzhen; peace vow",
  "Xi hails 'significant shift' in China-Australia ties",
  "Toxic liquor kills 11 in Manipur; 180+ ill",
  "India busts opioid ring shipping to US buyers",
  "RBI tipped to lift rates to 5.75% in Dec",
  "Nikkei -4.5%, Kospi -4.7% in Asia rout",
  "Exam-cheating scandal rocks South Korea",
  "Sydney liver kept alive a record 7 weeks",
  "100m red crabs march to sea on Christmas Is."]),
 ("MIDDLE EAST", (156, 43, 43), [
  "US blockade holds in Strait of Hormuz",
  "Tanker struck and ablaze near Khasab",
  "Houthi missile hits Riyadh's tallest tower",
  "Houthi raids cloud US-Saudi nuclear pact",
  "US presses Singapore, Malaysia on Iran curbs",
  "Record settler attacks mar West Bank harvest"]),
 ("AFRICA", (47, 107, 58), [
  "Angola to pay $180m for 10% of De Beers",
  "S. Africa mourns Phumzile Mlambo-Ngcuka, 71",
  "Egypt nears final IMF review; $2.3bn at stake",
  "3 die in Gombe village; Air Force blamed",
  "Zambia churches warn on arrests, intolerance",
  "Kenya contained Ebola 'with preparation'"]),
 ("LATIN AMERICA", (14, 116, 144), [
  "US: Chinese chemicals fuel Sinaloa cartel",
  "Costa Rica court voids budget curbs",
  "World Bank urges joint El Nino response",
  "Chile keeps bird-flu alert in Los Rios",
  "Mexico election-chief fight runs to 2027"]),
 ("MARKETS & TECH", (17, 24, 39), [
  "Nasdaq -5.3%; S&P -3.7% in 7th straight fall",
  "Nvidia -14% in a day; $2.8tn gone in 45 days",
  "Anthropic -9% a day after record $81.3bn IPO",
  "Bitcoin near $59k; gold $3,540, 14-month low",
  "Google launches Gemini 4 Neon, 1m context",
  "Nvidia, Microsoft deepen AI tie: Rubin on Azure"]),
 ("SCIENCE & CULTURE", (190, 24, 93), [
  "GTA 6: 32.5m copies, $3.79bn on day one",
  "'Hunger Games: Sunrise' opens in cinemas",
  "Ella Langley wins six CMA Awards",
  "Webb sees supergiant star swallow companion"]),
]
COLS = [[0, 1], [2, 3, 7], [4, 5, 6]]  # region indexes per column
NUMBERS = [("NASDAQ", "-5.3%", "Composite, worst day", RED),
 ("S&P 500", "-3.7%", "7th straight fall", RED),
 ("BITCOIN", "~$59,000", "Lowest since June", RED),
 ("GOLD", "$3,540", "14-month low", RED),
 ("ANTHROPIC IPO", "$81.3bn", "Largest ever; shares -9%", BLUE)]
TIMELINE = [("MORNING", "Asia rout: Nikkei -4.5%, Kospi -4.7%"),
 ("MIDDAY", "Shenzhen summit opens; peace declaration"),
 ("AFTERNOON", "COP31 goes into overtime on fossil fuels"),
 ("EVENING", "Houthi missile hits Riyadh tower"),
 ("CLOSE", "Nasdaq -5.3%; VIX jumps to 37")]
QUOTE = ("\"Transitioning away from fossil fuels ... is a "
 "matter of survival.\"")
GOOD = ["Donated liver kept alive a record 7 weeks, Sydney.",
 "100m red crabs march to sea; numbers doubled in 5 years.",
 "Firefly lost since 1983 flashes again in Virginia."]
LAND = [[(-168, 66), (-140, 70), (-125, 72), (-110, 68), (-95, 70), (-85, 66),
  (-75, 62), (-60, 60), (-55, 47), (-70, 42), (-75, 35), (-80, 26), (-90, 21),
  (-97, 16), (-105, 20), (-115, 28), (-125, 40), (-125, 48), (-140, 60),
  (-165, 60)],
 [(-80, 10), (-60, 5), (-50, 0), (-35, -8), (-40, -20), (-50, -30),
  (-58, -38), (-65, -45), (-70, -35), (-73, -20), (-78, -5)],
 [(-10, 36), (0, 38), (10, 38), (20, 40), (28, 36), (30, 42), (20, 45),
  (12, 44), (5, 43), (-2, 48), (-5, 50), (0, 52), (5, 55), (10, 57),
  (18, 56), (21, 60), (18, 65), (12, 68), (5, 60), (0, 58), (-8, 55), (-10, 48)],
 [(-17, 15), (-10, 30), (0, 36), (10, 37), (20, 32), (30, 31), (35, 28),
  (43, 12), (48, 11), (51, 2), (40, -5), (35, -18), (28, -30), (20, -35),
  (15, -28), (12, -18), (9, -2), (9, 4), (-8, 5), (-15, 12)],
 [(35, 36), (42, 38), (48, 30), (55, 26), (60, 25), (66, 25), (72, 20),
  (78, 8), (80, 13), (88, 22), (92, 16), (98, 10), (100, 8), (104, 2),
  (108, 10), (110, 20), (118, 25), (122, 32), (128, 38), (135, 43),
  (140, 45), (142, 52), (158, 60), (170, 66), (178, 65), (170, 60),
  (160, 55), (150, 60), (140, 72), (130, 72), (110, 74), (95, 76),
  (80, 73), (68, 68), (55, 68), (45, 68), (40, 60), (35, 50), (30, 42)],
 [(113, -22), (114, -30), (115, -35), (124, -33), (130, -32), (137, -35),
  (140, -38), (147, -39), (150, -37), (153, -27), (146, -19), (142, -11),
  (136, -12), (132, -12), (126, -14), (122, -17), (118, -20)]]
PINS = [(17, 114, 22), (9, 30, 50), (28, 47, 25), (27, 56, 26), (19, 94, 25),
 (24, 151, -34), (32, 13, -9), (33, 28, -26), (38, -99, 19), (43, -74, 41),
 (22, 139, 36), (31, 35, 32)]

def hero_a(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(191, 217, 232))
    for i, bx in enumerate([18, 78, 150, 215, 262]):
        bh = [55, 78, 66, 84, 46][i]
        d.rectangle([x + bx, y + h - 62 - bh, x + bx + 42, y + h - 62],
                    fill=(70, 90, 110) if i % 2 else (52, 68, 90))
        for wy in range(4):
            d.rectangle([x + bx + 6, y + h - 52 - bh + wy * 22,
                         x + bx + 14, y + h - 44 - bh + wy * 22],
                        fill=(255, 220, 120))
    d.ellipse([x + w - 52, y + 8, x + w - 20, y + 40], fill=(255, 214, 90))
    d.ellipse([x + 150, y + h - 62, x + w - 30, y + h - 18], fill=(122, 72, 40))
    for i, (fx, fc) in enumerate([(150, RED), (205, (200, 30, 30)), (258, (30, 60, 160))]):
        d.line([x + fx, y + h - 62, x + fx, y + h - 100], fill=INK, width=2)
        d.rectangle([x + fx, y + h - 100, x + fx + 26, y + h - 86], fill=fc)
        d.ellipse([x + fx - 4, y + h - 84, x + fx + 10, y + h - 70], fill=(255, 205, 170))
        d.polygon([(x + fx - 6, y + h - 70), (x + fx + 16, y + h - 70),
                   (x + fx + 3, y + h - 58)], fill=(40, 40, 40))
    txt(d, x + 8, y + h - 16, "Three leaders, one table, no breakthrough.",
        F(9, True), (20, 33, 61))
def hero_b(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(232, 201, 160))
    d.ellipse([x + 30, y + 6, x + 62, y + 38], fill=(255, 180, 90))
    d.rectangle([x, y + h - 62, x + w, y + h], fill=(64, 120, 180))
    for bx in [10, 120, 230]:
        d.arc([x + bx, y + 52, x + bx + 82, y + 118], 180, 360, fill=(40, 40, 40), width=5)
        d.line([x + bx, y + 118, x + bx + 82, y + 118], fill=(40, 40, 40), width=5)
        d.line([x + bx + 41, y + 52, x + bx + 41, y + 30], fill=(40, 40, 40), width=3)
    for sx, sy, sr in [(60, 30, 26), (150, 22, 32), (250, 34, 24)]:
        d.ellipse([x + sx - sr, y + sy - 14, x + sx + sr, y + sy + 14], fill=(120, 120, 120))
    d.polygon([(x + 285, y + 18), (x + 295, y + 34), (x + 312, y + 34),
               (x + 298, y + 44), (x + 303, y + 60), (x + 285, y + 50),
               (x + 267, y + 60), (x + 272, y + 44), (x + 258, y + 34),
               (x + 275, y + 34)], fill=(255, 120, 0))
    txt(d, x + 8, y + h - 16, "Three bridges hit; Poland airspace violated.",
        F(9, True), (20, 33, 61))
def hero_c(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(243, 226, 199))
    for i, bx in enumerate([14, 66, 118, 250, 288]):
        bh = [55, 60, 68, 55, 48][i]
        d.rectangle([x + bx, y + h - 62 - bh, x + bx + 30, y + h - 62],
                    fill=(90, 90, 90) if i % 2 else (60, 60, 60))
    pts = [(x + 20, y + 30), (x + 80, y + 52), (x + 140, y + 44),
           (x + 200, y + 82), (x + 260, y + 104), (x + 300, y + 132)]
    d.line(pts, fill=RED, width=5, joint="curve")
    d.polygon([(x + 300, y + 132), (x + 288, y + 118), (x + 306, y + 116)],
              fill=RED)
    txt(d, x + 14, y + 8, "NASDAQ", F(20, True), RED)
    txt(d, x + 150, y + 12, "-5.3% in a day", F(13, True), RED)
    txt(d, x + 8, y + h - 16, "AI rally breaks: $4tn gone in a week.",
        F(9, True), (20, 33, 61))
def build():
    im = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(im)
    d.rectangle([6, 6, W - 7, H - 7], outline=INK, width=2)
    ctr(d, W // 2, 14, "THE WORLD IN ONE DAY", F(40, s=True))
    ctr(d, W // 2, 60, "FRIDAY, 20 NOVEMBER 2026  \u2022  52 STORIES  \u2022  "
        "SEVEN REGIONS  \u2022  ONE FRONT PAGE", F(11, True))
    d.line([14, 80, W - 14, 80], fill=INK, width=1)
    rrect(d, 12, 84, 1000, 22, INK)
    ctr(d, W // 2, 88, "SHENZHEN SUMMIT  \u2022  KYIV UNDER FIRE  \u2022  "
        "WALL STREET ROUT  \u2022  COP31 OVERTIME", F(11, True), PAPER)
    hy, hh, pw = 110, 182, 322
    for i, (lab, col, fn) in enumerate([
            ("1  SHENZHEN \u2014 THE SUMMIT", BLUE, hero_a),
            ("2  KYIV \u2014 BRIDGES UNDER FIRE", (156, 43, 43), hero_b),
            ("3  WALL STREET \u2014 THE AI ROUT", RED, hero_c)]):
        x = 12 + i * 334
        rrect(d, x, hy, pw, 22, col)
        txt(d, x + 8, hy + 4, lab, F(10, True), (255, 255, 255))
        fn(d, x, hy + 22, pw, hh - 22)
        d.rectangle([x, hy, x + pw, hy + hh], outline=INK, width=1)
    ny = 300
    for i, (lab, val, sub, col) in enumerate(NUMBERS):
        x = 12 + i * 202
        rrect(d, x, ny, 194, 46, (255, 255, 255), out=INK)
        txt(d, x + 8, ny + 4, lab, F(8, True), GREY)
        txt(d, x + 8, ny + 16, val, F(20, True), col)
        txt(d, x + 8, ny + 36, sub, F(8), GREY)
    gy = 358
    txt(d, 12, gy, "52 STORIES, NUMBERED \u2014 READ DOWN EACH COLUMN",
        F(10, True))
    txt(d, 1012, gy, "ALL DATED 20 NOV 2026", F(10, True), RED)
    d.line([12, gy + 16, 1012, gy + 16], fill=INK, width=1)
    n = 0
    colx = [12, 350, 688]
    colw = [324, 324, 324]
    bottoms = []
    for ci, ridxs in enumerate(COLS):
        y = gy + 24
        for ri in ridxs:
            name, col, items = REGIONS[ri]
            rrect(d, colx[ci], y, colw[ci], 18, col)
            txt(d, colx[ci] + 6, y + 3, "%s \u2014 %d" % (name, len(items)),
                F(10, True), (255, 255, 255))
            y += 21
            for it in items:
                n += 1
                ls = wrap(it, F(10), colw[ci] - 24)
                assert len(ls) <= 2, "story too long: %s" % it
                rrect(d, colx[ci], y + 1, 15, 12, col)
                ctr(d, colx[ci] + 7, y + 1, str(n), F(8, True), (255, 255, 255))
                for li, ln in enumerate(ls):
                    txt(d, colx[ci] + 20, y + li * 12, ln, F(10))
                y += 12 * len(ls) + 2
            y += 5
        bottoms.append(y)
    return im, d, max(bottoms)

def finish(im, d, top):
    y = top + 4
    txt(d, 12, y, "WHERE IT HAPPENED \u2014 PINS ARE STORY NUMBERS",
        F(10, True))
    txt(d, 624, y, "THE DAY, HOUR BY HOUR", F(10, True))
    d.line([12, y + 16, 1012, y + 16], fill=INK, width=1)
    my = y + 22
    mh = 132
    mx, mw = 12, 600
    d.rectangle([mx, my, mx + mw, my + mh], fill=(220, 238, 245), outline=INK)
    def ll(lon, lat):
        return (mx + 8 + (lon + 170) / 360.0 * (mw - 16),
                my + 6 + (75 - lat) / 130.0 * (mh - 12))
    for poly in LAND:
        d.polygon([ll(a, b) for a, b in poly], fill=(190, 215, 170),
                  outline=(120, 150, 110))
    for num, lon, lat in PINS:
        px, py = ll(lon, lat)
        d.ellipse([px - 8, py - 8, px + 8, py + 8], fill=RED, outline=(255, 255, 255))
        ctr(d, px, py - 6, str(num), F(8, True), (255, 255, 255))
    ty = my
    for ph, ev in TIMELINE:
        txt(d, 624, ty, ph, F(10, True), RED)
        w = F(10, True).getlength(ph) + 8
        ls = wrap(ev, F(10), 388 - w)
        assert len(ls) == 1, "timeline too long: %s" % ev
        txt(d, 624 + w, ty, ls[0], F(10))
        ty += 15
    qy = ty + 4
    rrect(d, 624, qy, 388, 48, (255, 255, 255), out=INK)
    txt(d, 632, qy + 4, "QUOTE OF THE DAY \u2014 JESS GASPER, MARSHALL ISLANDS, COP31",
        F(8, True), GREY)
    for i, ln in enumerate(wrap(QUOTE, F(11), 372)):
        txt(d, 632, qy + 18 + i * 13, ln, F(11))
    by = my + mh + 10
    boxes = [("GOOD NEWS IN BRIEF", GOOD),
             ("DATE CHECK", ["Every story above is dated Fri 20 Nov 2026",
              "in its source. ICJ Myanmar ruling (19 Nov) and",
              "Anthropic debut (19 Nov) count only as 20 Nov",
              "follow-ups. No 21 Nov item is included."]),
             ("HOW IT WAS MADE", ["All artwork drawn in code with Pillow;",
              "no photos, no AI images. Deterministic:",
              "run twice, byte-identical PNG. 52 stories,",
              "7 regions, 12 map pins, 5-part timeline."])]
    for i, (t, lines) in enumerate(boxes):
        x = 12 + i * 336
        rrect(d, x, by, 328, 74, (255, 255, 255), out=INK)
        txt(d, x + 8, by + 5, t, F(9, True), RED)
        for j, ln in enumerate(lines):
            txt(d, x + 8, by + 19 + j * 12, ln, F(9))
    fy = by + 82
    assert fy + 26 <= H - 12, "layout overflow: %d" % fy
    ctr(d, W // 2, fy, "Sources: Reuters \u2022 Investopedia \u2022 NPR \u2022 "
        "The Guardian \u2022 IPS \u2022 Le Monde \u2022 AP wires, 20 Nov 2026.",
        F(9), GREY)
    ctr(d, W // 2, fy + 12, "THE WORLD IN ONE DAY \u2014 FRIDAY 20 NOVEMBER 2026 "
        "\u2022 52 STORIES \u2022 DRAWN IN CODE, NOT PHOTOGRAPHED", F(9, True))
    return fy
if __name__ == "__main__":
    im, d, bot = build()
    finish(im, d, bot)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    im.save(out, optimize=True)
    print("stories=%d regions=%d pins=%d size=%s" % (
        sum(len(r[2]) for r in REGIONS), len(REGIONS), len(PINS), im.size))
    print("saved", out)
