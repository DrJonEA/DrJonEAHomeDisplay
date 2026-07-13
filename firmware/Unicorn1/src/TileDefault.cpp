/*
 * TileDefault.cpp
 *
 *  Created on: 12 Jul 2026
 *      Author: jondurrant
 */

#include "TileDefault.h"
#include <cstdio>
#include "DeviceState.h"

TileDefault::TileDefault() {
	// TODO Auto-generated constructor stub

}

TileDefault::~TileDefault() {
	// TODO Auto-generated destructor stub
}

void TileDefault::init(lv_obj_t *parent){

	lv_style_init(&xLabelSt);
	lv_style_set_text_font(&xLabelSt, &lv_font_montserrat_10);
	lv_style_set_text_color(
			&xLabelSt,
			lv_color_make(0, 0xF0, 0xF0));

	pScrollTxt = lv_label_create(parent);
	lv_label_set_text(pScrollTxt, "Test");
	lv_obj_set_style_text_align(pScrollTxt, LV_TEXT_ALIGN_LEFT, 0);
	lv_obj_align(pScrollTxt, LV_ALIGN_TOP_LEFT, 32, 10);
	lv_obj_add_style(pScrollTxt , &xLabelSt,  LV_PART_MAIN);
	lv_obj_add_flag(pScrollTxt, LV_OBJ_FLAG_HIDDEN);

	pTemperature = lv_label_create(parent);
	lv_label_set_text(pTemperature, "??.?C");
	lv_obj_set_width(pTemperature, 32);
	lv_obj_set_style_text_align(pTemperature, LV_TEXT_ALIGN_LEFT, 0);
	lv_obj_align(pTemperature, LV_ALIGN_TOP_LEFT, 0, 7);
	lv_obj_add_style(pTemperature , &xLabelSt,  LV_PART_MAIN);

	pHumidity = lv_label_create(parent);
	lv_label_set_text(pHumidity, "??.?%");
	lv_obj_set_width(pHumidity, 32);
	lv_obj_set_style_text_align(pHumidity, LV_TEXT_ALIGN_LEFT, 0);
	lv_obj_align(pHumidity, LV_ALIGN_TOP_LEFT, 0, 15);
	lv_obj_add_style(pHumidity , &xLabelSt,  LV_PART_MAIN);


	LV_IMAGE_DECLARE(wifi_off);
	pWifiIcon = lv_image_create(parent);
	lv_image_set_src(pWifiIcon, &wifi_off);
	lv_obj_align(pWifiIcon, LV_ALIGN_TOP_RIGHT, 0, 0);

	LV_IMAGE_DECLARE(cloud_off);
	pCloudIcon = lv_image_create(parent);
	lv_image_set_src(pCloudIcon, &cloud_off);
	lv_obj_align(pCloudIcon, LV_ALIGN_TOP_RIGHT, -8, 0);

	LV_IMAGE_DECLARE(defcon5);
	pDefconIcon = lv_image_create(parent);
	lv_image_set_src(pDefconIcon, &defcon5);
	lv_obj_align(pDefconIcon, LV_ALIGN_TOP_LEFT, 0, 0);

	clockDisplay.init(parent);

	pIconTimer = lv_timer_create(timerIconCB, 1000,  this);

}


void TileDefault::timerCB(lv_timer_t * timer){
	TileDefault *self = (TileDefault *)lv_timer_get_user_data( timer);
	self->timerHandler(timer);
}

void TileDefault::timerHandler(lv_timer_t * timer){

	int32_t l = lv_obj_get_width(pScrollTxt) ;

	//printf("SCROLL %d\n", xPos);
	lv_obj_align(pScrollTxt, LV_ALIGN_TOP_LEFT, xPos--, 10);


	if (xPos < (l * -1)){
		xPos = 32;
		xMsgCount++;
		if (xMsgCount > TILE_MSG_CYCLES){
			lv_timer_delete(pTimer);
			pTimer = NULL;
			lv_obj_add_flag(pScrollTxt, LV_OBJ_FLAG_HIDDEN);
			lv_obj_clear_flag(pTemperature, LV_OBJ_FLAG_HIDDEN);
			lv_obj_clear_flag(pHumidity, LV_OBJ_FLAG_HIDDEN);
		}
	}
}

void TileDefault::timerIconCB(lv_timer_t * timer){
	TileDefault *self = (TileDefault *)lv_timer_get_user_data( timer);
	self->timerIconHandler(timer);
}

void TileDefault::timerIconHandler(lv_timer_t * timer){
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


void TileDefault::message(const char *s){
	xPos = 32;
	xMsgCount = 0;

	lv_label_set_text(pScrollTxt, s);
	lv_obj_align(pScrollTxt, LV_ALIGN_TOP_LEFT, xPos, 10);
	lv_obj_clear_flag(pScrollTxt, LV_OBJ_FLAG_HIDDEN);
	lv_obj_add_flag(pTemperature, LV_OBJ_FLAG_HIDDEN);
	lv_obj_add_flag(pHumidity, LV_OBJ_FLAG_HIDDEN);

	if (pTimer == NULL){
		pTimer = lv_timer_create(timerCB, 100,  this);
	}
}
