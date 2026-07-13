/*
 * TileImage.h
 *
 *  Created on: 12 Jul 2026
 *      Author: jondurrant
 */

#ifndef FIRMWARE_UNICORN1_SRC_TILEIMAGE_H_
#define FIRMWARE_UNICORN1_SRC_TILEIMAGE_H_

#include "lvgl.h"
#include "src/core/lv_obj.h"
#include "src/misc/lv_area.h"
#include "pico/stdlib.h"
#include "ClockDisplay.h"

class TileImage {
public:
	TileImage();
	virtual ~TileImage();

	void init(lv_obj_t *parent);

	void message(const char *s);

	void img(const void *ptr, size_t len, const char * msgStr = NULL);

	void showClock(bool b = true);
	void hideClock();

private:
	static void timerCB(lv_timer_t * timer);
	void timerHandler(lv_timer_t * timer);

	lv_obj_t *pImg;
	lv_image_dsc_t xImgDsc;
	lv_obj_t *pScrollTxt;

	lv_style_t xLabelStA;

	lv_timer_t * pTimer;

	int32_t xPos = 0;
	int32_t xScrollY = 0;

	ClockDisplay clockDisplay;
};

#endif /* FIRMWARE_UNICORN1_SRC_TILEIMAGE_H_ */
