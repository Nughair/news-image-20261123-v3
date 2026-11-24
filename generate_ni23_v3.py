#!/usr/bin/env python3
"""news-image-20261123 generator, v3 — "LATE EXTRA" magazine edition.

A third, independent presentation of the same news day as v1/v2:
Monday 23 November 2026, 40 stories (3 leads, 10 pictured cards,
27 wire briefs). Where v1/v2 ran three equal lead columns over a
half-width map, v3 leads with one wide hero (the Libya strike),
two half-width leads under it, a full-width map band across the
main column, and the briefs as a right-hand "WIRE" rail that runs
the height of the page. Palette: cream paper, oxblood burgundy,
ochre and charcoal — no navy.

Every story happened on Monday 23 November 2026 where it happened,
or was first reported / confirmed / published on Monday; earlier
timing is disclosed in the story text. Labels: REPORTED = confirmed
by the outlet named · CLAIM = one side's claim, unverified ·
FORECAST = scheduled, has not happened yet. See STORIES.md.

All artwork is drawn programmatically in this file (flat-vector
style); no photographs, no external assets beyond system fonts.

Usage: python3 generate_ni23_v3.py
  -> output/entry.png (1024x1024) + output/preview-300.png
"""
import math
import os

from PIL import Image, ImageDraw, ImageFont

# ------------------------------------------------------------------ fonts
FONT_DIR = "/usr/share/fonts/truetype/noto"
SERIF_BLACK = f"{FONT_DIR}/NotoSerif-Black.ttf"
SERIF_BOLD = f"{FONT_DIR}/NotoSerif-Bold.ttf"
SERIF = f"{FONT_DIR}/NotoSerif-Regular.ttf"
SERIF_IT = f"{FONT_DIR}/NotoSerif-Italic.ttf"
SANS_BLACK = f"{FONT_DIR}/NotoSans-Black.ttf"
SANS_XB = f"{FONT_DIR}/NotoSans-ExtraBold.ttf"
SANS_BOLD = f"{FONT_DIR}/NotoSans-Bold.ttf"
SANS = f"{FONT_DIR}/NotoSans-Regular.ttf"

_font_cache = {}


def F(path, size):
    key = (path, size)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(path, size)
    return _font_cache[key]


# ------------------------------------------------------------------ palette
PAPER = (250, 246, 233)
INK = (26, 24, 22)
BURG = (122, 22, 32)          # oxblood burgundy — primary
BURG_DARK = (84, 14, 24)
OCHRE = (196, 138, 28)
CHAR = (38, 36, 34)           # charcoal bands
GREY = (104, 100, 94)
RULE = (52, 48, 44)
CREAM_LINE = (219, 210, 188)
GREEN = (44, 128, 74)
SKY_DAWN = (250, 196, 120)
SKY_DAY = (168, 205, 226)
SEA = (64, 110, 158)

W = H = 1024
M = 24                        # page margin
CW = W - 2 * M                # content width = 976
MAIN_X = M                    # main column: 24..688 (664 wide)
MAIN_W = 664
RAIL_X = 700                  # wire rail: 700..1000 (300 wide)
RAIL_W = W - M - RAIL_X       # 300

img = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(img, "RGBA")

WARNINGS = []


# ------------------------------------------------------------------ helpers
def tw(s, f):
    return d.textlength(s, font=f)


def fit(s, path, start, max_w, min_size=7):
    """Largest font (<= start) whose rendering of s fits max_w."""
    size = start
    while size > min_size and tw(s, F(path, size)) > max_w:
        size -= 1
    if tw(s, F(path, size)) > max_w:
        WARNINGS.append(f"fit() could not fit {s!r} in {max_w}px")
    return F(path, size)


def wrap(s, f, max_w):
    words = s.split()
    lines, cur = [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if tw(t, f) <= max_w or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


def text_block(x, y, s, f, max_w, leading, fill=INK, max_lines=None):
    lines = wrap(s, f, max_w)
    if max_lines and len(lines) > max_lines:
        WARNINGS.append(f"text truncated to {max_lines} lines: {s[:40]!r}...")
        lines = lines[:max_lines]
    for i, ln in enumerate(lines):
        d.text((x, y + i * leading), ln, font=f, fill=fill)
    return y + len(lines) * leading


def centre(s, cx, y, f, fill=INK):
    d.text((cx - tw(s, f) / 2, y), s, font=f, fill=fill)


def chip(x, y, text, bg, fg=(255, 255, 255), font_size=9, pad_x=5, pad_y=2):
    f = F(SANS_BOLD, font_size)
    w_ = tw(text, f) + 2 * pad_x
    h_ = font_size + 2 * pad_y + 2
    d.rectangle([x, y, x + w_, y + h_], fill=bg)
    d.text((x + pad_x, y + pad_y), text, font=f, fill=fg)
    return w_, h_


def stat_chip_right(x, y, w, text):
    """White stat chip pinned to the top-right of a scene of width w."""
    sf = F(SANS_BOLD, 9)
    sw = tw(text, sf) + 10
    d.rectangle([x + w - sw - 7, y + 7, x + w - 7, y + 7 + 14],
                fill=(255, 255, 255))
    d.text((x + w - sw - 2, y + 9), text, font=sf, fill=INK)
    return sw


def rule(x0, x1, y, fill=RULE, width=1):
    d.line([x0, y, x1, y], fill=fill, width=width)


def person(cx, cy, s, colour):
    """Tiny figure: head + shoulders, s = height px, feet at cy."""
    r = s * 0.16
    d.ellipse([cx - r, cy - s, cx + r, cy - s + 2 * r], fill=colour)
    d.pieslice([cx - s * 0.30, cy - s + 2 * r - 2, cx + s * 0.30,
                cy + s * 0.35], 180, 360, fill=colour)


def badge(x, y, num, size=15):
    """Story-number badge: ink square, white number."""
    d.rectangle([x, y, x + size, y + size - 1], fill=INK)
    nf = F(SANS_BOLD, 9 if size < 15 else 10)
    s = str(num)
    d.text((x + size / 2 - tw(s, nf) / 2, y + 2), s, font=nf,
           fill=(255, 255, 255))


def kicker_label(x, y, kicker, label, font_size=9):
    """Number-badge-less kicker line: PLACE · [dot] LABEL."""
    kf = F(SANS_BOLD, font_size)
    d.text((x, y), kicker + "  ·", font=kf, fill=BURG)
    lx = x + tw(kicker + "  ·", kf) + 4
    lc = BURG if label == "CLAIM" else GREEN
    d.ellipse([lx, y + 3, lx + 6, y + 9], fill=lc)
    d.text((lx + 9, y), label, font=kf, fill=lc)


# ------------------------------------------------------------------ content
STRAP = ("UKRAINE SINKS A RUSSIAN WARSHIP OFF LIBYA · COP31 ENDS WITH "
         "NO DEAL · NATO COUNCIL SITS OVER POLAND")

STATS = [
    ("44h", "COP31 OVERTIME, NO DEAL"),
    ("7", "SEA DRONES OFF BENGHAZI"),
    ("22", "HORMUZ ATTACKS IN NOVEMBER"),
    ("99%", "OF GAZA AT RISK"),
    ("24", "DEAD IN CIKANDE FIRE"),
    ("$61,417", "BITCOIN, MONDAY PRINT"),
]

# (name, count, colour) — true tally of the 40 stories.
REGIONS = [
    ("AMERICAS", 12, (104, 62, 140)),
    ("EUROPE", 12, (38, 84, 150)),
    ("ASIA-PACIFIC", 6, (44, 128, 74)),
    ("AFRICA", 5, (196, 116, 30)),
    ("MIDDLE EAST", 3, (178, 24, 32)),
    ("WORLD", 2, (38, 36, 34)),
]

UTC_STRIP = [
    ("04:07", "Two tankers mined"),
    ("05:28", "COP31 ends, no pact"),
    ("06:27", "Bitcoin $61,417"),
    ("08:57", "Dymer toll at 11"),
    ("09:01", "Hormuz: CRITICAL"),
    ("15:42", "States sue SpaceX"),
]

HERO = {
    "num": 3, "tag": "LIBYA: SUNK", "stat": "7 DRONES",
    "kicker": "WAR AT SEA · BENGHAZI", "label": "REPORTED",
    "headline": "Ukraine sinks a Russian warship off Libya",
    "body": ("Zelenskyy announces on Monday that seven sea drones sank "
             "the corvette Merkury in Benghazi on Sunday; the cargo "
             "ship MV Angara was hit too, and a Ka-27 helicopter "
             "destroyed — 2,400 km from the front."),
    "source": "REUTERS / AP · KYIV",
}

LEADS = [
    {
        "num": 1, "tag": "COP31: NO DEAL", "stat": "44 HRS",
        "kicker": "CLIMATE · ANTALYA", "label": "REPORTED",
        "headline": "COP31 ends with no deal — the longest summit ever",
        "body": ("Kurum concedes defeat after 44 hours of overtime, as "
                 "the EU and 130 nations reject a text with no "
                 "fossil-fuel language."),
        "source": "UN NEWS / BBC · ANTALYA",
        "scene": "cop31",
    },
    {
        "num": 2, "tag": "NATO: EMERGENCY", "stat": "3 MISSILES",
        "kicker": "ALLIANCE · BRUSSELS", "label": "REPORTED",
        "headline": "NATO in emergency session over Poland",
        "body": ("The Council convenes on Monday over three Kh-101 "
                 "missiles that fell in Poland on Friday. Warsaw wants "
                 "stronger eastern-flank air defences."),
        "source": "REUTERS / RMF24 · BRUSSELS",
        "scene": "nato",
    },
]

# Cards: (num, tag, stat, place, label, headline, caption, source, scene)
CARDS = [
    (4, "HORMUZ", "22 IN NOV", "STRAIT OF HORMUZ", "REPORTED",
     "Hormuz attacks hit a wartime high", "Most since the war began",
     "CNN / UKMTO", "tanker"),
    (5, "GAZA", "99% AT RISK", "GAZA", "REPORTED",
     "Gaza a 'toxic wasteland', Oxfam warns", "99% of land contaminated",
     "OXFAM / CEOBS", "gaza"),
    (6, "CIKANDE", "24 DEAD", "INDONESIA", "REPORTED",
     "Cikande fire toll confirmed at 24", "Search resumes; ~30 missing",
     "REUTERS", "cikande"),
    (7, "GROK", "2 STATES SUE", "UNITED STATES", "REPORTED",
     "Two states sue SpaceX over Grok", "Deepfakes of real photos",
     "REUTERS / WIRED", "grok"),
    (8, "SPUTNIK-S", "THIS YEAR", "SPACE", "CLAIM",
     "Russia 'ready' with nuclear satellite", "Per NATO intel reports",
     "NDR / WDR / SZ", "satellite"),
    (9, "DENMARK", "EU TALKS", "COPENHAGEN", "REPORTED",
     "Denmark takes visa ban to the EU", "EU-wide Russian visa curb",
     "REUTERS", "denmark"),
    (10, "DYMER", "11 DEAD", "UKRAINE", "REPORTED",
     "Dymer toll 11; Kyiv region mourns", "Boy freed after 14 hours",
     "AP / REUTERS", "dymer"),
    (11, "MARKETS", "+2.2% S&P", "WALL STREET", "REPORTED",
     "Markets rebound; Bitcoin tops $60k", "Gold $3,620; Brent ~$92",
     "MORNINGSTAR", "markets"),
    (12, "OVERSIGHT", "EO 14438", "WASHINGTON", "REPORTED",
     "Agencies told: clear Congress first", "Democrats cry foul",
     "NPR / CNN", "whitehouse"),
    (13, "SEOUL", "1ST WOMAN", "SOUTH KOREA", "REPORTED",
     "Seoul names first woman spy chief", "Kang Kum-sil to run the NIS",
     "REUTERS", "seoul"),
]

# Wire briefs: (num, text, source, label-or-None) — REPORTED unless tagged.
# 37–40 verified against Reuters, Mon 23 Nov 2026 (see STORIES.md).
BRIEFS = [
    (14, "Dhaka: Hasina jailed if she returns", "Reuters", None),
    (15, "Kryvyi Rih toll rises to 11", "AP", None),
    (16, "Kremlin accuses Kyiv of 'terrorist activity'", "Reuters", None),
    (17, "Bangkok: MP's royal-defamation verdict upheld", "AP", None),
    (18, "SEC probing Nvidia's accounting", "Reuters", None),
    (19, "Huang 'in contact' with China spies", "NYT", "CLAIM"),
    (20, "Anthropic shares rise after $81bn IPO", "Investopedia", None),
    (21, "Clayton to double as acting cyber chief", "Axios", None),
    (22, "Pentagon pressed over NSA deaths", "Legion", None),
    (23, "FedEx pilot of 1994 rescue dies at 82", "", None),
    (24, "Zelenskyy: free paid-for Patriots", "Reuters", None),
    (25, "Warsaw: Poland will not invoke Article 4", "RMF24", None),
    (26, "Gripen held fire over Poland", "Reuters", None),
    (27, "MP: Iran stops 10 tankers a day", "IRNA", "CLAIM"),
    (28, "Libya: Merkury was refuelling under deal", "CNN", None),
    (29, "New reports detail Epstein's Russia links", "Nexus", None),
    (30, "Tokyo: Asia tech sell-off eases", "Morningstar", None),
    (31, "Zverev ends year as world No. 1 despite loss", "Times", None),
    (32, "NYC storm for Thanksgiving", "NOAA", "FORECAST"),
    (33, "California: high tides and rain hit Monday", "", None),
    (34, "Bengals at Commanders tonight", "ESPN", "FORECAST"),
    (35, "Brentford v Everton", "Sportradar", "FORECAST"),
    (36, "Tripoli voices 'grave concern' over ports", "WSJ", None),
    (37, "Dushanbe: Tajikistan starts ICC withdrawal", "Reuters", None),
    (38, "Lusaka: opposition leader faces treason trial", "Reuters", None),
    (39, "Berlin: bomb threats hit ~450 schools", "Reuters", None),
    (40, "Kinshasa: Congo halts cobalt exports again", "Reuters", None),
]

DATE_CHECK = (
    "Not Monday's news: Democrats' 258 seats (Sun) · penny signed out "
    "(Fri) · Delta's 1,600-flight outage (Sun) · Alcaraz wins Turin "
    "(Sun) · Liverpool 4–0 Man Utd (Sun) · Hong Kong vote (Sun) · "
    "Bolsonaro in ICU (Sun) · El Chapo Isidro caught (Sat) · Trump's "
    "Iran remarks (Fri) · Riemann claim (Sun)."
)

FOOTER = ("Every story here happened, or was first reported, on Monday "
          "23 November 2026. Claims are labelled as claimed; briefs are "
          "REPORTED unless tagged. Pictures and map: original, drawn in code.")


# ------------------------------------------------------------------ scenes
def scene_libya(x, y, w, h):
    """Hero: night harbour at Benghazi — big warship ablaze, four sea
    drones closing in, plum-dark sky (v3's dusk palette, not v2 blue)."""
    top, bot = (34, 26, 54), (88, 52, 66)
    for i in range(int(h * 0.58)):
        t = i / (h * 0.58)
        c = tuple(int(top[j] * (1 - t) + bot[j] * t) for j in range(3))
        d.line([x, y + i, x + w, y + i], fill=c)
    for i in range(60):
        px = x + (i * 97) % int(w)
        py = y + (i * 37) % int(h * 0.42)
        d.point((px, py), fill=(226, 224, 238))
    d.ellipse([x + w * 0.80, y + h * 0.05, x + w * 0.80 + 13,
               y + h * 0.05 + 13], fill=(238, 234, 214))
    # sea
    d.rectangle([x, y + h * 0.58, x + w, y + h], fill=(30, 44, 74))
    d.rectangle([x + w * 0.55, y + h * 0.58, x + w * 0.86, y + h],
                fill=(66, 84, 118))
    # warship, centre-right, large: hull, superstructure, mast
    sx, sy = x + w * 0.46, y + h * 0.55
    d.polygon([(sx, sy), (sx + w * 0.42, sy), (sx + w * 0.375, sy + h * 0.14),
               (sx + w * 0.05, sy + h * 0.14)], fill=(56, 58, 66))
    d.rectangle([sx + w * 0.13, sy - h * 0.20, sx + w * 0.24, sy],
                fill=(74, 78, 86))
    d.rectangle([sx + w * 0.27, sy - h * 0.13, sx + w * 0.315, sy],
                fill=(74, 78, 86))
    d.rectangle([sx + w * 0.06, sy - h * 0.06, sx + w * 0.11, sy],
                fill=(74, 78, 86))
    d.line([sx + w * 0.185, sy - h * 0.20, sx + w * 0.185, sy - h * 0.33],
           fill=(96, 100, 108), width=3)
    d.line([sx + w * 0.185, sy - h * 0.33, sx + w * 0.26, sy - h * 0.26],
           fill=(96, 100, 108), width=2)
    # fire on the aft deck + a light smoke plume drifting right
    fx, fy = sx + w * 0.30, sy - h * 0.13
    d.ellipse([fx - 26, fy - 17, fx + 26, fy + 17], fill=(255, 168, 44))
    d.ellipse([fx - 15, fy - 10, fx + 15, fy + 10], fill=(255, 222, 120))
    d.polygon([(fx - 13, fy - 10), (fx, fy - 34), (fx + 13, fy - 10)],
              fill=(240, 110, 36))
    for (ox, oy, orr) in [(0.86, 0.20, 9), (0.92, 0.15, 12),
                          (0.97, 0.10, 15)]:
        d.ellipse([x + w * ox - orr, y + h * oy - orr * 0.55,
                   x + w * ox + orr, y + h * oy + orr * 0.55],
                  fill=(84, 74, 80, 115))
    # firelight shimmer on the water (narrow, faint — not a slab)
    d.rectangle([fx - 14, y + h * 0.72, fx + 14, y + h * 0.97],
                fill=(150, 96, 44, 55))
    d.rectangle([fx - 7, y + h * 0.72, fx + 7, y + h * 0.90],
                fill=(170, 110, 50, 45))
    # four sea drones from the left, with foam wakes + 3 distant dots
    for (dx, dy, s) in [(0.05, 0.72, 1.45), (0.16, 0.84, 1.2),
                        (0.26, 0.68, 1.3), (0.35, 0.80, 1.05)]:
        bx, by = x + w * dx, y + h * dy
        d.line([bx - 46 * s, by + 7, bx, by], fill=(205, 224, 242), width=2)
        d.polygon([(bx, by - 5), (bx + 24 * s, by), (bx, by + 5)],
                  fill=(14, 14, 18))
        d.ellipse([bx + 19 * s - 2, by - 2, bx + 19 * s + 2, by + 2],
                  fill=(255, 90, 60))
    for (dx, dy) in [(0.30, 0.62), (0.38, 0.90), (0.12, 0.63)]:
        d.ellipse([x + w * dx - 2, y + h * dy - 2, x + w * dx + 2,
                   y + h * dy + 2], fill=(16, 16, 20))


def scene_cop31(x, y, w, h):
    """Dawn over Antalya: sun clear of the headland, delegates at a long
    table, one cream empty chair at its head."""
    for i in range(h):
        t = i / h
        c = tuple(int(SKY_DAWN[j] * (1 - t) + SKY_DAY[j] * t) for j in range(3))
        d.line([x, y + i, x + w, y + i], fill=c)
    sx, sy, sr = x + w * 0.70, y + h * 0.30, h * 0.17
    d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(255, 214, 90))
    d.ellipse([sx - sr * 0.7, sy - sr * 0.7, sx + sr * 0.7, sy + sr * 0.7],
              fill=(255, 230, 140))
    # low headland silhouette, far left only; flat sea band
    d.polygon([(x, y + h * 0.52), (x + w * 0.20, y + h * 0.40),
               (x + w * 0.34, y + h * 0.52)], fill=(110, 130, 140))
    d.rectangle([x, y + h * 0.52, x + w, y + h * 0.62], fill=SEA)
    d.line([x, y + h * 0.52, x + w, y + h * 0.52], fill=(52, 92, 132),
           width=1)
    # table + delegates (heads in the sky band, above the sea)
    ty = y + h * 0.84
    d.polygon([(x + w * 0.05, ty), (x + w * 0.95, ty),
               (x + w * 0.89, y + h), (x + w * 0.11, y + h)],
              fill=(96, 62, 34))
    d.rectangle([x + w * 0.05, ty - 3, x + w * 0.95, ty], fill=(70, 44, 22))
    cols = [(178, 24, 32), (22, 38, 76), (44, 128, 74), (196, 116, 30),
            (104, 62, 140), (30, 128, 128), (150, 60, 90), (70, 90, 160),
            (120, 120, 40), (160, 90, 40), (60, 130, 110)]
    for i, c in enumerate(cols):
        person(x + w * (0.11 + 0.062 * i), ty - 2, h * 0.27, c)
    # the empty chair, cream-filled so it reads against the brown table
    ex = x + w * 0.90
    d.rectangle([ex - 8, ty - 30, ex + 8, ty - 2], fill=(243, 236, 216),
                outline=(52, 36, 20), width=3)
    d.line([ex - 8, ty - 16, ex + 8, ty - 16], fill=(52, 36, 20), width=2)
    # torn text sheet on the table
    d.polygon([(x + w * 0.44, ty + 3), (x + w * 0.56, ty + 3),
               (x + w * 0.545, y + h - 3), (x + w * 0.455, y + h - 3)],
              fill=(252, 250, 240))
    d.line([x + w * 0.50, ty + 5, x + w * 0.50, y + h - 5],
           fill=(178, 24, 32), width=2)


def scene_nato(x, y, w, h):
    """Council chamber: slate wall, white compass star, flags and
    saturated-suit delegates (contrast pass built in)."""
    d.rectangle([x, y, x + w, y + h], fill=(30, 50, 92))
    cx, cy, r = x + w * 0.50, y + h * 0.30, h * 0.26
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(255, 255, 255),
              width=3)
    d.polygon([(cx, cy - r * 0.95), (cx + r * 0.16, cy - r * 0.16),
               (cx + r * 0.95, cy), (cx + r * 0.16, cy + r * 0.16),
               (cx, cy + r * 0.95), (cx - r * 0.16, cy + r * 0.16),
               (cx - r * 0.95, cy), (cx - r * 0.16, cy - r * 0.16)],
              fill=(255, 255, 255))
    d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=(30, 50, 92))
    # Poland inset, left: outline + 3 red markers
    mx, my, mw, mh = x + w * 0.04, y + h * 0.08, w * 0.19, h * 0.36
    d.rectangle([mx, my, mx + mw, my + mh], fill=(17, 30, 60),
                outline=(120, 140, 180))
    d.polygon([(mx + 3, my + mh * 0.30), (mx + mw * 0.30, my + 3),
               (mx + mw - 3, my + mh * 0.25), (mx + mw * 0.85, my + mh * 0.55),
               (mx + mw * 0.60, my + mh - 3), (mx + mw * 0.25, my + mh * 0.80),
               (mx + 3, my + mh * 0.60)], fill=(72, 102, 142))
    for (px, py) in [(0.30, 0.35), (0.62, 0.55), (0.78, 0.30)]:
        d.ellipse([mx + mw * px - 2.5, my + mh * py - 2.5,
                   mx + mw * px + 2.5, my + mh * py + 2.5], fill=(230, 40, 48),
                  outline=(255, 255, 255))
    # table + flags + delegates in saturated suits with pale halos
    ty = y + h * 0.80
    d.polygon([(x + w * 0.04, ty), (x + w * 0.96, ty),
               (x + w * 0.90, y + h), (x + w * 0.10, y + h)],
              fill=(84, 56, 32))
    d.rectangle([x + w * 0.04, ty - 3, x + w * 0.96, ty], fill=(58, 38, 20))
    flag_cols = [(178, 24, 32), (255, 255, 255), (22, 38, 76),
                 (44, 128, 74), (196, 116, 30), (104, 62, 140),
                 (30, 128, 128), (150, 60, 90), (70, 90, 160),
                 (120, 120, 40)]
    for i, c in enumerate(flag_cols):
        fx = x + w * (0.10 + 0.082 * i)
        d.rectangle([fx, ty - 15, fx + 11, ty - 6], fill=c,
                    outline=(200, 200, 200))
    suits = [(178, 24, 32), (44, 128, 74), (196, 116, 30), (104, 62, 140),
             (30, 128, 128)]
    for i, c in enumerate(suits):
        fx = x + w * (0.16 + 0.17 * i)
        d.ellipse([fx - 8, ty - 2 - h * 0.26 - 3, fx + 8,
                   ty - 2 + 3], fill=(235, 232, 215, 120))
        person(fx, ty - 2, h * 0.26, c)


LEAD_SCENES = {"cop31": scene_cop31, "nato": scene_nato}


# ------------------------------------------------------- card mini-scenes
# Tiles are 126x36: bold iconic shapes only.
def mini_tanker(x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(26, 36, 64))
    d.rectangle([x, y + h * 0.68, x + w, y + h], fill=SEA)
    hx = x + w * 0.10
    d.polygon([(hx, y + h * 0.58), (hx + w * 0.68, y + h * 0.58),
               (hx + w * 0.58, y + h * 0.80), (hx + w * 0.06, y + h * 0.80)],
              fill=(28, 28, 32))
    d.rectangle([hx + w * 0.08, y + h * 0.38, hx + w * 0.30, y + h * 0.58],
                fill=(150, 60, 50))
    for fx in (0.52, 0.64):
        gx = hx + w * fx
        d.polygon([(gx - 5, y + h * 0.46), (gx, y + h * 0.16),
                   (gx + 5, y + h * 0.46)], fill=(240, 110, 36))
        d.polygon([(gx - 2.5, y + h * 0.46), (gx, y + h * 0.30),
                   (gx + 2.5, y + h * 0.46)], fill=(255, 190, 80))


def mini_gaza(x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(196, 178, 140))
    d.rectangle([x, y + h * 0.80, x + w, y + h], fill=(140, 124, 96))
    for (bx, bw, bh) in [(0.05, 0.22, 0.46), (0.31, 0.17, 0.62),
                         (0.52, 0.20, 0.38)]:
        d.rectangle([x + w * bx, y + h * (0.80 - bh), x + w * (bx + bw),
                     y + h * 0.80], fill=(126, 112, 88))
        d.rectangle([x + w * (bx + 0.04), y + h * (0.80 - bh + 0.08),
                     x + w * (bx + 0.09), y + h * (0.80 - bh + 0.20)],
                    fill=(60, 54, 46))
    tx, ty, ts = x + w * 0.84, y + h * 0.14, 11
    d.polygon([(tx, ty), (tx + ts, ty + ts * 0.95), (tx - ts, ty + ts * 0.95)],
              fill=(255, 196, 0), outline=(20, 20, 20))
    d.rectangle([tx - 1, ty + 4, tx + 1, ty + 8], fill=(20, 20, 20))
    d.ellipse([tx - 1, ty + 9, tx + 1, ty + 11], fill=(20, 20, 20))


def mini_cikande(x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(70, 62, 66))
    d.rectangle([x + w * 0.08, y + h * 0.44, x + w * 0.60, y + h * 0.88],
                fill=(52, 50, 56))
    d.rectangle([x + w * 0.70, y + h * 0.16, x + w * 0.78, y + h * 0.88],
                fill=(46, 44, 50))
    for fx in (0.16, 0.30, 0.44, 0.56):
        gx = x + w * fx
        d.polygon([(gx - 5, y + h * 0.44), (gx, y + h * 0.14),
                   (gx + 5, y + h * 0.44)], fill=(240, 110, 36))
        d.polygon([(gx - 2.5, y + h * 0.44), (gx, y + h * 0.26),
                   (gx + 2.5, y + h * 0.44)], fill=(255, 190, 80))
    d.rectangle([x + w * 0.16, y + h * 0.60, x + w * 0.24, y + h * 0.72],
                fill=(250, 196, 92))
    d.rectangle([x + w * 0.32, y + h * 0.60, x + w * 0.40, y + h * 0.72],
                fill=(250, 196, 92))


def mini_grok(x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(36, 40, 58))
    px, py, pw, ph = x + w * 0.14, y + h * 0.12, w * 0.26, h * 0.76
    d.rounded_rectangle([int(px), int(py), int(px + pw), int(py + ph)],
                        radius=4, fill=(16, 16, 20),
                        outline=(120, 124, 140))
    d.rectangle([px + 3, py + 5, px + pw - 3, py + ph - 5],
                fill=(168, 205, 226))
    d.ellipse([px + pw * 0.30, py + ph * 0.14, px + pw * 0.70,
               py + ph * 0.14 + pw * 0.40], fill=(240, 200, 170))
    cx, cy, r = px + pw * 0.5, py + ph * 0.5, 9
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(230, 40, 48),
              width=3)
    d.line([cx - r * 0.7, cy + r * 0.7, cx + r * 0.7, cy - r * 0.7],
           fill=(230, 40, 48), width=3)
    gx, gy = x + w * 0.58, y + h * 0.30
    d.rectangle([gx, gy, gx + w * 0.30, gy + 7], fill=(150, 108, 54))
    d.line([gx + w * 0.15, gy + 7, gx + w * 0.11, gy + h * 0.36],
           fill=(150, 108, 54), width=3)
    d.rectangle([x + w * 0.54, y + h * 0.72, x + w * 0.92, y + h * 0.80],
                fill=(150, 108, 54))


def mini_satellite(x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(8, 8, 18))
    for i in range(16):
        d.point((x + (i * 53) % int(w), y + (i * 29) % int(h)),
                fill=(225, 228, 240))
    d.ellipse([x - w * 0.3, y + h * 0.80, x + w * 1.3, y + h * 1.8],
              fill=(44, 96, 160))
    sx, sy = x + w * 0.52, y + h * 0.24
    d.rectangle([sx, sy, sx + 26, sy + 14], fill=(210, 214, 220))
    d.polygon([(sx - 24, sy + 1), (sx, sy + 1), (sx, sy + 13),
               (sx - 24, sy + 13)], fill=(44, 68, 140))
    d.polygon([(sx + 26, sy + 1), (sx + 50, sy + 1), (sx + 50, sy + 13),
               (sx + 26, sy + 13)], fill=(44, 68, 140))
    rx, ry, rr = x + w * 0.20, y + h * 0.42, 9
    d.ellipse([rx - rr, ry - rr, rx + rr, ry + rr], fill=(255, 206, 60))
    for a in (90, 210, 330):
        d.pieslice([rx - rr - 4, ry - rr - 4, rx + rr + 4, ry + rr + 4],
                   a - 28, a + 28, fill=(255, 206, 60))
    d.ellipse([rx - 2, ry - 2, rx + 2, ry + 2], fill=(8, 8, 18))


def mini_denmark(x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(0, 32, 91))
    cx, cy, r = x + w * 0.26, y + h * 0.50, h * 0.30
    for k in range(12):
        a = math.radians(k * 30 - 90)
        sx, sy = cx + r * math.cos(a), cy + r * math.sin(a)
        d.ellipse([sx - 1.8, sy - 1.8, sx + 1.8, sy + 1.8],
                  fill=(255, 204, 0))
    px, py, pw, ph = x + w * 0.56, y + h * 0.14, w * 0.32, h * 0.72
    d.rectangle([px, py, px + pw, py + ph], fill=(120, 20, 28),
                outline=(230, 200, 160))
    d.ellipse([px + pw * 0.32, py + ph * 0.12, px + pw * 0.68,
               py + ph * 0.12 + pw * 0.36], fill=(240, 200, 170))
    d.line([px + 3, py + 3, px + pw - 3, py + ph - 3],
           fill=(255, 60, 60), width=3)
    d.line([px + 3, py + ph - 3, px + pw - 3, py + 3],
           fill=(255, 60, 60), width=3)


def mini_dymer(x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(58, 66, 84))
    bx, by, bw, bh = x + w * 0.12, y + h * 0.26, w * 0.44, h * 0.60
    d.polygon([(bx, by + 6), (bx + bw * 0.25, by), (bx + bw * 0.45, by + 5),
               (bx + bw * 0.70, by + 1), (bx + bw, by + 7),
               (bx + bw, by + bh), (bx, by + bh)], fill=(150, 146, 138))
    for r in range(2):
        for cidx in range(3):
            d.rectangle([bx + 4 + cidx * (bw / 3.4),
                         by + 9 + r * (bh / 2.6),
                         bx + 4 + cidx * (bw / 3.4) + 6,
                         by + 9 + r * (bh / 2.6) + 6],
                        fill=(30, 28, 34) if (r + cidx) % 2 else (90, 86, 80))
    d.line([x + w * 0.78, y + h * 0.08, x + w * 0.78, y + h * 0.88],
           fill=(240, 200, 60), width=3)
    d.line([x + w * 0.78, y + h * 0.08, x + w * 0.96, y + h * 0.20],
           fill=(240, 200, 60), width=3)
    d.line([x + w * 0.94, y + h * 0.20, x + w * 0.94, y + h * 0.38],
           fill=(200, 200, 210), width=1)
    d.rectangle([x + w * 0.92, y + h * 0.38, x + w * 0.96, y + h * 0.45],
                fill=(200, 60, 60))


def mini_markets(x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(246, 244, 238))
    for gy in (0.33, 0.66):
        d.line([x + 3, y + h * gy, x + w - 3, y + h * gy],
               fill=(220, 216, 200), width=1)
    candles = [(0.08, 0.50, 0.68, (178, 24, 32)),
               (0.24, 0.44, 0.60, (178, 24, 32)),
               (0.40, 0.36, 0.52, (44, 128, 74)),
               (0.56, 0.28, 0.44, (44, 128, 74)),
               (0.72, 0.18, 0.34, (44, 128, 74))]
    for (cx0, top, bot, col) in candles:
        cx = x + w * cx0
        d.line([cx + 3, y + h * (top - 0.05), cx + 3, y + h * (bot + 0.05)],
               fill=col, width=1)
        d.rectangle([cx, y + h * top, cx + 7, y + h * bot], fill=col)
    d.line([x + w * 0.08, y + h * 0.60, x + w * 0.88, y + h * 0.14],
           fill=BURG, width=2)
    d.polygon([(x + w * 0.88, y + h * 0.14), (x + w * 0.79, y + h * 0.14),
               (x + w * 0.88, y + h * 0.24)], fill=BURG)


def mini_whitehouse(x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(168, 205, 226))
    d.rectangle([x, y + h * 0.80, x + w, y + h], fill=(86, 148, 74))
    bx, by, bw, bh = x + w * 0.20, y + h * 0.32, w * 0.56, h * 0.48
    d.rectangle([bx, by, bx + bw, by + bh], fill=(250, 250, 246),
                outline=(180, 180, 170))
    d.pieslice([bx + bw * 0.32, by - h * 0.22, bx + bw * 0.68, by + 1],
               180, 360, fill=(250, 250, 246), outline=(180, 180, 170))
    for i in range(4):
        cx = bx + bw * (0.14 + 0.22 * i)
        d.rectangle([cx, by + 4, cx + 4, by + bh - 4], fill=(210, 210, 200))
    dx, dy = x + w * 0.70, y + h * 0.52
    d.rectangle([dx, dy, dx + 20, dy + 15], fill=(252, 250, 240),
                outline=(150, 150, 150))
    d.ellipse([dx + 13, dy + 8, dx + 19, dy + 14], fill=BURG)


def mini_seoul(x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(168, 205, 226))
    tx = x + w * 0.50
    d.polygon([(tx - 11, y + h * 0.88), (tx - 4, y + h * 0.30),
               (tx + 4, y + h * 0.30), (tx + 11, y + h * 0.88)],
              fill=(120, 130, 140))
    d.ellipse([tx - 8, y + h * 0.20, tx + 8, y + h * 0.20 + 8],
              fill=(200, 60, 60))
    d.line([tx, y + h * 0.08, tx, y + h * 0.20], fill=(200, 60, 60),
           width=2)
    bx = x + 3
    for bw, bh in [(13, 0.34), (10, 0.46), (14, 0.30), (10, 0.40)]:
        d.rectangle([bx, y + h - h * bh - 2, bx + bw, y + h - 2],
                    fill=(70, 92, 118))
        bx += bw + 4
    sx, sy, sr = x + w * 0.85, y + h * 0.68, 6
    d.pieslice([sx - sr, sy - sr, sx + sr, sy + sr], 90, 270,
               fill=(178, 24, 32))
    d.pieslice([sx - sr, sy - sr, sx + sr, sy + sr], 270, 90,
               fill=(22, 38, 76))


CARD_SCENES = {"tanker": mini_tanker, "gaza": mini_gaza,
               "cikande": mini_cikande, "grok": mini_grok,
               "satellite": mini_satellite, "denmark": mini_denmark,
               "dymer": mini_dymer, "markets": mini_markets,
               "whitehouse": mini_whitehouse, "seoul": mini_seoul}


# ------------------------------------------------------------------ world map
# Dotted continents from lon/lat polygons (own simplified outlines),
# drawn on the map band's own navy-plum panel. Pins = the 13 pictured
# stories at their true lon/lat; crowded pins get a leader line.
def point_in_poly(lon, lat, poly):
    inside = False
    j = len(poly) - 1
    for i in range(len(poly)):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if ((yi > lat) != (yj > lat)) and \
           (lon < (xj - xi) * (lat - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside


CONTINENTS = [
    [(-168, 66), (-156, 71), (-140, 70), (-130, 71), (-125, 62), (-125, 48),
     (-124, 40), (-118, 34), (-110, 23), (-97, 16), (-87, 13), (-83, 9),
     (-79, 9), (-81, 15), (-85, 16), (-90, 18), (-95, 19), (-97, 26),
     (-90, 30), (-82, 31), (-76, 35), (-75, 40), (-70, 43), (-66, 45),
     (-60, 47), (-55, 52), (-65, 60), (-68, 58), (-72, 62), (-78, 62),
     (-90, 66), (-95, 69), (-110, 68), (-125, 70), (-140, 70),
     (-155, 71), (-168, 66)],
    [(-80, 10), (-79, 4), (-77, -4), (-81, -6), (-77, -12), (-71, -18),
     (-70, -23), (-70, -30), (-71, -35), (-73, -44), (-74, -50),
     (-70, -54), (-66, -55), (-66, -47), (-62, -41), (-58, -34),
     (-52, -32), (-48, -27), (-40, -22), (-35, -9), (-35, -6),
     (-41, -3), (-44, -2), (-50, 0), (-52, 4), (-57, 6), (-61, 9),
     (-65, 10), (-71, 12), (-75, 10), (-80, 10)],
    [(-10, 37), (-9, 43), (-2, 44), (-1, 46), (-4, 48), (0, 50),
     (2, 51), (5, 53), (7, 54), (8, 57), (10, 59), (5, 60), (5, 62),
     (10, 64), (12, 66), (18, 69), (25, 71), (31, 70), (40, 68),
     (44, 66), (42, 60), (40, 56), (38, 54), (40, 50), (35, 46),
     (31, 46), (30, 46), (28, 45), (23, 40), (19, 42), (13, 44),
     (8, 44), (3, 42), (0, 39), (-2, 37), (-6, 36), (-10, 37)],
    [(-6, 35), (0, 36), (10, 37), (11, 34), (19, 30), (20, 32),
     (25, 32), (30, 31), (32, 31), (35, 28), (39, 21), (43, 12),
     (48, 11), (51, 11), (56, 16), (58, 21), (55, 25), (52, 28),
     (48, 30), (44, 30), (38, 20), (35, 15), (33, 12), (32, 10),
     (30, 12), (26, 17), (21, 16), (15, 15), (12, 14), (9, 9),
     (9, 4), (6, 4), (3, 6), (-8, 4), (-13, 8), (-17, 12), (-17, 15),
     (-15, 20), (-15, 25), (-13, 28), (-10, 30), (-6, 35)],
    [(26, 38), (30, 36), (36, 36), (36, 30), (39, 27), (41, 29),
     (44, 29), (47, 30), (50, 29), (54, 26), (57, 26), (58, 24),
     (61, 25), (66, 25), (70, 22), (73, 20), (76, 10), (80, 8),
     (81, 9), (84, 19), (88, 22), (91, 22), (93, 17), (95, 16),
     (98, 8), (100, 6), (101, 3), (104, 2), (105, 9), (107, 11),
     (109, 15), (106, 21), (110, 20), (113, 22), (116, 23),
     (120, 25), (122, 31), (120, 35), (122, 38), (127, 40),
     (130, 42), (133, 43), (136, 44), (140, 47), (142, 50),
     (142, 54), (140, 59), (142, 60), (158, 59), (162, 60),
     (170, 66), (178, 65), (180, 66), (180, 62), (170, 60),
     (162, 60), (158, 53), (150, 59), (142, 54), (142, 48),
     (138, 44), (132, 43), (128, 40), (124, 39), (121, 36),
     (116, 36), (113, 30), (110, 24), (108, 18), (104, 8),
     (100, 13), (96, 16), (92, 21), (89, 22), (86, 20), (82, 16),
     (77, 8), (73, 16), (68, 23), (62, 25), (57, 25), (53, 26),
     (48, 30), (44, 29), (41, 29), (36, 36), (33, 39), (26, 41),
     (26, 38)],
    [(114, -22), (113, -26), (114, -32), (115, -34), (118, -35),
     (124, -33), (129, -32), (131, -32), (133, -34), (136, -35),
     (138, -35), (140, -38), (144, -38), (147, -38), (150, -37),
     (153, -32), (153, -28), (151, -24), (149, -20), (146, -19),
     (143, -15), (142, -11), (141, -13), (136, -12), (135, -15),
     (132, -11), (129, -15), (126, -14), (122, -17), (118, -20),
     (114, -22)],
    [(166, -45), (168, -46), (170, -45), (172, -43), (174, -41),
     (176, -39), (178, -37), (179, -38), (177, -40), (175, -42),
     (173, -44), (171, -46), (169, -47), (167, -47), (166, -45)],
    # New Zealand, widened so its dots survive the grid
    [(145, -41), (147, -41), (147, -43), (145, -44), (145, -41)],
    # Tasmania
]

PINS = [
    (1, 30.7, 36.9),    # Antalya
    (2, 4.35, 50.85),   # Brussels
    (3, 20.07, 32.12),  # Benghazi
    (4, 56.5, 26.6),    # Strait of Hormuz
    (5, 34.45, 31.5),   # Gaza
    (6, 106.4, -6.2),   # Cikande
    (7, -122.7, 45.5),  # Oregon
    (8, 37.6, 55.75),   # Moscow
    (9, 12.57, 55.68),  # Copenhagen
    (10, 30.2, 50.8),   # Dymer
    (11, -74.0, 40.7),  # New York
    (12, -77.04, 38.9),  # Washington DC
    (13, 126.98, 37.57),  # Seoul
]

MAP_LON = (-168.0, 192.0)
MAP_LAT = (78.0, -57.0)
PIN_OFFSETS = {1: (16, 5), 2: (-12, -8), 8: (10, -8), 11: (12, -10)}


def draw_map(mx, my, mw, mh):
    d.rectangle([mx, my, mx + mw, my + mh], fill=(24, 22, 40))
    cols, rows = 150, 30
    cw_, ch_ = mw / cols, mh / rows
    for r in range(rows):
        lat = MAP_LAT[0] + (r + 0.5) * (MAP_LAT[1] - MAP_LAT[0]) / rows
        for c in range(cols):
            lon = MAP_LON[0] + (c + 0.5) * (MAP_LON[1] - MAP_LON[0]) / cols
            if any(point_in_poly(lon, lat, poly) for poly in CONTINENTS):
                cx = mx + (c + 0.5) * cw_
                cy = my + (r + 0.5) * ch_
                d.ellipse([cx - 1.4, cy - 1.4, cx + 1.4, cy + 1.4],
                          fill=(240, 234, 208))
    for lat in (0, 23.5, -23.5):
        gy = my + (MAP_LAT[0] - lat) / (MAP_LAT[0] - MAP_LAT[1]) * mh
        d.line([mx, gy, mx + mw, gy], fill=(96, 96, 128), width=1)
    for num, lon, lat in PINS:
        px = mx + (lon - MAP_LON[0]) / (MAP_LON[1] - MAP_LON[0]) * mw
        py = my + (MAP_LAT[0] - lat) / (MAP_LAT[0] - MAP_LAT[1]) * mh
        ox, oy = PIN_OFFSETS.get(num, (0, 0))
        if (ox, oy) != (0, 0):
            d.line([px, py, px + ox, py + oy], fill=(255, 255, 255),
                   width=1)
            px, py = px + ox, py + oy
        d.ellipse([px - 6.5, py - 6.5, px + 6.5, py + 6.5], fill=BURG,
                  outline=(255, 255, 255), width=2)
        ns = str(num)
        f = F(SANS_BLACK, 8)
        d.text((px - tw(ns, f) / 2, py - 5), ns, font=f,
               fill=(255, 255, 255))


# ------------------------------------------------------------------ layout
def draw_scene_clipped(scene_fn, x, y, w, h):
    """Render a scene on its own layer and paste it — nothing a scene
    draws may spill past its box."""
    global d
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    old_d = d
    d = ImageDraw.Draw(layer, "RGBA")
    try:
        scene_fn(0, 0, w, h)
    finally:
        d = old_d
    img.paste(layer, (x, y), layer)


def masthead():
    d.rectangle([0, 0, W, 27], fill=INK)
    d.text((M, 7), "THE WORLD IN ONE DAY · LATE EXTRA", font=F(SANS_BOLD, 11),
           fill=(250, 246, 233))
    rt = "40 STORIES · EVERY ONE DATED MONDAY 23 NOVEMBER 2026"
    rf = F(SANS_BOLD, 11)
    d.text((W - M - tw(rt, rf), 7), rt, font=rf, fill=OCHRE)
    centre("Monday 23 November 2026", W / 2, 33,
           fit("Monday 23 November 2026", SERIF_BLACK, 54, CW), fill=BURG)
    # strap: ochre rules at 95 and 121, burgundy text between
    rule(M, M + CW, 95, fill=OCHRE, width=2)
    centre(STRAP, W / 2, 103, fit(STRAP, SERIF_IT, 15, CW), fill=BURG_DARK)
    rule(M, M + CW, 121, fill=OCHRE, width=1)
    # stat ticker: charcoal band, six stats in cream + ochre
    d.rectangle([M, 127, M + CW, 153], fill=CHAR)
    colw = CW / 6
    for i, (num, lab) in enumerate(STATS):
        cx = M + colw * i + colw / 2
        centre(num, cx, 129, fit(num, SANS_BLACK, 13, colw - 8), fill=OCHRE)
        lf = F(SANS_BOLD, 7)
        lines = wrap(lab, lf, colw - 8)
        for j, ln in enumerate(lines[:1]):
            centre(ln, cx, 144, lf, fill=(232, 228, 214))
        if len(lines) > 1:
            WARNINGS.append(f"stat label wraps: {lab!r}")


def hero():
    x, y, w = MAIN_X, 159, MAIN_W
    draw_scene_clipped(scene_libya, x, y, w, 140)
    d.rectangle([x, y, x + w, y + 140], outline=INK, width=1)
    chip(x + 8, y + 8, HERO["tag"], BURG, font_size=10)
    stat_chip_right(x, y, w, HERO["stat"])
    # source credit strip on the scene's bottom edge
    d.rectangle([x, y + 126, x + w, y + 140], fill=(12, 12, 16))
    d.text((x + 6, y + 129), HERO["source"], font=F(SANS_BOLD, 8),
           fill=(235, 232, 220))
    ky = y + 148
    badge(x, ky, HERO["num"])
    kicker_label(x + 21, ky + 1, HERO["kicker"], HERO["label"], 10)
    hy = text_block(x, ky + 18, HERO["headline"], F(SERIF_BOLD, 22), w, 25,
                    max_lines=1)
    by = text_block(x, hy + 2, HERO["body"], F(SANS, 10), w, 13.5,
                    fill=(40, 40, 44), max_lines=2)
    if by > 390:
        WARNINGS.append(f"hero text ends at {by} > 390")


def lead_pair():
    y = 394
    for i, lead in enumerate(LEADS):
        x = MAIN_X + i * 338
        w = 326
        draw_scene_clipped(LEAD_SCENES[lead["scene"]], x, y, w, 90)
        d.rectangle([x, y, x + w, y + 90], outline=INK, width=1)
        chip(x + 6, y + 6, lead["tag"], BURG, font_size=9)
        stat_chip_right(x, y, w, lead["stat"])
        d.rectangle([x, y + 78, x + w, y + 90], fill=(12, 12, 16))
        d.text((x + 5, y + 80), lead["source"], font=F(SANS_BOLD, 7),
               fill=(235, 232, 220))
        ky = y + 96
        badge(x, ky, lead["num"], size=13)
        kicker_label(x + 18, ky, lead["kicker"], lead["label"], 8)
        hy = text_block(x, ky + 15, lead["headline"], F(SERIF_BOLD, 15), w,
                        17, max_lines=2)
        by = text_block(x, hy + 1, lead["body"], F(SANS, 9), w, 11.5,
                        fill=(40, 40, 44), max_lines=2)
        if by > 566:
            WARNINGS.append(f"lead {lead['num']} text ends at {by} > 566")


def map_band():
    y = 574
    d.text((MAIN_X, y), "WHERE IT HAPPENED — THE DAY ON THE MAP",
           font=F(SANS_BLACK, 11), fill=BURG)
    hw = tw("WHERE IT HAPPENED — THE DAY ON THE MAP", F(SANS_BLACK, 11))
    d.text((MAIN_X + hw + 8, y + 2), "· 13 pictured stories pinned",
           font=F(SANS, 9), fill=GREY)
    draw_map(MAIN_X, y + 16, MAIN_W, 126)
    # region bar under the map
    by = y + 148
    total = sum(c for _, c, _ in REGIONS)
    assert total == 40, f"region tally {total} != 40"
    x = MAIN_X
    f = F(SANS_BOLD, 8)
    spans = {}
    for name, count, colour in REGIONS:
        w_ = MAIN_W * count / total
        d.rectangle([x, by, x + w_, by + 12], fill=colour)
        spans[name] = (x, x + w_)
        if name in ("AMERICAS", "EUROPE", "AFRICA"):
            centre(f"{name} {count}", x + w_ / 2, by + 2, f,
                   fill=(255, 255, 255))
        x += w_
    jx = (spans["ASIA-PACIFIC"][0] + spans["WORLD"][1]) / 2
    centre("ASIA-PACIFIC 6 · MIDEAST 3 · WORLD 2", jx, by + 15, f, fill=GREY)


def utc_strip():
    # Two rows of three: the main column is too narrow for one row.
    y = 748
    lw, _ = chip(MAIN_X, y, "THE DAY IN UTC", CHAR, font_size=9)
    f_t, f_s = F(SANS_BLACK, 10), F(SANS, 9)
    col_x = [MAIN_X + lw + 10, MAIN_X + lw + 196, MAIN_X + lw + 382]
    for row in range(2):
        ry = y + row * 15
        for col in range(3):
            t, s = UTC_STRIP[row * 3 + col]
            x = col_x[col] if row == 0 else col_x[col]
            if row == 1:
                x = col_x[col]
            d.text((x, ry + 1), t, font=f_t, fill=BURG)
            sx = x + tw(t, f_t) + 4
            d.text((sx, ry + 2), s, font=f_s, fill=INK)
            if sx + tw(s, f_s) > MAIN_X + MAIN_W:
                WARNINGS.append(f"UTC item overflows: {t} {s!r}")


def card(x, y, cnum, tag, stat, place, label, head, caption, source, scene):
    w = 126
    draw_scene_clipped(CARD_SCENES[scene], x, y, w, 36)
    d.rectangle([x, y, x + w, y + 36], outline=INK, width=1)
    chip(x + 4, y + 4, tag, BURG, font_size=7)
    sf = F(SANS_BOLD, 7)
    sw = tw(stat, sf) + 6
    d.rectangle([x + w - sw - 4, y + 4, x + w - 4, y + 4 + 11],
                fill=(255, 255, 255))
    d.text((x + w - sw - 1, y + 6), stat, font=sf, fill=INK)
    d.rectangle([x, y + 27, x + w, y + 36], fill=(12, 12, 16))
    d.text((x + 4, y + 29), source, font=F(SANS_BOLD, 6),
           fill=(235, 232, 220))
    ky = y + 40
    badge(x, ky, cnum, size=11)
    kf = F(SANS_BOLD, 7)
    d.text((x + 15, ky + 1), place, font=kf, fill=BURG)
    lx = x + 15 + tw(place, kf) + 3
    lc = BURG if label == "CLAIM" else GREEN
    d.ellipse([lx, ky + 3, lx + 5, ky + 8], fill=lc)
    d.text((lx + 7, ky + 1), label, font=kf, fill=lc)
    hy = text_block(x, ky + 12, head, F(SERIF_BOLD, 10), w, 11.5,
                    max_lines=2)
    text_block(x, hy + 1, caption, F(SANS, 7), w, 9, fill=GREY, max_lines=1)


def cards_grid():
    for j, c in enumerate(CARDS):
        row, col = divmod(j, 5)
        card(MAIN_X + col * 134, 782 + row * 91, *c)


def rail():
    # hairline separating rail from main column
    d.line([692, 159, 692, 1006], fill=CREAM_LINE, width=1)
    d.rectangle([RAIL_X, 159, RAIL_X + RAIL_W, 185], fill=BURG)
    d.text((RAIL_X + 8, 165), "THE WIRE — 27 MORE FROM MONDAY",
           font=F(SANS_BLACK, 11), fill=(250, 246, 233))
    nf, tf, gf = F(SANS_BOLD, 9), F(SANS, 9), F(SANS, 8)
    y = 193
    for (num, text, source, label) in BRIEFS:
        d.text((RAIL_X, y), f"{num}", font=nf, fill=BURG)
        tx = RAIL_X + 22
        max_w = RAIL_W - 22
        lines = wrap(text, tf, max_w)
        if len(lines) > 2:
            WARNINGS.append(f"brief {num} wraps to {len(lines)} lines")
            lines = lines[:2]
        for i, ln in enumerate(lines):
            d.text((tx, y + i * 11), ln, font=tf, fill=INK)
        suffix = ""
        if source or label:
            suffix = " (" + source + (f" · {label})" if label else ")") \
                if source else f" ({label})"
        if suffix:
            last = lines[-1]
            sx = tx + tw(last, tf) + 1
            if sx + tw(suffix, gf) <= RAIL_X + RAIL_W:
                d.text((sx, y + (len(lines) - 1) * 11), suffix, font=gf,
                       fill=GREY)
            else:
                WARNINGS.append(f"brief {num} suffix dropped (no room)")
        y += 29
    if y - 29 + 22 > 978:
        WARNINGS.append(f"rail briefs end at {y - 29 + 22} > 978")
    d.text((RAIL_X, 982),
           "Briefs are REPORTED unless tagged CLAIM or FORECAST.",
           font=F(SANS, 8), fill=GREY)
    d.text((RAIL_X, 993), "Sources are named beside every story.",
           font=F(SANS, 8), fill=GREY)


def date_check():
    y = 964
    d.rectangle([MAIN_X, y, MAIN_X + MAIN_W, 1006], outline=BURG, width=2)
    d.text((MAIN_X + 9, y + 5),
           "DATE CHECK — CHECKED, AND LEFT OUT ON PURPOSE",
           font=F(SANS_BLACK, 10), fill=BURG)
    text_block(MAIN_X + 9, y + 19, DATE_CHECK, F(SANS, 8), MAIN_W - 18, 10,
               fill=(40, 40, 44), max_lines=2)


def main():
    masthead()
    hero()
    lead_pair()
    map_band()
    utc_strip()
    cards_grid()
    rail()
    date_check()
    centre(FOOTER, MAIN_X + MAIN_W / 2, 1012,
           fit(FOOTER, SANS, 7, MAIN_W), fill=GREY)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "output")
    os.makedirs(out, exist_ok=True)
    img.save(os.path.join(out, "entry.png"))
    img.resize((300, 300), Image.LANCZOS).save(
        os.path.join(out, "preview-300.png"))
    for wn in WARNINGS:
        print("WARNING:", wn)
    print("wrote output/entry.png + output/preview-300.png")


if __name__ == "__main__":
    main()
