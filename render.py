#!/usr/bin/env python3
"""Render the front page for news-image-20261127.

Draws "THE WORLD IN ONE DAY - FRIDAY - 27 NOVEMBER 2026", a newspaper
front page summing up the world news of Friday 27 November 2026, as a
1024x1024 PNG. Pure Pillow + DejaVu fonts; fully deterministic: the
same run always produces byte-identical output.

Usage: python3 render.py <output-path>
"""

import sys

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------- fonts
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

_font_cache = {}


def font(path, size):
    key = (path, size)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(path, size)
    return _font_cache[key]


# ---------------------------------------------------------------- palette
PAPER = (247, 243, 233)
INK = (18, 16, 12)
RED = (140, 26, 20)
GREY = (92, 86, 74)
FAINT = (150, 143, 126)
SKY = (43, 58, 74)
SKY_LIGHT = (74, 94, 112)
GROUND = (24, 24, 26)
CREAM = (238, 230, 210)
GOLD = (198, 152, 52)
BALLOON_RED = (158, 44, 36)

W = 1024
H = 1024
MARGIN = 48
RIGHT = W - MARGIN
COL_W = (RIGHT - MARGIN - 36) // 2


# ---------------------------------------------------------------- helpers
def fit_size(draw, path, text, max_width, start):
    """Largest font size <= start at which text fits max_width."""
    size = start
    while size > 8:
        if draw.textlength(text, font=font(path, size)) <= max_width:
            return size
        size -= 2
    return size


def centered(draw, y, text, fnt, fill=INK, tracking=0):
    if tracking:
        widths = [draw.textlength(ch, font=fnt) for ch in text]
        total = sum(widths) + tracking * (len(text) - 1)
        x = (W - total) / 2
        for ch, w in zip(text, widths):
            draw.text((x, y), ch, font=fnt, fill=fill)
            x += w + tracking
        return
    w = draw.textlength(text, font=fnt)
    draw.text(((W - w) / 2, y), text, font=fnt, fill=fill)


def draw_tracked(draw, x, y, text, fnt, fill, tracking):
    for ch in text:
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += draw.textlength(ch, font=fnt) + tracking
    return x


def wrap(draw, text, fnt, max_width):
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if draw.textlength(trial, font=fnt) <= max_width:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def hrule(draw, y, width=2, fill=INK, x0=MARGIN, x1=RIGHT):
    draw.rectangle([x0, y, x1, y + width - 1], fill=fill)


# ---------------------------------------------------------------- artwork
def draw_lead_art(draw, x0, y0, x1, y1):
    """The grounded parade balloons under a nor'easter sky."""
    draw.rectangle([x0, y0, x1, y1], fill=SKY)
    draw.rectangle([x0, y0, x1, y0 + 22], fill=SKY_LIGHT)

    # diagonal rain streaks, kept inside the panel
    for rx in range(x0 + 6, x1 - 16, 34):
        for ry in range(y0 + 8, y1 - 46, 40):
            sx = rx + ry // 4
            if sx > x1 - 14:
                continue
            draw.line([sx, ry, sx - 9, ry + 15],
                      fill=(168, 186, 200), width=2)

    base = y1 - 32
    # skyline silhouette
    heights = [36, 50, 28, 56, 38, 46, 30, 52, 34, 42]
    step = (x1 - x0) // 10
    for i, bh in enumerate(heights):
        bx = x0 + i * step + 2
        draw.rectangle([bx, base - bh, bx + step - 6, base], fill=(30, 40, 52))
        for wy in range(base - bh + 7, base - 9, 13):
            for wx in range(bx + 6, bx + step - 12, 15):
                if (wx * 7 + wy * 13) % 5 == 0:
                    draw.rectangle([wx, wy, wx + 5, wy + 6], fill=GOLD)

    # ground, with the caption set into it
    draw.rectangle([x0, base, x1, y1], fill=GROUND)
    draw.rectangle([x0, base, x1, base + 3], fill=(90, 96, 104))
    cap = ("Grounded: the great balloons of the 100th Macy's Parade stay "
           "earthbound as the storm lashes the East Coast.")
    cf = font(SANS, 15)
    cw = draw.textlength(cap, font=cf)
    draw.text((x0 + (x1 - x0 - cw) / 2, base + 9), cap, font=cf, fill=CREAM)

    # three balloons, held low against the wind, fully inside the panel
    balloons = [
        (x0 + 170, 33, BALLOON_RED),
        (x0 + 450, 37, CREAM),
        (x0 + 720, 30, GOLD),
    ]
    for cx, r, colour in balloons:
        cy = base - r - 12
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=colour)
        draw.polygon([(cx - r // 3, cy + r - 4), (cx + r // 3, cy + r - 4),
                      (cx, cy + r + 10)], fill=colour)
        for dx in (-11, 0, 11):
            draw.line([cx + dx // 2, cy + r + 8, cx + dx, base - 2],
                      fill=(210, 210, 205), width=2)

    draw.rectangle([x0, y0, x1, y1], outline=INK, width=3)


# ---------------------------------------------------------------- stories
STORIES = [
    ("MARKETS", "Trump Tariffs Rattle Asian Markets",
     "Shares slide in Tokyo, Seoul and Shanghai as the new US levies "
     "land; exporters brace."),
    ("CAIRO - EGYPT", "Tanker Fire Kills 31 in Cairo",
     "A fuel-tanker blaze tears through a depot on the city's edge; "
     "the injured fill hospitals."),
    ("BANGKOK - THAILAND", "Blast Rocks Bangkok Refinery",
     "An explosion sends a plume over the capital; nearby residents "
     "are ordered to leave."),
    ("WELLINGTON - NEW ZEALAND", "Final Count Decides 67 of 131 Seats",
     "The last ballots are tallied in Wellington, settling the new "
     "parliament's shape."),
]


def draw_story(draw, x, y, kicker, headline, summary):
    kf = font(SANS_B, 18)
    draw_tracked(draw, x, y, kicker, kf, RED, 2)
    hf = font(SERIF_B, 26)
    yy = y + 26
    for line in wrap(draw, headline, hf, COL_W):
        draw.text((x, yy), line, font=hf, fill=INK)
        yy += 30
    sf = font(SANS, 18)
    yy += 2
    for line in wrap(draw, summary, sf, COL_W):
        draw.text((x, yy), line, font=sf, fill=(40, 37, 31))
        yy += 22
    return yy


# ---------------------------------------------------------------- page
def render(path):
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)

    # --- masthead ------------------------------------------------------
    hrule(draw, 26, 2)
    hrule(draw, 32, 1)
    title = "THE WORLD IN ONE DAY"
    ts = fit_size(draw, SERIF_B, title, RIGHT - MARGIN, 88)
    centered(draw, 40, title, font(SERIF_B, ts))
    hrule(draw, 140, 1)

    # --- date line ------------------------------------------------------
    centered(draw, 152, "FRIDAY \u2022 27 NOVEMBER 2026",
             font(SANS_B, 25), tracking=1)
    small = font(SANS, 16)
    draw.text((MARGIN, 158), "DAILY EDITION", font=small, fill=GREY)
    right_txt = "No. 27"
    draw.text((RIGHT - draw.textlength(right_txt, font=small), 158),
              right_txt, font=small, fill=GREY)
    hrule(draw, 190, 6)

    # --- lead story ------------------------------------------------------
    y = 208
    draw_tracked(draw, MARGIN, y, "UNITED STATES \u2014 STORM & TRAVEL",
                 font(SANS_B, 20), RED, 2)
    y += 30
    lead_lines = ["Nor'easter Grounds the", "100th Macy's Parade"]
    ls = min(fit_size(draw, SERIF_B, line, RIGHT - MARGIN, 62)
             for line in lead_lines)
    lf = font(SERIF_B, ls)
    for line in lead_lines:
        draw.text((MARGIN, y), line, font=lf, fill=INK)
        y += ls + 3
    y += 4
    deck = ("First postponement in the parade's history, as the storm cuts "
            "power to more than 500,000 homes \u2014 with 80 million "
            "travelers on the move.")
    deck_f = font(SERIF, 24)
    for line in wrap(draw, deck, deck_f, RIGHT - MARGIN):
        draw.text((MARGIN, y), line, font=deck_f, fill=(40, 37, 31))
        y += 30
    y += 8

    # --- lead art ---------------------------------------------------------
    draw_lead_art(draw, MARGIN, y, RIGHT, y + 140)
    y += 140 + 12
    hrule(draw, y, 2)
    y += 12

    # --- around the world ---------------------------------------------------
    draw_tracked(draw, MARGIN, y, "AROUND THE WORLD",
                 font(SANS_B, 19), INK, 3)
    y += 30
    col_x = [MARGIN, MARGIN + COL_W + 36]
    grid_top = y
    for row in range(2):
        ends = [draw_story(draw, col_x[col], y, *STORIES[row * 2 + col])
                for col in range(2)]
        y = max(ends) + 12
        if row == 0:
            hrule(draw, y - 6, 1, fill=FAINT)
    grid_bottom = y - 12
    mid_x = MARGIN + COL_W + 18
    draw.line([mid_x, grid_top, mid_x, grid_bottom], fill=FAINT, width=1)
    y += 4

    # --- bottom strip ---------------------------------------------------------
    strip_h = 80
    draw.rectangle([MARGIN, y, RIGHT, y + strip_h], fill=INK)
    draw_tracked(draw, MARGIN + 20, y + 9, "ALSO IN TODAY'S NEWS",
                 font(SANS_B, 17), GOLD, 2)
    credit = "Compiled from the day's reports"
    credit_f = font(SANS, 14)
    draw.text((RIGHT - 20 - draw.textlength(credit, font=credit_f), y + 11),
              credit, font=credit_f, fill=(178, 170, 152))
    strip_f = font(SANS_B, 18)
    draw.text((MARGIN + 20, y + 33),
              "EU agrees \u20ac1.6 trillion budget, with funding for Ukraine",
              font=strip_f, fill=CREAM)
    draw.text((MARGIN + 20, y + 56),
              "SPORT: Sinner out of Australian Open  \u2022  CRICKET: "
              "Sooryavanshi smashes 204 off 53 balls",
              font=font(SANS_B, 17), fill=CREAM)
    y += strip_h

    assert y <= H - 8, f"layout overflow: content ends at y={y}"
    img.save(path, format="PNG", optimize=True)
    return y


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "entry.png"
    end_y = render(out)
    print("wrote", out, "- content ends at y =", end_y)
