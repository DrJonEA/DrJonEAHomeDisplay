/*
 * Widgets.cpp
 *
 *  Created on: 4 Aug 2025
 *      Author: jondurrant
 */

#include "Widgets.h"
#include <cstdio>

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
	lv_style_set_text_font(&xLabelSt, &lv_font_montserrat_8);
	lv_style_set_text_color(
			&xLabelSt,
			lv_color_make(0, 0x00, 0xF0));

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

	/*Create a line and apply the new style*/
	/*
	lv_obj_t * line1;
	line1 = lv_line_create(lv_screen_active());
	lv_line_set_points(line1, line_points, 5);
	lv_obj_add_style(line1, &style_line, 0);
	lv_obj_center(line1);
	*/

	pDrJonLbl = lv_label_create(xTV);
	//lv_label_set_long_mode(pDrJonLbl, LV_LABEL_LONG_WRAP);     /*Break the long lines*/
	lv_label_set_text(pDrJonLbl, "DrJon");
	lv_obj_set_width(pDrJonLbl, 32);  /*Set smaller width to make the lines wrap*/
	lv_obj_set_style_text_align(pDrJonLbl, LV_TEXT_ALIGN_LEFT, 0);
	lv_obj_align(pDrJonLbl, LV_ALIGN_TOP_LEFT, 0,-3);
	lv_obj_add_style(pDrJonLbl , &xLabelSt,  LV_PART_MAIN);

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

	clockDisplay.init(xTV);

	pTimer = lv_timer_create(timerCB, 100,  this);

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


void Widgets::message(const char *s){
	lv_label_set_text(pTestLbl, s);
}

