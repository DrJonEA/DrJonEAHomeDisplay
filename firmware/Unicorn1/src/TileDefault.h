/*
 * TileDefault.h
 *
 *  Created on: 12 Jul 2026
 *      Author: jondurrant
 */

#ifndef FIRMWARE_UNICORN1_SRC_TILEDEFAULT_H_
#define FIRMWARE_UNICORN1_SRC_TILEDEFAULT_H_

#include "lvgl.h"
#include "src/core/lv_obj.h"
#include "src/misc/lv_area.h"
#include "pico/stdlib.h"
#include "ClockDisplay.h"
#include <time.h>

#ifndef TILE_MSG_CYCLES
#define TILE_MSG_CYCLES 3
#endif

class TileDefault {
public:
	TileDefault();
	virtual ~TileDefault();

	void init(lv_obj_t *parent);

	void message(const char *s);

private:
	static void timerCB(lv_timer_t * timer);
	void timerHandler(lv_timer_t * timer);

	static void timerIconCB(lv_timer_t * timer);
	void timerIconHandler(lv_timer_t * timer);

	lv_style_t xLabelSt;

	ClockDisplay clockDisplay;
	lv_obj_t *pWifiIcon;
	lv_obj_t *pCloudIcon;
	lv_obj_t *pDefconIcon;

	lv_obj_t *pTemperature;
	lv_obj_t *pHumidity;
	lv_obj_t *pScrollTxt;

	lv_timer_t * pTimer;
	lv_timer_t * pIconTimer;

	int32_t xPos = 0;
	int8_t xMsgCount = 0;

};

#endif /* FIRMWARE_UNICORN1_SRC_TILEDEFAULT_H_ */
