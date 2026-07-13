/*******************************************************************************
 * Size: 12 px
 * Bpp: 1
 * Opts: --bpp 1 --size 12 --no-compress --stride 1 --align 1 --font slkscr.ttf --range 32-127 --format lvgl -o SilkScreen12.c
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



#ifndef SILKSCREEN12
#define SILKSCREEN12 1
#endif

#if SILKSCREEN12

/*-----------------
 *    BITMAPS
 *----------------*/

/*Store the image of the glyphs*/
static LV_ATTRIBUTE_LARGE_CONST const uint8_t glyph_bitmap[] = {
    /* U+0020 " " */
    0x0,

    /* U+0021 "!" */
    0xf2,

    /* U+0022 "\"" */
    0x99, 0x90,

    /* U+0023 "#" */
    0x24, 0x4a, 0xd9, 0x2b, 0x64, 0x89, 0x0,

    /* U+0024 "$" */
    0x10, 0xf0, 0x20, 0x30, 0x10, 0x7f, 0x20,

    /* U+0025 "%" */
    0xe4, 0xe4, 0xe4, 0x10, 0x27, 0x27, 0x27,

    /* U+0026 "&" */
    0x13, 0xc1, 0x7, 0x40, 0xf, 0x10,

    /* U+0027 "'" */
    0xe0,

    /* U+0028 "(" */
    0x32, 0x48, 0x8,

    /* U+0029 ")" */
    0x84, 0x92, 0x20,

    /* U+002A "*" */
    0x10, 0x22, 0x49, 0xa9, 0x22, 0x4, 0x0,

    /* U+002B "+" */
    0x10, 0x20, 0x47, 0xf1, 0x2, 0x4, 0x0,

    /* U+002C "," */
    0x30,

    /* U+002D "-" */
    0xf0,

    /* U+002E "." */
    0x80,

    /* U+002F "/" */
    0x8, 0x42, 0x48, 0x42, 0x0,

    /* U+0030 "0" */
    0x72, 0x18, 0x61, 0x84, 0x7, 0x0,

    /* U+0031 "1" */
    0xe2, 0x22, 0x22, 0xf0,

    /* U+0032 "2" */
    0xf0, 0x0, 0x5c, 0x82, 0xf, 0xc0,

    /* U+0033 "3" */
    0xf0, 0x0, 0x5c, 0x4, 0xf, 0x0,

    /* U+0034 "4" */
    0x94, 0xa5, 0x2f, 0x88, 0x40,

    /* U+0035 "5" */
    0xfe, 0x8, 0x3e, 0xf, 0xef, 0x80,

    /* U+0036 "6" */
    0x3b, 0xf, 0xbe, 0xc7, 0x3, 0x80,

    /* U+0037 "7" */
    0xfc, 0x10, 0x44, 0x41, 0x4, 0x0,

    /* U+0038 "8" */
    0x70, 0x8, 0x5c, 0x84, 0x7, 0x0,

    /* U+0039 "9" */
    0x70, 0x38, 0xdf, 0x7c, 0x37, 0x0,

    /* U+003A ":" */
    0x90,

    /* U+003B ";" */
    0x20, 0x88,

    /* U+003C "<" */
    0x8, 0x9, 0x2, 0x0, 0x20,

    /* U+003D "=" */
    0xf0, 0xf,

    /* U+003E ">" */
    0x80, 0x8, 0x12, 0x2, 0x0,

    /* U+003F "?" */
    0xf8, 0x0, 0x4e, 0x0, 0x2, 0x0,

    /* U+0040 "@" */
    0x7d, 0x36, 0x74, 0xe8, 0x0, 0xf, 0x0,

    /* U+0041 "A" */
    0x73, 0xa3, 0xf8, 0xc6, 0x20,

    /* U+0042 "B" */
    0xfa, 0x8, 0x7e, 0x86, 0xf, 0x80,

    /* U+0043 "C" */
    0x70, 0x8, 0x60, 0x84, 0x7, 0x0,

    /* U+0044 "D" */
    0xfa, 0x18, 0x61, 0x86, 0xf, 0x80,

    /* U+0045 "E" */
    0xf8, 0x8f, 0x88, 0xf0,

    /* U+0046 "F" */
    0xf8, 0x8f, 0x88, 0x80,

    /* U+0047 "G" */
    0x7e, 0x8, 0x2f, 0x84, 0x7, 0x0,

    /* U+0048 "H" */
    0x86, 0x18, 0x7f, 0x86, 0x18, 0x40,

    /* U+0049 "I" */
    0xfe,

    /* U+004A "J" */
    0x4, 0x10, 0x41, 0x84, 0x7, 0x0,

    /* U+004B "K" */
    0x86, 0x9, 0x38, 0x92, 0x8, 0x40,

    /* U+004C "L" */
    0x88, 0x88, 0x88, 0xf0,

    /* U+004D "M" */
    0x83, 0x6, 0x9c, 0x98, 0x30, 0x60, 0x80,

    /* U+004E "N" */
    0x83, 0x6, 0x8c, 0x98, 0x70, 0x60, 0x80,

    /* U+004F "O" */
    0x72, 0x18, 0x61, 0x84, 0x7, 0x0,

    /* U+0050 "P" */
    0xfa, 0x8, 0x7e, 0x82, 0x8, 0x0,

    /* U+0051 "Q" */
    0x72, 0x18, 0x61, 0x84, 0x7, 0x1,

    /* U+0052 "R" */
    0xf2, 0x8, 0x7c, 0x92, 0x8, 0x40,

    /* U+0053 "S" */
    0x3c, 0x8, 0x1e, 0x4, 0xf, 0x0,

    /* U+0054 "T" */
    0xf2, 0x22, 0x22, 0x20,

    /* U+0055 "U" */
    0x86, 0x18, 0x61, 0x84, 0x7, 0x0,

    /* U+0056 "V" */
    0x83, 0x6, 0x9, 0x22, 0x44, 0x84, 0x0,

    /* U+0057 "W" */
    0x83, 0x26, 0x4c, 0x99, 0x20, 0x9, 0x0,

    /* U+0058 "X" */
    0x82, 0x0, 0x90, 0x82, 0x40, 0x20, 0x80,

    /* U+0059 "Y" */
    0x82, 0x0, 0x90, 0x81, 0x2, 0x4, 0x0,

    /* U+005A "Z" */
    0xf8, 0x42, 0x48, 0x43, 0xe0,

    /* U+005B "[" */
    0xea, 0xac,

    /* U+005C "\\" */
    0x84, 0x20, 0x40, 0x84, 0x20,

    /* U+005D "]" */
    0xd5, 0x5c,

    /* U+005E "^" */
    0x20, 0x22,

    /* U+005F "_" */
    0xfc,

    /* U+0060 "`" */
    0x80, 0x80, 0x0,

    /* U+0061 "a" */
    0x73, 0xa3, 0xf8, 0xc6, 0x20,

    /* U+0062 "b" */
    0xfa, 0x8, 0x7e, 0x86, 0xf, 0x80,

    /* U+0063 "c" */
    0x70, 0x8, 0x60, 0x84, 0x7, 0x0,

    /* U+0064 "d" */
    0xfa, 0x18, 0x61, 0x86, 0xf, 0x80,

    /* U+0065 "e" */
    0xf8, 0x8f, 0x88, 0xf0,

    /* U+0066 "f" */
    0xf8, 0x8f, 0x88, 0x80,

    /* U+0067 "g" */
    0x7e, 0x8, 0x2f, 0x84, 0x7, 0x0,

    /* U+0068 "h" */
    0x86, 0x18, 0x7f, 0x86, 0x18, 0x40,

    /* U+0069 "i" */
    0xfe,

    /* U+006A "j" */
    0x4, 0x10, 0x41, 0x84, 0x7, 0x0,

    /* U+006B "k" */
    0x86, 0x9, 0x38, 0x92, 0x8, 0x40,

    /* U+006C "l" */
    0x88, 0x88, 0x88, 0xf0,

    /* U+006D "m" */
    0x83, 0x6, 0x9c, 0x98, 0x30, 0x60, 0x80,

    /* U+006E "n" */
    0x83, 0x6, 0x8c, 0x98, 0x70, 0x60, 0x80,

    /* U+006F "o" */
    0x72, 0x18, 0x61, 0x84, 0x7, 0x0,

    /* U+0070 "p" */
    0xfa, 0x8, 0x7e, 0x82, 0x8, 0x0,

    /* U+0071 "q" */
    0x72, 0x18, 0x61, 0x84, 0x7, 0x1,

    /* U+0072 "r" */
    0xf2, 0x8, 0x7c, 0x92, 0x8, 0x40,

    /* U+0073 "s" */
    0x3c, 0x8, 0x1e, 0x4, 0xf, 0x0,

    /* U+0074 "t" */
    0xf2, 0x22, 0x22, 0x20,

    /* U+0075 "u" */
    0x86, 0x18, 0x61, 0x84, 0x7, 0x0,

    /* U+0076 "v" */
    0x83, 0x6, 0x9, 0x22, 0x44, 0x84, 0x0,

    /* U+0077 "w" */
    0x83, 0x26, 0x4c, 0x99, 0x20, 0x9, 0x0,

    /* U+0078 "x" */
    0x82, 0x0, 0x90, 0x82, 0x40, 0x20, 0x80,

    /* U+0079 "y" */
    0x82, 0x0, 0x90, 0x81, 0x2, 0x4, 0x0,

    /* U+007A "z" */
    0xf8, 0x42, 0x48, 0x43, 0xe0,

    /* U+007B "{" */
    0x32, 0x28, 0x22, 0x30,

    /* U+007C "|" */
    0xff, 0xc0,

    /* U+007D "}" */
    0xc4, 0x41, 0x44, 0xc0,

    /* U+007E "~" */
    0x24, 0x9, 0x0
};


/*---------------------
 *  GLYPH DESCRIPTION
 *--------------------*/

static const lv_font_fmt_txt_glyph_dsc_t glyph_dsc[] = {
    {.bitmap_index = 0, .adv_w = 0, .box_w = 0, .box_h = 0, .ofs_x = 0, .ofs_y = 0} /* id = 0 reserved */,
    {.bitmap_index = 0, .adv_w = 91, .box_w = 1, .box_h = 1, .ofs_x = 0, .ofs_y = 0},
    {.bitmap_index = 1, .adv_w = 69, .box_w = 1, .box_h = 7, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 2, .adv_w = 114, .box_w = 4, .box_h = 3, .ofs_x = 1, .ofs_y = 4},
    {.bitmap_index = 4, .adv_w = 160, .box_w = 7, .box_h = 7, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 11, .adv_w = 137, .box_w = 6, .box_h = 9, .ofs_x = 1, .ofs_y = -1},
    {.bitmap_index = 18, .adv_w = 160, .box_w = 8, .box_h = 7, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 25, .adv_w = 137, .box_w = 5, .box_h = 9, .ofs_x = 1, .ofs_y = -1},
    {.bitmap_index = 31, .adv_w = 69, .box_w = 1, .box_h = 3, .ofs_x = 1, .ofs_y = 4},
    {.bitmap_index = 32, .adv_w = 91, .box_w = 3, .box_h = 7, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 35, .adv_w = 91, .box_w = 3, .box_h = 7, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 38, .adv_w = 160, .box_w = 7, .box_h = 7, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 45, .adv_w = 160, .box_w = 7, .box_h = 7, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 52, .adv_w = 69, .box_w = 3, .box_h = 2, .ofs_x = 0, .ofs_y = -1},
    {.bitmap_index = 53, .adv_w = 114, .box_w = 4, .box_h = 1, .ofs_x = 1, .ofs_y = 3},
    {.bitmap_index = 54, .adv_w = 46, .box_w = 1, .box_h = 1, .ofs_x = 0, .ofs_y = 0},
    {.bitmap_index = 55, .adv_w = 114, .box_w = 5, .box_h = 7, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 60, .adv_w = 137, .box_w = 6, .box_h = 7, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 66, .adv_w = 114, .box_w = 4, .box_h = 7, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 70, .adv_w = 137, .box_w = 6, .box_h = 7, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 76, .adv_w = 137, .box_w = 6, .box_h = 7, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 82, .adv_w = 137, .box_w = 5, .box_h = 7, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 87, .adv_w = 137, .box_w = 6, .box_h = 7, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 93, .adv_w = 137, .box_w = 6, .box_h = 7, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 99, .adv_w = 137, .box_w = 6, .box_h = 7, .ofs_x = 2, .ofs_y = 0},
    {.bitmap_index = 105, .adv_w = 137, .box_w = 6, .box_h = 7, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 111, .adv_w = 137, .box_w = 6, .box_h = 7, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 117, .adv_w = 46, .box_w = 1, .box_h = 4, .ofs_x = 0, .ofs_y = 2},
    {.bitmap_index = 118, .adv_w = 69, .box_w = 3, .box_h = 5, .ofs_x = 0, .ofs_y = 0},
    {.bitmap_index = 120, .adv_w = 114, .box_w = 5, .box_h = 7, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 125, .adv_w = 114, .box_w = 4, .box_h = 4, .ofs_x = 1, .ofs_y = 2},
    {.bitmap_index = 127, .adv_w = 114, .box_w = 5, .box_h = 7, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 132, .adv_w = 137, .box_w = 6, .box_h = 7, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 138, .adv_w = 160, .box_w = 7, .box_h = 7, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 145, .adv_w = 137, .box_w = 5, .box_h = 7, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 150, .adv_w = 137, .box_w = 6, .box_h = 7, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 156, .adv_w = 137, .box_w = 6, .box_h = 7, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 162, .adv_w = 137, .box_w = 6, .box_h = 7, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 168, .adv_w = 114, .box_w = 4, .box_h = 7, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 172, .adv_w = 114, .box_w = 4, .box_h = 7, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 176, .adv_w = 137, .box_w = 6, .box_h = 7, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 182, .adv_w = 137, .box_w = 6, .box_h = 7, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 188, .adv_w = 69, .box_w = 1, .box_h = 7, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 189, .adv_w = 137, .box_w = 6, .box_h = 7, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 195, .adv_w = 137, .box_w = 6, .box_h = 7, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 201, .adv_w = 114, .box_w = 4, .box_h = 7, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 205, .adv_w = 160, .box_w = 7, .box_h = 7, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 212, .adv_w = 160, .box_w = 7, .box_h = 7, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 219, .adv_w = 137, .box_w = 6, .box_h = 7, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 225, .adv_w = 137, .box_w = 6, .box_h = 7, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 231, .adv_w = 137, .box_w = 6, .box_h = 8, .ofs_x = 1, .ofs_y = -1},
    {.bitmap_index = 237, .adv_w = 137, .box_w = 6, .box_h = 7, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 243, .adv_w = 137, .box_w = 6, .box_h = 7, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 249, .adv_w = 114, .box_w = 4, .box_h = 7, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 253, .adv_w = 137, .box_w = 6, .box_h = 7, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 259, .adv_w = 160, .box_w = 7, .box_h = 7, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 266, .adv_w = 160, .box_w = 7, .box_h = 7, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 273, .adv_w = 160, .box_w = 7, .box_h = 7, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 280, .adv_w = 160, .box_w = 7, .box_h = 7, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 287, .adv_w = 114, .box_w = 5, .box_h = 7, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 292, .adv_w = 91, .box_w = 2, .box_h = 7, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 294, .adv_w = 114, .box_w = 5, .box_h = 7, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 299, .adv_w = 91, .box_w = 2, .box_h = 7, .ofs_x = 2, .ofs_y = 0},
    {.bitmap_index = 301, .adv_w = 114, .box_w = 5, .box_h = 3, .ofs_x = 1, .ofs_y = 4},
    {.bitmap_index = 303, .adv_w = 137, .box_w = 6, .box_h = 1, .ofs_x = 1, .ofs_y = -1},
    {.bitmap_index = 304, .adv_w = 91, .box_w = 3, .box_h = 7, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 307, .adv_w = 137, .box_w = 5, .box_h = 7, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 312, .adv_w = 137, .box_w = 6, .box_h = 7, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 318, .adv_w = 137, .box_w = 6, .box_h = 7, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 324, .adv_w = 137, .box_w = 6, .box_h = 7, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 330, .adv_w = 114, .box_w = 4, .box_h = 7, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 334, .adv_w = 114, .box_w = 4, .box_h = 7, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 338, .adv_w = 137, .box_w = 6, .box_h = 7, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 344, .adv_w = 137, .box_w = 6, .box_h = 7, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 350, .adv_w = 69, .box_w = 1, .box_h = 7, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 351, .adv_w = 137, .box_w = 6, .box_h = 7, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 357, .adv_w = 137, .box_w = 6, .box_h = 7, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 363, .adv_w = 114, .box_w = 4, .box_h = 7, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 367, .adv_w = 160, .box_w = 7, .box_h = 7, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 374, .adv_w = 160, .box_w = 7, .box_h = 7, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 381, .adv_w = 137, .box_w = 6, .box_h = 7, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 387, .adv_w = 137, .box_w = 6, .box_h = 7, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 393, .adv_w = 137, .box_w = 6, .box_h = 8, .ofs_x = 1, .ofs_y = -1},
    {.bitmap_index = 399, .adv_w = 137, .box_w = 6, .box_h = 7, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 405, .adv_w = 137, .box_w = 6, .box_h = 7, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 411, .adv_w = 114, .box_w = 4, .box_h = 7, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 415, .adv_w = 137, .box_w = 6, .box_h = 7, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 421, .adv_w = 160, .box_w = 7, .box_h = 7, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 428, .adv_w = 160, .box_w = 7, .box_h = 7, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 435, .adv_w = 160, .box_w = 7, .box_h = 7, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 442, .adv_w = 160, .box_w = 7, .box_h = 7, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 449, .adv_w = 114, .box_w = 5, .box_h = 7, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 454, .adv_w = 114, .box_w = 4, .box_h = 7, .ofs_x = 1, .ofs_y = 0},
    {.bitmap_index = 458, .adv_w = 69, .box_w = 1, .box_h = 10, .ofs_x = 1, .ofs_y = -1},
    {.bitmap_index = 460, .adv_w = 114, .box_w = 4, .box_h = 7, .ofs_x = 2, .ofs_y = 0},
    {.bitmap_index = 464, .adv_w = 137, .box_w = 6, .box_h = 3, .ofs_x = 1, .ofs_y = 4}
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
const lv_font_t SilkScreen12 = {
#else
lv_font_t SilkScreen12 = {
#endif
    .get_glyph_dsc = lv_font_get_glyph_dsc_fmt_txt,    /*Function pointer to get glyph's data*/
    .get_glyph_bitmap = lv_font_get_bitmap_fmt_txt,    /*Function pointer to get glyph's bitmap*/
    .line_height = 10,          /*The maximum line height required by the font*/
    .base_line = 1,             /*Baseline measured from the bottom of the line*/
#if !(LVGL_VERSION_MAJOR == 6 && LVGL_VERSION_MINOR == 0)
    .subpx = LV_FONT_SUBPX_NONE,
#endif
#if LV_VERSION_CHECK(7, 4, 0) || LVGL_VERSION_MAJOR >= 8
    .underline_position = -2,
    .underline_thickness = 0,
#endif
    .static_bitmap = 0,
    .dsc = &font_dsc,          /*The custom font data. Will be accessed by `get_glyph_bitmap/dsc` */
#if LV_VERSION_CHECK(8, 2, 0) || LVGL_VERSION_MAJOR >= 9
    .fallback = &lv_font_montserrat_12,
#endif
    .user_data = NULL,
};



#endif /*#if SILKSCREEN12*/
