"""Advent calendar theme images: one per day, 1-31 December (advent01.png .. advent31.png).

Same layout as the weekday images (see make_calendar_images.py): a 32x22 dark background and a 12x12 pixel-art emblem in the bottom-right box left free by the text.
Sprites are ASCII maps: '.' is transparent and other characters index PALETTE (or a per-day override).
"""
import math

from make_calendar_images import EMBLEM_X, EMBLEM_Y, H, W, disc, gradient, plot, sprite

PALETTE = {
    "R": (220, 30, 30), "r": (130, 15, 15),
    "G": (40, 170, 60), "g": (20, 95, 35),
    "Y": (240, 200, 60), "y": (160, 120, 30),
    "W": (240, 240, 240), "w": (165, 165, 180),
    "K": (70, 70, 75),
    "B": (140, 85, 40), "b": (85, 50, 22),
    "O": (250, 140, 30), "P": (240, 120, 170),
    "U": (60, 120, 230), "u": (140, 190, 255),
    "S": (190, 195, 210), "s": (110, 115, 130),
    "F": (255, 235, 100), "f": (255, 140, 30),
    "C": (240, 220, 170), "T": (210, 160, 100),
    "V": (160, 70, 200),
}

NIGHT = ((0, 0, 25), (10, 15, 55))
RED = ((35, 0, 0), (90, 12, 10))
GREEN = ((0, 25, 10), (10, 60, 30))
PURPLE = ((15, 0, 35), (55, 20, 85))
TEAL = ((0, 25, 30), (10, 60, 55))
WARM = ((35, 12, 0), (85, 38, 10))

# day -> (title, background, sprite rows or drawing function, palette overrides)
ADVENT = {
    1: ("Behind Door Number One", GREEN, [
        "......bGG...",
        "......b.....",
        "..RRRRbRRR..",
        ".RRWRRRRRRR.",
        ".RWRRRRRRRR.",
        ".RRRRRRRRRr.",
        ".RRRRRRRRRr.",
        ".RRRRRRRRRr.",
        "..RRRRRRRr..",
        "..RRRRRRrr..",
        "...RRrRRr...",
        "............",
    ], {}),
    2: ("Fritters & Freedom", PURPLE, [
        "............",
        "...TTTTTT...",
        "..TPPPPPPT..",
        ".TPPUPPYPPT.",
        ".TPPP..PPPT.",
        ".TPY....PPT.",
        ".TPP....UPT.",
        ".TPPP..PPPT.",
        ".TPWPPPPGPT.",
        "..TPPPPPPT..",
        "...TTTTTT...",
        "............",
    ], {}),
    3: ("Roll the Dice", TEAL, [
        "............",
        ".wWWWWWWWWw.",
        ".WWWWWWWWWW.",
        ".WWKKWWKKWW.",
        ".WWKKWWKKWW.",
        ".WWWWKKWWWW.",
        ".WWWWKKWWWW.",
        ".WWKKWWKKWW.",
        ".WWKKWWKKWW.",
        ".WWWWWWWWWW.",
        ".wWWWWWWWWw.",
        "............",
    ], {"K": (10, 10, 10)}),
    4: ("Lights, Latkes & Wheat", NIGHT, [
        "............",
        "......F....F",
        "......f....f",
        "......W....W",
        "......W....W",
        ".yyyy.W.yyyW",
        ".YYYYYYYYYYY",
        "......Y.....",
        "......Y.....",
        "......Y.....",
        "....YYYYY...",
        "............",
    ], {}),
    5: ("Rattling Chains & Naughty Lists", RED, [
        "T..........T",
        "Ty........yT",
        ".Ty......yT.",
        "..TTBBBBTT..",
        "..BBBBBBBB..",
        ".BBFBBBBFBB.",
        ".BBBBBBBBBB.",
        ".BBWBBBBWBB.",
        "..BBRRRRBB..",
        "...BBRRBB...",
        "....BRRB....",
        ".....RR.....",
    ], {"B": (95, 60, 35), "R": (240, 40, 60)}),
    6: ("Boots Full of Treats", GREEN, [
        "...O.Y......",
        "..OOOYY.....",
        "..OOYYY.....",
        ".WWWWWWW....",
        ".WWWWWWW....",
        "..RRRRR.....",
        "..RRRRR.....",
        "..RRRRR.....",
        "..RRRRRRRR..",
        "..RRRRRRRRR.",
        "..rrrrrrrrr.",
        "............",
    ], {}),
    7: ("Spin to Win", NIGHT, [
        ".....ss.....",
        ".....ss.....",
        "..UUUUUUUU..",
        "..UUUUUUUU..",
        "..UUYYYYUU..",
        "..UUUUUYUU..",
        "..UUYYYYUU..",
        "..UUUUUUUU..",
        "...UUUUUU...",
        "....UUUU....",
        ".....UU.....",
        "............",
    ], {}),
    8: ("Under the Bodhi Tree", NIGHT, [
        "............",
        "..GGG..GGG..",
        ".GGGGgGGGGG.",
        ".GGGGgGGGGG.",
        ".GGGGgGGGGG.",
        "..GGGgGGGG..",
        "...GGgGGG...",
        "....GgGG....",
        ".....gG.....",
        ".....g......",
        ".....g......",
        "............",
    ], {}),
    9: ("Llama Drama & Winter Woollies", RED, [
        "............",
        "............",
        "CCCCCCCCCCCC",
        "TCCCCCCCCCCT",
        "CTCCCCCCCCTC",
        "CCTCCCCCCTCC",
        "CCCTCRRCTCCC",
        "CCCCTRRTCCCC",
        "CCCCCTTCCCCC",
        "CCCCCCCCCCCC",
        "CCCCCCCCCCCC",
        "............",
    ], {"R": (200, 20, 20)}),
    10: ("Stand Up & Cheer", PURPLE, [
        "............",
        "..........Y.",
        "........YYY.",
        "......YYYYY.",
        "..wwYYYYYYY.",
        ".wwwYYYYYYY.",
        ".wwwYYYYYYY.",
        "..wwYYYYYYY.",
        "...b..YYYYY.",
        "...b....YYY.",
        "..bb......Y.",
        "............",
    ], {}),
    11: ("King of the Mountain", NIGHT, [
        "............",
        ".....W......",
        "....WWW.....",
        "...WWWWW....",
        "...WsWWsW.W.",
        "..sSsSsSsWWW",
        "..SSSSSSSsWs",
        ".SSSsSSSSSSS",
        ".SSSSSSsSSSS",
        "SSsSSSSSSSsS",
        "SSSSSSSSSSSS",
        "gggggggggggg",
    ], {"S": (95, 100, 130), "s": (65, 70, 95)}),
    12: ("Fiesta of Roses", TEAL, [
        "............",
        "...RRRR.....",
        "..RrRRrR....",
        "..RRrrRR..O.",
        "..RrRRrR.OYO",
        "...RRRR...O.",
        ".....G....G.",
        "..GG.G...G..",
        "...GGG..G...",
        ".....G.G....",
        ".....GG.....",
        ".....G......",
    ], {}),
    13: ("Buns & Blazing Crowns", NIGHT, [
        "............",
        "............",
        ".F..F..F..F.",
        ".f..f..f..f.",
        ".W..W..W..W.",
        ".W..W..W..W.",
        ".W..W..W..W.",
        "GGgGGgGGgGGg",
        "gGRGgGRGgGRG",
        "GGgGGgGGgGGg",
        "............",
        "............",
    ], {}),
    14: ("Wishing on Shooting Stars", PURPLE, [
        "........Y...",
        "........Y...",
        ".....YYYYYYY",
        "......YYYYY.",
        ".......YYY..",
        "......YY.YY.",
        ".....WY...Y.",
        "....W.......",
        "...u........",
        "..u.........",
        ".U..........",
        "U...........",
    ], {}),
    15: ("Spill the Tea", GREEN, [
        "...w..w.....",
        "....w..w....",
        "...w..w.....",
        "............",
        ".RRRRRRR....",
        ".RWRRRRRRR..",
        ".RWRRRRR.R..",
        ".RRRRRRR.R..",
        ".RRRRRRRRR..",
        ".RRRRRRR....",
        "..RRRRR.....",
        "............",
    ], {}),
    16: ("Knock, Knock, Who's There?", PURPLE, [
        ".....P......",
        ".....P......",
        "U...OOO...G.",
        ".UU.OOO.GG..",
        "..OOOOOOOO..",
        "PPOOOOOOOOYY",
        "..OOOOOOOO..",
        ".GG.OOO.UU..",
        "G...OOO...U.",
        ".....Y......",
        ".....Y......",
        "............",
    ], {}),
    17: ("Hail Saturn, Flip the Rules!", TEAL, [
        ".....Y......",
        "....YYY.....",
        ".....R......",
        ".....RV.....",
        "....RVV.....",
        "....VVRR....",
        "...VRRRV....",
        "...RRVVV....",
        "..RVVVRR....",
        "..VVRRRRV...",
        ".WWWWWWWWW..",
        "............",
    ], {}),
    18: ("Ugly Sweaters & Global Journeys", RED, [
        "............",
        "...GGWWGG...",
        ".GGGGGGGGGG.",
        "GGGWGGGGWGGG",
        "GGRRRRRRRRGG",
        "GGWRWRWRWRGG",
        "GGRWRWRWRWGG",
        "GGRRRRRRRRGG",
        "GG.GYGGYG.GG",
        "WW.GGGGGG.WW",
        "...WWWWWW...",
        "............",
    ], {}),
    19: ("Old-School St. Nick", GREEN, [
        "...RRWW.....",
        "..WW..RR....",
        "..RR..WW....",
        "......RR....",
        "......WW....",
        "......RR....",
        "......WW....",
        "..OO..RR....",
        "yOOOOyWW....",
        "..OO..RR....",
        "......WW....",
        "............",
    ], {}),
    20: ("Sing It Loud", RED, [
        "............",
        "....YYYYYYY.",
        "....YYYYYYY.",
        "....Y.....Y.",
        "....Y.....Y.",
        "....Y.....Y.",
        "....Y.....Y.",
        "..YYY...YYY.",
        ".YYYY..YYYY.",
        ".YYY...YYY..",
        "............",
        "............",
    ], {}),
    21: ("Welcome Back, Sun!", NIGHT, [
        "............",
        "......F.....",
        "......f.....",
        "......W.....",
        "..GG.GW.....",
        "...GRRGG....",
        ".BBBBBBBBTT.",
        "BBbBBBBBTbbT",
        "BBBBbBBBTbTT",
        "BBBBBBbBTbbT",
        ".BBBBBBBBTT.",
        "............",
    ], {}),
    22: ("Sweet Soup & Solstice", RED, [
        "............",
        "............",
        "............",
        "..PP..WW.YY.",
        ".PPPPWWWWYY.",
        "UUUUUUUUUUUU",
        "UuUuUuUuUuUU",
        ".UUUUUUUUUU.",
        "..UUUUUUUU..",
        "....UUUU....",
        "...UUUUUU...",
        "............",
    ], {}),
    23: ("Air Your Grievances!", NIGHT, [
        ".....WS.....",
        ".....WS.....",
        ".....WS.....",
        ".....WS.....",
        ".....WS.....",
        ".....WS.....",
        ".....WS.....",
        ".....WS.....",
        ".....WS.....",
        "....sWSs....",
        "...ssSSss...",
        "..ssssssss..",
    ], {}),
    24: ("Book Flood & Midnight Magic", PURPLE, [
        "............",
        "............",
        "..CCC..CCC..",
        ".CwwwCCwwwC.",
        ".CCCCCCCCCC.",
        ".CwwwCCwwwC.",
        ".CCCCCCCCCC.",
        ".CwwCCCCwwC.",
        ".CCCCCCCCCC.",
        "RRRRRbbRRRRR",
        "............",
        "............",
    ], {"R": (180, 25, 25)}),
    25: ("Unwrap the Joy", GREEN, [
        "...Y....Y...",
        "..YYY..YYY..",
        "...YYYYYY...",
        "RRRRRYYRRRRR",
        "RRRRRYYRRRRR",
        "rrrrrYYrrrrr",
        ".RRRRYYRRRR.",
        ".RRRRYYRRRR.",
        ".RRRRYYRRRR.",
        ".RRRRYYRRRR.",
        ".RRRRYYRRRR.",
        ".rrrrYYrrrr.",
    ], {}),
    26: ("Leftovers & Unity", WARM, [
        ".....F......",
        ".....f......",
        ".....K......",
        "..RRRKGGG...",
        "..RRRKGGG...",
        "..RRRKGGG...",
        "..RRRKGGG...",
        "..RRRKGGG...",
        ".BBBBBBBBB..",
        "..b.....b...",
        ".bbbbbbbbb..",
        "............",
    ], {}),
    27: ("Make Your Own Rules", TEAL, [
        ".....g......",
        ".....R......",
        ".WWWWWWWWWW.",
        ".WWWWWWWWWW.",
        ".BBRBBBGBBB.",
        ".BGBBBYBBRB.",
        ".BBBRBBBGBB.",
        ".BYBBGBBBYB.",
        ".BBBBBBRBBB.",
        ".bbbbbbbbbb.",
        "............",
        "............",
    ], {"B": (110, 60, 25), "b": (70, 35, 12)}),
    28: ("Pranks & Teamwork", NIGHT, [
        "............",
        "............",
        "Y.........Y.",
        ".R.......V..",
        ".RR.....VV..",
        "..RR...VV...",
        "..RRRRVVV...",
        "..RRRRVVVV..",
        ".RRRRRVVVVV.",
        ".YYYYYYYYYY.",
        "............",
        "............",
    ], {}),
    29: ("Shop Local & Share", PURPLE, None, {}),   # clock, drawn below
    30: ("Bacon, Purpose & Big Plans", TEAL, None, {}),  # bacon, drawn below
    31: ("First-Footing, Bells & Confetti", NIGHT, None, {}),  # fireworks, drawn below
}


def _clock(img):
    cx, cy = EMBLEM_X + 5.5, EMBLEM_Y + 5.5
    disc(img, cx, cy, 5.8, PALETTE["Y"])
    disc(img, cx, cy, 4.7, PALETTE["W"])
    hand = (10, 10, 10)
    ox, oy = EMBLEM_X + 5, EMBLEM_Y + 5
    plot(img, [(ox, oy - d) for d in range(0, 5)], hand)            # minute hand to 12
    plot(img, [(ox - 1, oy - 1), (ox - 2, oy - 2)], hand)            # hour hand to ~11
    plot(img, [(ox + 1, oy + 1)], PALETTE["R"])                      # centre/second hand stub


def _bacon(img):
    for base in (EMBLEM_Y + 2, EMBLEM_Y + 7):
        for dx in range(12):
            y = base + round(math.sin(dx / 1.6 + base))
            x = EMBLEM_X + dx
            plot(img, [(x, y)], (190, 50, 45))
            plot(img, [(x, y + 1)], (245, 205, 175))
            plot(img, [(x, y + 2)], (160, 40, 35))


def _fireworks(img):
    bursts = [(EMBLEM_X + 4, EMBLEM_Y + 4, 4, PALETTE["Y"]), (EMBLEM_X + 9, EMBLEM_Y + 8, 3, PALETTE["P"]),
              (EMBLEM_X + 3, EMBLEM_Y + 10, 2, PALETTE["u"])]
    for cx, cy, r, color in bursts:
        pts = []
        for i in range(8):
            a = 2 * math.pi * i / 8
            for d in range(2, r + 1):
                pts.append((round(cx + d * math.cos(a)), round(cy + d * math.sin(a))))
        plot(img, pts, color)
        plot(img, [(cx, cy)], PALETTE["W"])


DRAWN = {29: _clock, 30: _bacon, 31: _fireworks}


def make_advent(day):
    _title, background, rows, overrides = ADVENT[day]
    img = gradient(*background)
    if rows is None:
        DRAWN[day](img)
    else:
        assert len(rows) == 12 and all(len(r) == 12 for r in rows), "advent %d sprite must be 12x12" % day
        sprite(img, rows, {**PALETTE, **overrides})
    return img


ADVENT_IMAGES = {"advent%02d.png" % day: (lambda d=day: make_advent(d)) for day in ADVENT}
