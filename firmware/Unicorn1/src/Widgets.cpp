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


	/*Create an array for the points of the line*/
	lv_point_precise_t line_points[] = { {5, 5}, {10, 20}, {20, 10}, {25, 15}, {30,30}};

	/*Create style*/
	lv_style_init(&style_line);
	lv_style_set_line_width(&style_line, 2);
	lv_style_set_line_color(&style_line, lv_palette_main(LV_PALETTE_BLUE));
	lv_style_set_line_rounded(&style_line, true);

	pTemperature = lv_label_create(xTV);
	lv_label_set_text(pTemperature, "??.?C");
	lv_obj_set_width(pTemperature, 32);
	lv_obj_set_style_text_align(pTemperature, LV_TEXT_ALIGN_LEFT, 0);
	lv_obj_align(pTemperature, LV_ALIGN_TOP_LEFT, 0, 7);
	lv_obj_add_style(pTemperature , &xLabelSt,  LV_PART_MAIN);

	pHumidity = lv_label_create(xTV);
	lv_label_set_text(pHumidity, "??.?%");
	lv_obj_set_width(pHumidity, 32);
	lv_obj_set_style_text_align(pHumidity, LV_TEXT_ALIGN_LEFT, 0);
	lv_obj_align(pHumidity, LV_ALIGN_TOP_LEFT, 0, 15);
	lv_obj_add_style(pHumidity , &xLabelSt,  LV_PART_MAIN);

	pTestLbl = lv_label_create(xTV);
	//lv_label_set_long_mode(pTestLbl, LV_LABEL_LONG_WRAP);     /*Break the long lines*/
	lv_label_set_text(pTestLbl, "Testing a Scoll Message");
	//lv_obj_set_width(pTestLbl, 32);  /*Set smaller width to make the lines wrap*/
	lv_obj_set_style_text_align(pTestLbl, LV_TEXT_ALIGN_LEFT, 0);
	lv_obj_align(pTestLbl, LV_ALIGN_TOP_LEFT, 0, 4);
	lv_obj_add_style(pTestLbl , &xLabelStA,  LV_PART_MAIN);
	xPos = 32;// lv_obj_get_width(pTestLbl);
	lv_obj_set_pos(pTestLbl,  xPos,  4);

	/*
	pBtmLbl = lv_label_create(xTV);
	//lv_label_set_long_mode(pBtmLbl, LV_LABEL_LONG_WRAP);     
	lv_label_set_text(pBtmLbl, "081234");//:32");
	lv_obj_set_width(pBtmLbl, 32);  
	lv_obj_set_style_text_align(pBtmLbl, LV_TEXT_ALIGN_LEFT, 0);
	lv_obj_align(pBtmLbl, LV_ALIGN_TOP_LEFT, -1,24);
	lv_obj_add_style(pBtmLbl , &xLabelStB,  LV_PART_MAIN);
	*/

	LV_IMAGE_DECLARE(wifi_off);
	pWifiIcon = lv_image_create(xTV);
	lv_image_set_src(pWifiIcon, &wifi_off);
	lv_obj_align(pWifiIcon, LV_ALIGN_TOP_RIGHT, 0, 0);

	LV_IMAGE_DECLARE(cloud_off);
	pCloudIcon = lv_image_create(xTV);
	lv_image_set_src(pCloudIcon, &cloud_off);
	lv_obj_align(pCloudIcon, LV_ALIGN_TOP_RIGHT, -8, 0);

	LV_IMAGE_DECLARE(defcon5);
	pDefconIcon = lv_image_create(xTV);
	lv_image_set_src(pDefconIcon, &defcon5);
	lv_obj_align(pDefconIcon, LV_ALIGN_TOP_LEFT, 0, 0);

	clockDisplay.init(xTV);

	pTimer = lv_timer_create(timerCB, 100,  this);
	pIconTimer = lv_timer_create(timerIconCB, 1000,  this);

}


void Widgets::timerCB(lv_timer_t * timer){
	Widgets *self = (Widgets *)lv_timer_get_user_data( timer);
		self->timerHandler(timer);
}

void Widgets::timerHandler(lv_timer_t * timer){
	//printf("Timer to %d\n", xPos);
	lv_obj_set_pos(pTestLbl,  xPos--,  4);

	int32_t l = lv_obj_get_width(pTestLbl) ;
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
	lv_label_set_text(pTestLbl, s);
}

