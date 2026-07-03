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

	xTV =lv_scr_act();
	lv_obj_clear_flag(xTV, LV_OBJ_FLAG_SCROLLABLE);

	lv_style_init(&xStyleTile);
	lv_style_set_bg_color(&xStyleTile, lv_color_hex(0x000000));
	lv_style_set_bg_opa(&xStyleTile, LV_OPA_COVER);
	lv_obj_add_style(xTV, &xStyleTile, 0);

	lv_style_init(&xLabelSt);
	lv_style_set_text_font(&xLabelSt, &lv_font_montserrat_10);
	lv_style_set_text_color(
			&xLabelSt,
			lv_color_make(0, 0xF0, 0xF0));

	lv_style_init(&xLabelStA);
	lv_style_set_text_font(&xLabelStA, &lv_font_montserrat_12);
	lv_style_set_text_color(
			&xLabelStA,
			lv_color_make(0, 0xF0, 0xF0));

	lv_style_init(&xLabelStB);
	lv_style_set_text_font(&xLabelStB, &lv_font_unscii_8);
	lv_style_set_text_color(
			&xLabelStB,
			lv_color_make(0xFF, 0xF0, 0xF0));


	xTV = lv_tileview_create(xTV);
	xTile1 = lv_tileview_add_tile(xTV, 0, 0, LV_DIR_NONE);
	xTile2 = lv_tileview_add_tile(xTV, 1, 0, LV_DIR_NONE);
	lv_obj_add_style(xTile1, &xStyleTile, 0);
	lv_obj_add_style(xTile2, &xStyleTile, 0);
	lv_obj_clear_flag(xTV, LV_OBJ_FLAG_SCROLLABLE);
	lv_obj_clear_flag(xTile1, LV_OBJ_FLAG_SCROLLABLE);
	lv_obj_clear_flag(xTile2, LV_OBJ_FLAG_SCROLLABLE);


	pTemperature = lv_label_create(xTile1);
	lv_label_set_text(pTemperature, "??.?C");
	lv_obj_set_width(pTemperature, 32);
	lv_obj_set_style_text_align(pTemperature, LV_TEXT_ALIGN_LEFT, 0);
	lv_obj_align(pTemperature, LV_ALIGN_TOP_LEFT, 0, 7);
	lv_obj_add_style(pTemperature , &xLabelSt,  LV_PART_MAIN);

	pHumidity = lv_label_create(xTile1);
	lv_label_set_text(pHumidity, "??.?%");
	lv_obj_set_width(pHumidity, 32);
	lv_obj_set_style_text_align(pHumidity, LV_TEXT_ALIGN_LEFT, 0);
	lv_obj_align(pHumidity, LV_ALIGN_TOP_LEFT, 0, 15);
	lv_obj_add_style(pHumidity , &xLabelSt,  LV_PART_MAIN);



	LV_IMAGE_DECLARE(wifi_off);
	pWifiIcon = lv_image_create(xTile1);
	lv_image_set_src(pWifiIcon, &wifi_off);
	lv_obj_align(pWifiIcon, LV_ALIGN_TOP_RIGHT, 0, 0);

	LV_IMAGE_DECLARE(cloud_off);
	pCloudIcon = lv_image_create(xTile1);
	lv_image_set_src(pCloudIcon, &cloud_off);
	lv_obj_align(pCloudIcon, LV_ALIGN_TOP_RIGHT, -8, 0);

	LV_IMAGE_DECLARE(defcon5);
	pDefconIcon = lv_image_create(xTile1);
	lv_image_set_src(pDefconIcon, &defcon5);
	lv_obj_align(pDefconIcon, LV_ALIGN_TOP_LEFT, 0, 0);

	clockDisplay.init(xTile1);

	//Tile 2
	pImg = lv_image_create(xTile2);
	lv_obj_align(pImg, LV_ALIGN_TOP_LEFT, 0, 0);

	pScrollTxt = lv_label_create(xTile2);
	lv_label_set_text(pScrollTxt, "Test");
	lv_obj_set_style_text_align(pScrollTxt, LV_TEXT_ALIGN_LEFT, 0);
	lv_obj_align(pScrollTxt, LV_ALIGN_BOTTOM_LEFT, 0, 0);
	lv_obj_add_style(pScrollTxt , &xLabelStA,  LV_PART_MAIN);

	pTimer = lv_timer_create(timerCB, 100,  this);
	pIconTimer = lv_timer_create(timerIconCB, 1000,  this);

}

void Widgets::img(const void *ptr, size_t len, const char * msgStr){
	xImgDsc.header.cf = LV_COLOR_FORMAT_RGB565;
	xImgDsc.header.magic = LV_IMAGE_HEADER_MAGIC;
	xImgDsc.header.w = 32;
	xImgDsc.header.h = 32;
	xImgDsc.data_size = len;
	xImgDsc.data = (const uint8_t*)ptr;

	printf("Set img %u\n", len);

	lv_image_set_src(pImg, &xImgDsc);
	if (msgStr == NULL){
		lv_label_set_text(pScrollTxt, "");
	} else {
		printf("Msg set to %s\n", msgStr);
		lv_label_set_text(pScrollTxt, msgStr);
	}
	lv_tileview_set_tile_by_index(
			xTV,
			1, 0,
			LV_ANIM_ON);

}

void Widgets::setLayout(uint layout){
	lv_tileview_set_tile_by_index(
				xTV,
				layout, 0,
				LV_ANIM_ON);
}


void Widgets::timerCB(lv_timer_t * timer){
	Widgets *self = (Widgets *)lv_timer_get_user_data( timer);
		self->timerHandler(timer);
}

void Widgets::timerHandler(lv_timer_t * timer){

	int32_t l = lv_obj_get_width(pScrollTxt) ;

	lv_obj_align(pScrollTxt, LV_ALIGN_BOTTOM_LEFT, xPos--, 0);
	//printf("Scroll (%d, %d) at (%d, %d)\n", l, h, xPos, 20);
	//lv_obj_set_pos(pScrollTxt,  xPos--,  20);


	if (xPos < (l * -1)){
		xPos = 32;//l;
	}
}

void Widgets::timerIconCB(lv_timer_t * timer){
	Widgets *self = (Widgets *)lv_timer_get_user_data( timer);
		self->timerIconHandler(timer);
}

void Widgets::timerIconHandler(lv_timer_t * timer){
	LV_IMAGE_DECLARE(wifi_off);
	LV_IMAGE_DECLARE(wifi_on);
	LV_IMAGE_DECLARE(cloud_off);
	LV_IMAGE_DECLARE(cloud_on);
	LV_IMAGE_DECLARE(defcon5);
	LV_IMAGE_DECLARE(defcon4);
	LV_IMAGE_DECLARE(defcon3);
	LV_IMAGE_DECLARE(defcon2);
	LV_IMAGE_DECLARE(defcon1);

	if (DeviceState::singleton()->isWifiOnline()){
		lv_image_set_src(pWifiIcon, &wifi_on);
	} else {
		lv_image_set_src(pWifiIcon, &wifi_off);
	}

	if (DeviceState::singleton()->isMQTTOnline()){
		lv_image_set_src(pCloudIcon, &cloud_on);
	} else {
		lv_image_set_src(pCloudIcon, &cloud_off);
	}

	char buf[10];
	sprintf(buf, "%.1fC", DeviceState::singleton()->getTemperature());
	lv_label_set_text(pTemperature, buf);

	sprintf(buf, "%.1f%%", DeviceState::singleton()->getHumidity());
	lv_label_set_text(pHumidity, buf);

	switch(DeviceState::singleton()->getDefCon()){
	case 1:
		lv_image_set_src(pDefconIcon, &defcon1);
		break;
	case 2:
		lv_image_set_src(pDefconIcon, &defcon2);
		break;
	case 3:
		lv_image_set_src(pDefconIcon, &defcon3);
		break;
	case 4:
		lv_image_set_src(pDefconIcon, &defcon4);
		break;
	case 5:
		lv_image_set_src(pDefconIcon, &defcon5);
		break;
	}
}


void Widgets::message(const char *s){
	lv_label_set_text(pScrollTxt, s);
}

