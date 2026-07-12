/*
 * Widgets.cpp
 *
 *  Created on: 4 Aug 2025
 *      Author: jondurrant
 */

#include "Widgets.h"
#include <cstdio>
#include "DeviceState.h"

Widgets *Widgets::SELF = NULL;

Widgets * Widgets::singleton(){
	if (SELF == NULL){
		SELF = new Widgets;
	}
	return SELF;
}

Widgets::Widgets() {
}

Widgets::~Widgets() {
	// TODO Auto-generated destructor stub
}



void Widgets::init() {

	pTV =lv_scr_act();
	lv_obj_clear_flag(pTV, LV_OBJ_FLAG_SCROLLABLE);

	lv_style_init(&xStyleTile);
	lv_style_set_bg_color(&xStyleTile, lv_color_hex(0x000000));
	lv_style_set_bg_opa(&xStyleTile, LV_OPA_COVER);
	lv_obj_add_style(pTV, &xStyleTile, 0);


	pTV = lv_tileview_create(pTV);
	pTile1 = lv_tileview_add_tile(pTV, 0, 0, LV_DIR_NONE);
	pTile2 = lv_tileview_add_tile(pTV, 1, 0, LV_DIR_NONE);
	lv_obj_add_style(pTile1, &xStyleTile, 0);
	lv_obj_add_style(pTile2, &xStyleTile, 0);
	lv_obj_clear_flag(pTV, LV_OBJ_FLAG_SCROLLABLE);
	lv_obj_clear_flag(pTile1, LV_OBJ_FLAG_SCROLLABLE);
	lv_obj_clear_flag(pTile2, LV_OBJ_FLAG_SCROLLABLE);

	xTileDefault.init(pTile1);
	xTileImage.init(pTile2);
}

void Widgets::img(const void *ptr, size_t len, const char * msgStr){
	xTileImage.img(ptr, len, msgStr);
	lv_tileview_set_tile_by_index(
			pTV,
			1, 0,
			LV_ANIM_ON);
}

void Widgets::setLayout(uint layout){
	lv_tileview_set_tile_by_index(
				pTV,
				layout, 0,
				LV_ANIM_ON);
}



void Widgets::message(const char *s){
	xTileDefault.message(s);
	lv_tileview_set_tile_by_index(
				pTV,
				0, 0,
				LV_ANIM_ON);
}

