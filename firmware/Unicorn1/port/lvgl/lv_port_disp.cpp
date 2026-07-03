/**
 * @file lv_port_disp_templ.c
 *
 */

/*Copy this file as "lv_port_disp.c" and set this value to "1" to enable content*/
#if 1

/*********************
 *      INCLUDES
 *********************/
extern "C"{
#include "lvgl.h"
}
#include <FreeRTOS.h>
#include "lv_port_disp.h"
#include "libraries/pico_graphics/pico_graphics.hpp"
#include "cosmic_unicorn.hpp"

#define BYTES_PER_PIXEL 3

using namespace pimoroni;
CosmicUnicorn cosmic_unicorn;


static lv_display_t * display1;
static 	uint8_t *buf1;
static  	uint8_t *buf2;
//static uint8_t buf1[MY_DISP_HOR_RES * MY_DISP_VER_RES / 10 * BYTES_PER_PIXEL];
//static uint8_t buf2[MY_DISP_HOR_RES * MY_DISP_VER_RES / 10 * BYTES_PER_PIXEL];


void my_flush_cb(lv_display_t * display, const lv_area_t * area, uint8_t * px_map){

    uint8_t * buf = px_map;
    int32_t x, y;
    for(y = area->y1; y <= area->y2; y++) {
        for(x = area->x1; x <= area->x2; x++) {
        	uint8_t b = *buf++;
        	uint8_t g = *buf++;
        	uint8_t r = *buf++;
        	cosmic_unicorn.set_pixel(
        	        			x,  y,
        						r,g,b
        						);
        }
    }

    /* IMPORTANT!!!
     * Inform LVGL that flushing is complete so buffer can be modified again. */
    lv_display_flush_ready(display);
}


void lv_port_disp_init(void){
	cosmic_unicorn.init();
	cosmic_unicorn.set_brightness(0.5);

	display1 = lv_display_create(MY_DISP_HOR_RES, MY_DISP_VER_RES);

	/* Set display buffer for display `display1`. */
	size_t bufSize = MY_DISP_HOR_RES * MY_DISP_VER_RES / 10 * BYTES_PER_PIXEL;
	buf1 = (uint8_t*)pvPortMalloc(bufSize);
	buf2 = (uint8_t*)pvPortMalloc(bufSize);
	lv_display_set_buffers(display1, buf1, buf2, bufSize, LV_DISPLAY_RENDER_MODE_PARTIAL);

	lv_display_set_flush_cb(display1, my_flush_cb);
}


#endif
