/*******************************************************************************
 * Size: 10 px
 * Bpp: 1
 * Opts: --bpp 1 --size 10 --no-compress --stride 1 --align 1 --font slkscr.ttf --range 32-127 --format lvgl -o SilkScreen10.c
 ******************************************************************************/

#ifdef __has_include
    #if __has_include("lvgl.h")
        #ifndef LV_LVGL_H_INCLUDE_SIMPLE
            #define LV_LVGL_H_INCLUDE_SIMPLE
        #endif
    #endif
#endif

#ifdef LV_LVGL_H_INCLUDE_SIMPLE
    #include "lvgl.h"
#else
    #include "lvgl/lvgl.h"
#endif



#ifndef SILKSCREEN10
#define SILKSCREEN10 1
#endif

#if SILKSCREEN10

/*-----------------
 *    BITMAPS
 *----------------*/

/*Store the image of the glyphs*/
static LV_ATTRIBUTE_LARGE_CONST const uint8_t glyph_bitmap[] = {
    /* U+0020 " " */
    0x0,

    /* U+0021 "!" */
    0xe4,

    /* U+0022 "\"" */
    0xb4,

    /* U+0023 "#" */
    0x4b, 0xb4, 0x92, 0xed, 0x20,

    /* U+0024 "$" */
    0x23, 0xe0, 0xc0, 0x7, 0xe8,

    /* U+0025 "%" */
    0xcb, 0x22, 0x0, 0x4d, 0x30,

    /* U+0026 "&" */
    0x23, 0xe0, 0xc0, 0x41, 0xe4,

    /* U+0027 "'" */
    0xc0,

    /* U+0028 "(" */
    0x6a, 0x10,

    /* U+0029 ")" */
    0x95, 0x20,

    /* U+002A "*" */
    0x22, 0x96, 0x88, 0xa4, 0x80,

    /* U+002B "+" */
    0x20, 0x8f, 0xc8, 0x20, 0x80,

    /* U+002C "," */
    0x60,

    /* U+002D "-" */
    0xf0,

    /* U+002E "." */
    0x80,

    /* U+002F "/" */
    0x25, 0x9, 0x0,

    /* U+0030 "0" */
    0x64, 0x63, 0x10, 0x30,

    /* U+0031 "1" */
    0xc4, 0x44, 0x4f,

    /* U+0032 "2" */
    0xe0, 0x58, 0x8, 0x7c,

    /* U+0033 "3" */
    0xe0, 0x58, 0x0, 0xf0,

    /* U+0034 "4" */
    0xaa, 0xaa, 0xf2,

    /* U+0035 "5" */
    0xfc, 0x3c, 0x3f, 0xf8,

    /* U+0036 "6" */
    0x68, 0xee, 0x96,

    /* U+0037 "7" */
    0xf1, 0x20, 0x44,

    /* U+0038 "8" */
    0x64, 0x58, 0x8, 0xb0,

    /* U+0039 "9" */
    0x64, 0xde, 0xf1, 0xb0,

    /* U+003A ":" */
    0xa0,

    /* U+003B ";" */
    0x41, 0x80,

    /* U+003C "<" */
    0x2a, 0x4, 0x40,

    /* U+003D "=" */
    0xf0, 0xf0,

    /* U+003E ">" */
    0x88, 0x85, 0x0,

    /* U+003F "?" */
    0xe0, 0x58, 0x0, 0x20,

    /* U+0040 "@" */
    0x7a, 0xdb, 0xae, 0x1, 0xe0,

    /* U+0041 "A" */
    0x74, 0x7f, 0x18, 0xc4,

    /* U+0042 "B" */
    0xf4, 0x7d, 0x8, 0xf8,

    /* U+0043 "C" */
    0x64, 0x61, 0x8, 0xb0,

    /* U+0044 "D" */
    0xf4, 0x63, 0x18, 0x78,

    /* U+0045 "E" */
    0xf3, 0xc9, 0xc0,

    /* U+0046 "F" */
    0xf3, 0xc9, 0x0,

    /* U+0047 "G" */
    0x7c, 0x2f, 0x10, 0x30,

    /* U+0048 "H" */
    0x8c, 0x7f, 0x18, 0xc4,

    /* U+0049 "I" */
    0xfc,

    /* U+004A "J" */
    0x8, 0x42, 0x18, 0xb0,

    /* U+004B "K" */
    0x8d, 0x31, 0xa, 0x44,

    /* U+004C "L" */
    0x92, 0x49, 0xc0,

    /* U+004D "M" */
    0x87, 0x3a, 0x61, 0x86, 0x10,

    /* U+004E "N" */
    0x87, 0x1a, 0x61, 0x8e, 0x10,

    /* U+004F "O" */
    0x64, 0x63, 0x10, 0x30,

    /* U+0050 "P" */
    0xf4, 0x7d, 0x8, 0x40,

    /* U+0051 "Q" */
    0x64, 0x63, 0x10, 0x30, 0x20,

    /* U+0052 "R" */
    0xe4, 0x79, 0xa, 0x44,

    /* U+0053 "S" */
    0x7c, 0x1c, 0xe0, 0xf8,

    /* U+0054 "T" */
    0xf4, 0x44, 0x44,

    /* U+0055 "U" */
    0x8c, 0x63, 0x18, 0xb0,

    /* U+0056 "V" */
    0x86, 0x10, 0x12, 0x48, 0x80,

    /* U+0057 "W" */
    0x86, 0x1a, 0x69, 0xa5, 0x20,

    /* U+0058 "X" */
    0x85, 0x22, 0x0, 0x4a, 0x10,

    /* U+0059 "Y" */
    0x85, 0x20, 0x8, 0x20, 0x80,

    /* U+005A "Z" */
    0xe5, 0x9, 0xc0,

    /* U+005B "[" */
    0xea, 0xb0,

    /* U+005C "\\" */
    0x91, 0x2, 0x40,

    /* U+005D "]" */
    0xd5, 0x70,

    /* U+005E "^" */
    0x54,

    /* U+005F "_" */
    0xf8,

    /* U+0060 "`" */
    0x90, 0x0,

    /* U+0061 "a" */
    0x74, 0x7f, 0x18, 0xc4,

    /* U+0062 "b" */
    0xf4, 0x7d, 0x8, 0xf8,

    /* U+0063 "c" */
    0x64, 0x61, 0x8, 0xb0,

    /* U+0064 "d" */
    0xf4, 0x63, 0x18, 0x78,

    /* U+0065 "e" */
    0xf3, 0xc9, 0xc0,

    /* U+0066 "f" */
    0xf3, 0xc9, 0x0,

    /* U+0067 "g" */
    0x7c, 0x2f, 0x10, 0x30,

    /* U+0068 "h" */
    0x8c, 0x7f, 0x18, 0xc4,

    /* U+0069 "i" */
    0xfc,

    /* U+006A "j" */
    0x8, 0x42, 0x18, 0xb0,

    /* U+006B "k" */
    0x8d, 0x31, 0xa, 0x44,

    /* U+006C "l" */
    0x92, 0x49, 0xc0,

    /* U+006D "m" */
    0x87, 0x3a, 0x61, 0x86, 0x10,

    /* U+006E "n" */
    0x87, 0x1a, 0x61, 0x8e, 0x10,

    /* U+006F "o" */
    0x64, 0x63, 0x10, 0x30,

    /* U+0070 "p" */
    0xf4, 0x7d, 0x8, 0x40,

    /* U+0071 "q" */
    0x64, 0x63, 0x10, 0x30, 0x20,

    /* U+0072 "r" */
    0xe4, 0x79, 0xa, 0x44,

    /* U+0073 "s" */
    0x7c, 0x1c, 0xe0, 0xf8,

    /* U+0074 "t" */
    0xf4, 0x44, 0x44,

    /* U+0075 "u" */
    0x8c, 0x63, 0x18, 0xb0,

    /* U+0076 "v" */
    0x86, 0x10, 0x12, 0x48, 0x80,

    /* U+0077 "w" */
    0x86, 0x1a, 0x69, 0xa5, 0x20,

    /* U+0078 "x" */
    0x85, 0x22, 0x0, 0x4a, 0x10,

    /* U+0079 "y" */
    0x85, 0x20, 0x8, 0x20, 0x80,

    /* U+007A "z" */
    0xe5, 0x9, 0xc0,

    /* U+007B "{" */
    0x6a, 0x4, 0xc0,

    /* U+007C "|" */
    0xff,

    /* U+007D "}" */
    0xc8, 0x85, 0x80,

    /* U+007E "~" */
    0x4d, 0x0
};


/*---------------------
 *  GLYPH DESCRIPTION
 *--------------------*/

static const lv_font_fmt_txt_glyph_dsc_t glyph_dsc[] = {
    {.bitmap_index = 0, .adv_w = 0, .box_w = 0, .box_h = 0, .ofs_x = 0, .ofs_y = 0} /* id = 0 reserved */,
    {.bitmap_index = 0, .adv_w = 76, .box_w = 1, .box_h = 1, .ofs_x = 0, .ofs_y = 0},
    {.bitmap_index = 1, .adv_w = 57, .box_w = 1, .box_h = 6, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 2, .adv_w = 95, .box_w = 3, .box_h = 2, .ofs_x = 1, .ofs_y = 4},
    {.bitmap_index = 3, .adv_w = 133, .box_w = 6, .box_h = 6, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 8, .adv_w = 114, .box_w = 5, .box_h = 8, .ofs_x = 1, .ofs_y = -1},
    {.bitmap_index = 13, .adv_w = 133, .box_w = 6, .box_h = 6, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 18, .adv_w = 114, .box_w = 5, .box_h = 8, .ofs_x = 1, .ofs_y = -1},
    {.bitmap_index = 23, .adv_w = 57, .box_w = 1, .box_h = 2, .ofs_x = 1, .ofs_y = 4},
    {.bitmap_index = 24, .adv_w = 76, .box_w = 2, .box_h = 6, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 26, .adv_w = 76, .box_w = 2, .box_h = 6, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 28, .adv_w = 133, .box_w = 6, .box_h = 6, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 33, .adv_w = 133, .box_w = 6, .box_h = 6, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 38, .adv_w = 57, .box_w = 2, .box_h = 2, .ofs_x = 0, .ofs_y = -1},
    {.bitmap_index = 39, .adv_w = 95, .box_w = 4, .box_h = 1, .ofs_x = 1, .ofs_y = 3},
    {.bitmap_index = 40, .adv_w = 38, .box_w = 1, .box_h = 1, .ofs_x = 0, .ofs_y = 0},
    {.bitmap_index = 41, .adv_w = 95, .box_w = 3, .box_h = 6, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 44, .adv_w = 114, .box_w = 5, .box_h = 6, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 48, .adv_w = 95, .box_w = 4, .box_h = 6, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 51, .adv_w = 114, .box_w = 5, .box_h = 6, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 55, .adv_w = 114, .box_w = 5, .box_h = 6, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 59, .adv_w = 114, .box_w = 4, .box_h = 6, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 62, .adv_w = 114, .box_w = 5, .box_h = 6, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 66, .adv_w = 114, .box_w = 4, .box_h = 6, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 69, .adv_w = 114, .box_w = 4, .box_h = 6, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 72, .adv_w = 114, .box_w = 5, .box_h = 6, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 76, .adv_w = 114, .box_w = 5, .box_h = 6, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 80, .adv_w = 38, .box_w = 1, .box_h = 3, .ofs_x = 0, .ofs_y = 1},
    {.bitmap_index = 81, .adv_w = 57, .box_w = 2, .box_h = 5, .ofs_x = 0, .ofs_y = 0},
    {.bitmap_index = 83, .adv_w = 95, .box_w = 3, .box_h = 6, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 86, .adv_w = 95, .box_w = 4, .box_h = 3, .ofs_x = 1, .ofs_y = 1},
    {.bitmap_index = 88, .adv_w = 95, .box_w = 3, .box_h = 6, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 91, .adv_w = 114, .box_w = 5, .box_h = 6, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 95, .adv_w = 133, .box_w = 6, .box_h = 6, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 100, .adv_w = 114, .box_w = 5, .box_h = 6, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 104, .adv_w = 114, .box_w = 5, .box_h = 6, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 108, .adv_w = 114, .box_w = 5, .box_h = 6, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 112, .adv_w = 114, .box_w = 5, .box_h = 6, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 116, .adv_w = 95, .box_w = 3, .box_h = 6, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 119, .adv_w = 95, .box_w = 3, .box_h = 6, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 122, .adv_w = 114, .box_w = 5, .box_h = 6, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 126, .adv_w = 114, .box_w = 5, .box_h = 6, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 130, .adv_w = 57, .box_w = 1, .box_h = 6, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 131, .adv_w = 114, .box_w = 5, .box_h = 6, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 135, .adv_w = 114, .box_w = 5, .box_h = 6, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 139, .adv_w = 95, .box_w = 3, .box_h = 6, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 142, .adv_w = 133, .box_w = 6, .box_h = 6, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 147, .adv_w = 133, .box_w = 6, .box_h = 6, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 152, .adv_w = 114, .box_w = 5, .box_h = 6, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 156, .adv_w = 114, .box_w = 5, .box_h = 6, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 160, .adv_w = 114, .box_w = 5, .box_h = 7, .ofs_x = 1, .ofs_y = -1},
    {.bitmap_index = 165, .adv_w = 114, .box_w = 5, .box_h = 6, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 169, .adv_w = 114, .box_w = 5, .box_h = 6, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 173, .adv_w = 95, .box_w = 4, .box_h = 6, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 176, .adv_w = 114, .box_w = 5, .box_h = 6, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 180, .adv_w = 133, .box_w = 6, .box_h = 6, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 185, .adv_w = 133, .box_w = 6, .box_h = 6, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 190, .adv_w = 133, .box_w = 6, .box_h = 6, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 195, .adv_w = 133, .box_w = 6, .box_h = 6, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 200, .adv_w = 95, .box_w = 3, .box_h = 6, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 203, .adv_w = 76, .box_w = 2, .box_h = 6, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 205, .adv_w = 95, .box_w = 3, .box_h = 6, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 208, .adv_w = 76, .box_w = 2, .box_h = 6, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 210, .adv_w = 95, .box_w = 3, .box_h = 2, .ofs_x = 1, .ofs_y = 4},
    {.bitmap_index = 211, .adv_w = 114, .box_w = 5, .box_h = 1, .ofs_x = 1, .ofs_y = -1},
    {.bitmap_index = 212, .adv_w = 76, .box_w = 2, .box_h = 6, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 214, .adv_w = 114, .box_w = 5, .box_h = 6, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 218, .adv_w = 114, .box_w = 5, .box_h = 6, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 222, .adv_w = 114, .box_w = 5, .box_h = 6, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 226, .adv_w = 114, .box_w = 5, .box_h = 6, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 230, .adv_w = 95, .box_w = 3, .box_h = 6, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 233, .adv_w = 95, .box_w = 3, .box_h = 6, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 236, .adv_w = 114, .box_w = 5, .box_h = 6, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 240, .adv_w = 114, .box_w = 5, .box_h = 6, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 244, .adv_w = 57, .box_w = 1, .box_h = 6, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 245, .adv_w = 114, .box_w = 5, .box_h = 6, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 249, .adv_w = 114, .box_w = 5, .box_h = 6, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 253, .adv_w = 95, .box_w = 3, .box_h = 6, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 256, .adv_w = 133, .box_w = 6, .box_h = 6, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 261, .adv_w = 133, .box_w = 6, .box_h = 6, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 266, .adv_w = 114, .box_w = 5, .box_h = 6, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 270, .adv_w = 114, .box_w = 5, .box_h = 6, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 274, .adv_w = 114, .box_w = 5, .box_h = 7, .ofs_x = 1, .ofs_y = -1},
    {.bitmap_index = 279, .adv_w = 114, .box_w = 5, .box_h = 6, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 283, .adv_w = 114, .box_w = 5, .box_h = 6, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 287, .adv_w = 95, .box_w = 4, .box_h = 6, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 290, .adv_w = 114, .box_w = 5, .box_h = 6, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 294, .adv_w = 133, .box_w = 6, .box_h = 6, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 299, .adv_w = 133, .box_w = 6, .box_h = 6, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 304, .adv_w = 133, .box_w = 6, .box_h = 6, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 309, .adv_w = 133, .box_w = 6, .box_h = 6, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 314, .adv_w = 95, .box_w = 3, .box_h = 6, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 317, .adv_w = 95, .box_w = 3, .box_h = 6, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 320, .adv_w = 57, .box_w = 1, .box_h = 8, .ofs_x = 1, .ofs_y = -1},
    {.bitmap_index = 321, .adv_w = 95, .box_w = 3, .box_h = 6, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 324, .adv_w = 114, .box_w = 5, .box_h = 2, .ofs_x = 1, .ofs_y = 4}
};

/*---------------------
 *  CHARACTER MAPPING
 *--------------------*/



/*Collect the unicode lists and glyph_id offsets*/
static const lv_font_fmt_txt_cmap_t cmaps[] =
{
    {
        .range_start = 32, .range_length = 95, .glyph_id_start = 1,
        .unicode_list = NULL, .glyph_id_ofs_list = NULL, .list_length = 0, .type = LV_FONT_FMT_TXT_CMAP_FORMAT0_TINY
    }
};



/*--------------------
 *  ALL CUSTOM DATA
 *--------------------*/

#if LVGL_VERSION_MAJOR == 8
/*Store all the custom data of the font*/
static  lv_font_fmt_txt_glyph_cache_t cache;
#endif

#if LVGL_VERSION_MAJOR >= 8
static const lv_font_fmt_txt_dsc_t font_dsc = {
#else
static lv_font_fmt_txt_dsc_t font_dsc = {
#endif
    .glyph_bitmap = glyph_bitmap,
    .glyph_dsc = glyph_dsc,
    .cmaps = cmaps,
    .kern_dsc = NULL,
    .kern_scale = 0,
    .cmap_num = 1,
    .bpp = 1,
    .kern_classes = 0,
    .bitmap_format = 0,
#if LVGL_VERSION_MAJOR == 8
    .cache = &cache
#endif

};

extern const lv_font_t lv_font_montserrat_12;


/*-----------------
 *  PUBLIC FONT
 *----------------*/

/*Initialize a public general font descriptor*/
#if LVGL_VERSION_MAJOR >= 8
const lv_font_t SilkScreen10 = {
#else
lv_font_t SilkScreen10 = {
#endif
    .get_glyph_dsc = lv_font_get_glyph_dsc_fmt_txt,    /*Function pointer to get glyph's data*/
    .get_glyph_bitmap = lv_font_get_bitmap_fmt_txt,    /*Function pointer to get glyph's bitmap*/
    .line_height = 8,          /*The maximum line height required by the font*/
    .base_line = 1,             /*Baseline measured from the bottom of the line*/
#if !(LVGL_VERSION_MAJOR == 6 && LVGL_VERSION_MINOR == 0)
    .subpx = LV_FONT_SUBPX_NONE,
#endif
#if LV_VERSION_CHECK(7, 4, 0) || LVGL_VERSION_MAJOR >= 8
    .underline_position = -1,
    .underline_thickness = 0,
#endif
    .static_bitmap = 0,
    .dsc = &font_dsc,          /*The custom font data. Will be accessed by `get_glyph_bitmap/dsc` */
#if LV_VERSION_CHECK(8, 2, 0) || LVGL_VERSION_MAJOR >= 9
    .fallback = &lv_font_montserrat_12,
#endif
    .user_data = NULL,
};



#endif /*#if SILKSCREEN10*/
