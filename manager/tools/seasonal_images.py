"""Seasonal and celebration calendar theme images: Easter, solstice/equinoxes and birthdays.

Same layout and sprite conventions as advent_images.py. Birthday cakes carry the person's
initial; add someone by adding an entry to BIRTHDAYS (and a 3x5 glyph to INITIALS if needed).
"""
from advent_images import GREEN, NIGHT, PALETTE, PURPLE, TEAL, WARM
from make_calendar_images import gradient, sprite

SPRITES = {
    "easter": (PURPLE, [
        "....PPPP....",
        "...PPPPPP...",
        "..PPWPPWPP..",
        "..PPPPPPPP..",
        ".YYYYYYYYYY.",
        ".UYUYUYUYUU.",
        ".YYYYYYYYYY.",
        ".GGGGGGGGGG.",
        ".GGWGGGWGGG.",
        "..GGGGGGGG..",
        "...GGGGGG...",
        "....GGGG....",
    ], {}),
    # Sunrise behind a Stonehenge trilithon.
    "summer_solstice": (WARM, [
        ".....OO.....",
        "....OYYO....",
        "...OYYYYO...",
        ".sSSSSSSSSs.",
        "..SSOYYOSS..",
        "..SS.OO.SS..",
        "..SS....SS..",
        "..SS....SS..",
        "..sS....sS..",
        "gGGGGGGGGGGg",
        "GGgGGGGgGGGG",
        "gggggggggggg",
    ], {"S": (150, 150, 165), "s": (95, 95, 110)}),
    # Daffodil.
    "spring_equinox": (TEAL, [
        ".....Y......",
        "..Y.YYY.Y...",
        "..YYYOYYY...",
        ".YYYOOOYYY..",
        "..YYYOYYY...",
        "..Y.YYY.Y...",
        ".....G......",
        ".....G...G..",
        ".G...G..G...",
        "..G..G.G....",
        "...G.GG.....",
        "....GG......",
    ], {}),
    # Maple leaf.
    "autumn_equinox": (NIGHT, [
        ".....O......",
        "....OOO.....",
        ".O..ORO..O..",
        ".OO.ORO.OO..",
        "OOOOOROOOOO.",
        ".OOOOROOOO..",
        "..OOOROOO...",
        ".OOOOROOOO..",
        "OOO..R..OOO.",
        ".....b......",
        ".....b......",
        "............",
    ], {"R": (170, 60, 15)}),
}

CAKE = [
    "............",
    "..F..F..F...",
    "..f..f..f...",
    "..U..P..Y...",
    "..U..P..Y...",
    ".WWWWWWWWWW.",
    ".CCCCCCCCCC.",
    ".CCCCCCCCCC.",
    ".CCCCCCCCCC.",
    ".CCCCCCCCCC.",
    ".PCPCPCPCPC.",
    "SSSSSSSSSSSS",
]
INITIAL_ORIGIN = (4, 6)  # top-left of the 3x5 initial within the cake sprite (rows 6-10)

INITIALS = {
    "J": ["..#", "..#", "..#", "#.#", ".#."],
    "K": ["#.#", "#.#", "##.", "#.#", "#.#"],
}

# image name -> (initial, background)
BIRTHDAYS = {
    "birthday_kevin": ("K", PURPLE),
    "birthday_jon": ("J", GREEN),
}


def _cake_with_initial(initial):
    rows = [list(r) for r in CAKE]
    ox, oy = INITIAL_ORIGIN
    for dy, line in enumerate(INITIALS[initial]):
        for dx, ch in enumerate(line):
            if ch == "#":
                rows[oy + dy][ox + dx] = "R"
    return ["".join(r) for r in rows]


def _make_sprite(background, rows, overrides):
    assert len(rows) == 12 and all(len(r) == 12 for r in rows), "sprite must be 12x12"
    img = gradient(*background)
    sprite(img, rows, {**PALETTE, **overrides})
    return img


SEASONAL_IMAGES = {
    "%s.png" % name: (lambda spec=spec: _make_sprite(*spec)) for name, spec in SPRITES.items()
}
SEASONAL_IMAGES.update({
    "%s.png" % name: (lambda i=initial, bg=bg: _make_sprite(bg, _cake_with_initial(i), {"R": (200, 20, 40)}))
    for name, (initial, bg) in BIRTHDAYS.items()
})
