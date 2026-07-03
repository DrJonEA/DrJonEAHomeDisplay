/*
 * Widgets.h
 *
 *  Created on: 4 Aug 2025
 *      Author: jondurrant
 */

#ifndef EXP_LVGLDASHBOARD_SRC_WIDGETS_H_
#define EXP_LVGLDASHBOARD_SRC_WIDGETS_H_

#include "lvgl.h"
#include "src/core/lv_obj.h"
#include "src/misc/lv_area.h"
#include "pico/stdlib.h"
#include "ClockDisplay.h"
#include <time.h>


class Widgets {
public:
	static Widgets * singleton();
	virtual ~Widgets();

	void init();

	void message(const char *s);

	void img(const void *ptr, size_t len);

private:
	Widgets();
	static Widgets *SELF;
	static void timerCB(lv_timer_t * timer);
	void timerHandler(lv_timer_t * timer);

	static void timerIconCB(lv_timer_t * timer);
	void timerIconHandler(lv_timer_t * timer);

	ClockDisplay clockDisplay;

	lv_obj_t *xTV;
	lv_obj_t *xTile1;
	lv_obj_t *xTile2;

	lv_obj_t *pDrJonLbl;
	lv_obj_t *pTestLbl;
	lv_obj_t *pBtmLbl;

	lv_obj_t *pWifiIcon;
	lv_obj_t *pCloudIcon;
	lv_obj_t *pDefconIcon;

	lv_obj_t *pTemperature;
	lv_obj_t *pHumidity;

	lv_obj_t *pImg;
	lv_image_dsc_t xImgDsc;

	lv_style_t xStyleTile;
	lv_style_t xLabelSt;
	lv_style_t xLabelStA;
	lv_style_t xLabelStB;
	lv_style_t style_line;

	lv_timer_t * pTimer;
	lv_timer_t * pIconTimer;

	int32_t xPos = 0;

};

#endif /* EXP_LVGLDASHBOARD_SRC_WIDGETS_H_ */
