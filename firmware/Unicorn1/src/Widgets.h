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

#include "TileDefault.h"
#include "TileImage.h"

class Widgets {
public:
	static Widgets * singleton();
	virtual ~Widgets();

	void init();

	void message(const char *s);

	void img(const void *ptr, size_t len, const char * msgStr = NULL);

	void setLayout(uint layout);

private:
	Widgets();
	static Widgets *SELF;
	static void timerCB(lv_timer_t * timer);
	void timerHandler(lv_timer_t * timer);

	static void timerIconCB(lv_timer_t * timer);
	void timerIconHandler(lv_timer_t * timer);

	TileDefault xTileDefault;
	TileImage xTileImage;

	lv_obj_t *pTV;
	lv_obj_t *pTile1;
	lv_obj_t *pTile2;

	lv_style_t xStyleTile;
};

#endif /* EXP_LVGLDASHBOARD_SRC_WIDGETS_H_ */
