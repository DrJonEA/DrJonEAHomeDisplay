/*
 * TileImage.cpp
 *
 *  Created on: 12 Jul 2026
 *      Author: jondurrant
 */

#include "TileImage.h"
#include <cstdio>
#include <cstring>

TileImage::TileImage() {
	// TODO Auto-generated constructor stub

}

TileImage::~TileImage() {
	// TODO Auto-generated destructor stub
}


void TileImage::init(lv_obj_t *parent){

	lv_style_init(&xLabelStA);
	lv_style_set_text_font(&xLabelStA, &lv_font_montserrat_12);
	lv_style_set_text_color(
			&xLabelStA,
			lv_color_make(0, 0xF0, 0xF0));

	pImg = lv_image_create(parent);
	lv_obj_align(pImg, LV_ALIGN_TOP_LEFT, 0, 0);

	pScrollTxt = lv_label_create(parent);
	lv_label_set_text(pScrollTxt, "Test");
	lv_obj_set_style_text_align(pScrollTxt, LV_TEXT_ALIGN_LEFT, 0);
	lv_obj_align(pScrollTxt, LV_ALIGN_BOTTOM_LEFT, 0, xScrollY);
	lv_obj_add_style(pScrollTxt , &xLabelStA,  LV_PART_MAIN);

	clockDisplay.init(parent);
	clockDisplay.hide();

}

void TileImage::img(const void *ptr, size_t len, const char * msgStr){
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
		if (strlen(msgStr) > 0){
			if (pTimer == NULL){
				xMsgCount = 0;
				pTimer = lv_timer_create(timerCB, 100,  this);
			}
		}
	}
}


void TileImage::timerCB(lv_timer_t * timer){
	TileImage *self = (TileImage *)lv_timer_get_user_data( timer);
		self->timerHandler(timer);
}

void TileImage::timerHandler(lv_timer_t * timer){

	int32_t l = lv_obj_get_width(pScrollTxt) ;

	lv_obj_align(pScrollTxt, LV_ALIGN_BOTTOM_LEFT, xPos--, xScrollY);

	if (xPos < (l * -1)){
		xPos = 32;

		xMsgCount++;
		if (xMsgCount > TILE_MSG_CYCLES){
			lv_timer_delete(pTimer);
			pTimer = NULL;
		}
	}
}

void TileImage::showClock(bool b){
	clockDisplay.show(b);
	if (b){
		xScrollY = -8;
	} else {
		xScrollY = 0;
	}
}
void TileImage::hideClock(){
	showClock(false);
}
