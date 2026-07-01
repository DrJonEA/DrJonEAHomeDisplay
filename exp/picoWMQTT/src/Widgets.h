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
	Widgets();
	virtual ~Widgets();

	void init();

private:

	static void timerCB(lv_timer_t * timer);
	void timerHandler(lv_timer_t * timer);

	ClockDisplay clockDisplay;

	lv_obj_t *xTV;
	lv_obj_t *xTile1;

	lv_obj_t *pDrJonLbl;
	lv_obj_t *pTestLbl;
	lv_obj_t *pBtmLbl;

	lv_style_t xStyleTile;
	lv_style_t xLabelSt;
	lv_style_t xLabelStA;
	lv_style_t xLabelStB;
	lv_style_t style_line;

	lv_timer_t * pTimer;

	int32_t xPos = 0;

};

#endif /* EXP_LVGLDASHBOARD_SRC_WIDGETS_H_ */
