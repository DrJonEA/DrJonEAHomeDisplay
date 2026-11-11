"""Marvel theme images: MCU in-universe dates and Marvel character/universe debut days.

Same layout and sprite conventions as advent_images.py; dates are set in
calendar_themes/marvel.json.
"""
from advent_images import NIGHT, PALETTE, PURPLE, WARM
from make_calendar_images import gradient, sprite

SPACE = ((10, 0, 25), (40, 10, 60))

MARVEL_PALETTE = {**PALETTE, "K": (12, 12, 15)}

# image name -> (background, 12x12 sprite rows, palette overrides)
SPRITES = {
    "marvel_winter_soldier": (NIGHT, [  # the metal arm with the red star
        "..SSSSSSS...",
        ".SSSSRSSSS..",
        ".SSSRRRSSS..",
        ".SRRRRRRRS..",
        ".SSRRRRRSS..",
        ".SSRRSRRSS..",
        ".SSSSSSSSS..",
        "..sSsSsSs...",
        "..SsSsSsS...",
        "..sSsSsSs...",
        "...SSSSS....",
        "...S.S.S....",
    ], {}),
    "marvel_accords": (PURPLE, [  # signing the Sokovia Accords
        "............",
        ".CCCCCCC....",
        ".CwwwwwC....",
        ".CCCCCCC....",
        ".CwwwwwC...Y",
        ".CCCCCCC..Y.",
        ".CwwwwCC.Y..",
        ".CCCCCCCK...",
        ".CCCCCCC....",
        ".CUUCUCC....",
        ".CCCCCCC....",
        "............",
    ], {}),
    "marvel_snap": (SPACE, [  # the Infinity Gauntlet
        ".Y.Y.Y.Y....",
        ".Y.Y.Y.Y....",
        ".YYYYYYY....",
        ".YVYUYRY.YY.",
        ".YYYYYYYYYY.",
        ".YYYYOYYYY..",
        ".YYYYYYYY...",
        ".YYYGYYYY...",
        "..YYYYYY....",
        "..yyyyyy....",
        "..YYYYYY....",
        "..yyyyyy....",
    ], {}),
    "marvel_hulk_snap": (NIGHT, [  # the nano gauntlet on Hulk's arm
        ".R.R.R.R....",
        ".R.R.R.R....",
        ".RRRRRRR....",
        ".RVRUROR.RR.",
        ".RRRRRRRRRR.",
        ".RRRRGRRRR..",
        ".RRRRRRRR...",
        "..YYYYYY....",
        "..GGGGGG....",
        "..GgGGgG....",
        "..GGGGGG....",
        "..GgGGGG....",
    ], {"R": (190, 30, 30)}),
    "marvel_human_torch": (NIGHT, [  # Golden Age: the original Human Torch
        ".....F......",
        "....fFf.....",
        "...fFYFf....",
        "....FYF.....",
        ".f.fFFFf.f..",
        "..fFFYFFf...",
        "...fFYFf....",
        "....FFF.....",
        "...fF.Ff....",
        "..fF...Ff...",
        ".fF.....Ff..",
        "............",
    ], {}),
    "marvel_daredevil": (NIGHT, [  # the horned red cowl
        "..R......R..",
        "..RR....RR..",
        "..RRRRRRRR..",
        ".RRRRRRRRRR.",
        ".RRKKRRKKRR.",
        ".RRRRRRRRRR.",
        ".RRRRRRRRRR.",
        "..RCCCCCCR..",
        "..RCCCCCCR..",
        "...CCrrCC...",
        "....CCCC....",
        "............",
    ], {"R": (175, 20, 20), "K": (70, 0, 0)}),
    "marvel_iron_man": (NIGHT, [  # the helmet
        "...RRRRRR...",
        "..RRRRRRRR..",
        ".RRYYYYYYRR.",
        ".RYYYYYYYYR.",
        ".RYWWYYWWYR.",
        ".RYYYYYYYYR.",
        ".RYYYYYYYYR.",
        ".RRYyyyyYRR.",
        "..RYYYYYYR..",
        "..RRYYYYRR..",
        "...RRRRRR...",
        "............",
    ], {"R": (190, 25, 25)}),
    "marvel_xmen": (PURPLE, [  # the X
        "....KKKK....",
        "..KKYYYYKK..",
        ".KRRYYYYRRK.",
        ".KYRRYYRRYK.",
        "KYYYRRRRYYYK",
        "KYYYYRRYYYYK",
        "KYYYYRRYYYYK",
        "KYYYRRRRYYYK",
        ".KYRRYYRRYK.",
        ".KRRYYYYRRK.",
        "..KKYYYYKK..",
        "....KKKK....",
    ], {}),
    "marvel_spider": (NIGHT, [  # the spider on its thread
        ".....w......",
        ".....w......",
        ".....w......",
        "..R..w..R...",
        "...R.R.R....",
        "R..RRRRR..R.",
        ".RRRUUURRR..",
        "...RUUUR....",
        ".RRRUUURRR..",
        "R..RRRRR..R.",
        "...R...R....",
        "..R.....R...",
    ], {}),
    "marvel_comics_1": (PURPLE, [  # Marvel Comics #1
        "............",
        ".YYYYYYYYYY.",
        ".YRRRRRRRRY.",
        ".YYYYYYYYYY.",
        ".YUUUWWUUUY.",
        ".YUUWWWUUUY.",
        ".YUUUWWUUUY.",
        ".YUUUWWUUUY.",
        ".YUUUWWUUUY.",
        ".YUUWWWWUUY.",
        ".YYYYYYYYYY.",
        "............",
    ], {}),
    "marvel_fantastic_four": (WARM, [  # the 4
        "....WWWW....",
        "..WWUUUUWW..",
        ".WUUUUWWUUW.",
        ".WUUUWWWUUW.",
        "WUUUWWUWUUUW",
        "WUUWWUUWUUUW",
        "WUUWWWWWWUUW",
        "WUUUUUUWUUUW",
        ".WUUUUUWUUW.",
        ".WUUUUUWUUW.",
        "..WWUUUUWW..",
        "....WWWW....",
    ], {}),
}


def make_marvel(name):
    background, rows, overrides = SPRITES[name]
    assert len(rows) == 12 and all(len(r) == 12 for r in rows), "%s sprite must be 12x12" % name
    img = gradient(*background)
    sprite(img, rows, {**MARVEL_PALETTE, **overrides})
    return img


MARVEL_IMAGES = {"%s.png" % name: (lambda n=name: make_marvel(n)) for name in SPRITES}
