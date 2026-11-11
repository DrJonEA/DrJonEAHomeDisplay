"""Midkemian calendar theme images (Raymond E. Feist's Riftwar world): festivals and month starts.

Same layout and sprite conventions as advent_images.py; dates are set in
calendar_themes/midkemia.json.
"""
from advent_images import GREEN, NIGHT, PALETTE, TEAL, WARM
from make_calendar_images import gradient, sprite

SUMMER = ((30, 15, 0), (70, 45, 10))

# image name -> (background, 12x12 sprite rows, palette overrides)
SPRITES = {
    "mk_banapis": (SUMMER, [  # Banapis: midsummer festival maypole
        ".....Y......",
        "....PbG.....",
        "...P.b.G....",
        "..R..b..U...",
        ".R...b...U..",
        "R....b....U.",
        ".....b......",
        ".....b......",
        ".....b......",
        ".....b......",
        "....bbb.....",
        "GgGGGGGgGGGG",
    ], {"b": (170, 120, 70)}),
    "mk_kimia": (SUMMER, [  # Kimia: high trade
        "............",
        "............",
        "......YYYY..",
        "......yyyy..",
        "......YYYY..",
        "..YYYYyyyy..",
        "..yyyyYYYY..",
        "..YYYYyyyy..",
        "..yyyyYYYY..",
        "..YYYYyyyy..",
        "..YYYYYYYY..",
        "............",
    ], {}),
    "mk_rodec": (SUMMER, [  # Rodec: late summer wheat
        "..Y.Y.Y.Y...",
        ".YY.YYYY.YY.",
        ".YYYYYYYYYY.",
        "..YyYYYYyY..",
        "...yyYYyy...",
        "....yyyy....",
        "....RRRR....",
        "....yyyy....",
        "...y.yy.y...",
        "..y..yy..y..",
        ".y...yy...y.",
        "............",
    ], {}),
    "mk_staphron": (WARM, [  # Staphron: early autumn acorn
        ".....b......",
        "..BBBBBBBB..",
        ".BbBbBbBbBB.",
        ".BBBBBBBBBB.",
        "..TTTTTTTT..",
        "..TTTTTTTT..",
        "..TTTTTTTT..",
        "...TTTTTT...",
        "...TTTTTT...",
        "....TTTT....",
        ".....TT.....",
        "............",
    ], {"T": (205, 155, 75), "b": (110, 70, 35)}),
    "mk_natinica": (WARM, [  # Natinica: harvest
        ".....g......",
        ".....gG.....",
        "..OOOOOOOO..",
        ".OfOOfOOfOO.",
        "OfOOOfOOOfOO",
        "OfOOOfOOOfOO",
        "OfOOOfOOOfOO",
        "OfOOOfOOOfOO",
        ".OfOOfOOfOO.",
        "..OOOOOOOO..",
        "............",
        "............",
    ], {"f": (190, 90, 10)}),
    "mk_wochem": (NIGHT, [  # Wochem: autumn leaves and first frost
        ".....W......",
        "....WBW.....",
        "...WBBBW....",
        ".WBBBbBBBW..",
        "..WBBbBBW...",
        ".WBBBbBBBW..",
        "..WBBbBBW...",
        ".WBBBbBBBW..",
        "..WBBbBBW...",
        "...WBbBW....",
        ".....b......",
        ".....b......",
    ], {"B": (205, 105, 40), "b": (120, 55, 20)}),
    "mk_midwinter": (NIGHT, [  # Mid-Winter Day: the festival fire
        "............",
        ".....F......",
        "....FF......",
        "....FYF.....",
        "...fFYFf....",
        "..fFYYYFf...",
        "..fFYWYFf...",
        "...fFYFf....",
        ".bB.fff.Bb..",
        "..bBbBbBb...",
        ".BBb...bBB..",
        "WWWWWWWWWWWW",
    ], {}),
    "mk_nuna": (NIGHT, [  # Nuna: deep winter
        ".....W......",
        "....WWW.....",
        "....GGG.....",
        "...WWGWW....",
        "...GGGGG....",
        "..WWGGGWW...",
        "..GGGGGGG...",
        ".WWGGGGGWW..",
        ".GGGGGGGGG..",
        ".....b......",
        ".....b......",
        "WWWWWWWWWWWW",
    ], {"G": (30, 120, 50), "b": (110, 70, 35)}),
    "mk_agaeis": (NIGHT, [  # Agaeis: the long freeze
        "WWWWWWWWWWWW",
        "uuuuuuuuuuuu",
        ".uu.uuu.uu.u",
        ".uu..uu..u.u",
        ".uu..u...u..",
        "..u..u...u..",
        "..u..u......",
        "..u.........",
        "..W..W......",
        ".........W..",
        "............",
        "............",
    ], {}),
    "mk_yamiev": (TEAL, [  # Yamiev: spring thaw snowdrop
        "....ggg.....",
        "...g...g....",
        "...g...gG...",
        "...g..WWW...",
        "...g..WWW...",
        "...g.W.W.W..",
        "...g........",
        "..gg........",
        ".gGg...gg...",
        "..Gg..gG....",
        "WWWgWWgWWWWW",
        "bbbbbbbbbbbb",
    ], {"g": (60, 150, 70), "G": (110, 200, 90), "b": (90, 60, 35)}),
    "mk_dzanin": (GREEN, [  # Dzanin: late spring blossom
        "............",
        "..PP........",
        ".PYPP...PP..",
        "..PPb..PYPP.",
        "....b...Pb..",
        ".....b..b...",
        "..PP..bb....",
        ".PYPP.b.....",
        "..PPbb......",
        "...b........",
        "..b.........",
        ".b..........",
    ], {"b": (150, 90, 50)}),
}


def make_midkemia(name):
    background, rows, overrides = SPRITES[name]
    assert len(rows) == 12 and all(len(r) == 12 for r in rows), "%s sprite must be 12x12" % name
    img = gradient(*background)
    sprite(img, rows, {**PALETTE, **overrides})
    return img


MIDKEMIA_IMAGES = {"%s.png" % name: (lambda n=name: make_midkemia(n)) for name in SPRITES}
