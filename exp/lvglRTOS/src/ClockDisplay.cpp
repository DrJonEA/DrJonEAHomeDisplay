#include "ClockDisplay.h"

ClockDisplay::ClockDisplay() {
    xTime.tm_hour = 0;
    xTime.tm_min = 0;
}

ClockDisplay::~ClockDisplay() {
}

void ClockDisplay::init(lv_obj_t * parent) {
    lv_style_init(&xStyleRoller);
    lv_style_set_text_font(&xStyleRoller, &lv_font_unscii_8);
    lv_style_set_bg_color(&xStyleRoller, lv_color_hex(0x000000));
    lv_style_set_bg_opa(&xStyleRoller, LV_OPA_COVER);
    lv_style_set_border_width(&xStyleRoller, 0);
    lv_style_set_text_color(&xStyleRoller, lv_color_hex(0xA0A0A0));
    lv_style_set_text_align(&xStyleRoller, LV_TEXT_ALIGN_CENTER);

    pHourTen = lv_label_create(parent);
    lv_label_set_text(pHourTen, "0");
    lv_obj_add_style(pHourTen, &xStyleRoller, LV_PART_MAIN);
    lv_obj_set_size(pHourTen, 8, 8);
    lv_obj_align(pHourTen, LV_ALIGN_TOP_LEFT, 0, 24);

    pHourUnit = lv_label_create(parent);
    lv_label_set_text(pHourUnit, "0");
    lv_obj_add_style(pHourUnit, &xStyleRoller, LV_PART_MAIN);
    lv_obj_set_size(pHourUnit, 8, 8);
    lv_obj_align(pHourUnit, LV_ALIGN_TOP_LEFT, 7, 24);

    lv_style_init(&xStyleColon);
    lv_style_set_bg_color(&xStyleColon, lv_color_hex(0xA0A0A0));
    lv_style_set_bg_opa(&xStyleColon, LV_OPA_COVER);
    lv_style_set_border_width(&xStyleColon, 0);

    lv_obj_t * dotTop = lv_obj_create(parent);
    lv_obj_add_style(dotTop, &xStyleColon, LV_PART_MAIN);
    lv_obj_set_size(dotTop, 1, 1);
    lv_obj_align(dotTop, LV_ALIGN_TOP_LEFT, 15, 27);

    lv_obj_t * dotBottom = lv_obj_create(parent);
    lv_obj_add_style(dotBottom, &xStyleColon, LV_PART_MAIN);
    lv_obj_set_size(dotBottom, 1, 1);
    lv_obj_align(dotBottom, LV_ALIGN_TOP_LEFT, 15, 30);

    pMinTen = lv_label_create(parent);
    lv_label_set_text(pMinTen, "0");
    lv_obj_add_style(pMinTen, &xStyleRoller, LV_PART_MAIN);
    lv_obj_set_size(pMinTen, 8, 8);
    lv_obj_align(pMinTen, LV_ALIGN_TOP_LEFT, 17, 24);

    pMinUnit = lv_label_create(parent);
    lv_label_set_text(pMinUnit, "0");
    lv_obj_add_style(pMinUnit, &xStyleRoller, LV_PART_MAIN);
    lv_obj_set_size(pMinUnit, 8, 8);
    lv_obj_align(pMinUnit, LV_ALIGN_TOP_LEFT, 24, 24);

    pHourTenAnim = lv_label_create(parent);
    lv_label_set_text(pHourTenAnim, "0");
    lv_obj_add_style(pHourTenAnim, &xStyleRoller, LV_PART_MAIN);
    lv_obj_set_size(pHourTenAnim, 8, 8);
    lv_obj_align(pHourTenAnim, LV_ALIGN_TOP_LEFT, 0, 24);
    lv_obj_add_flag(pHourTenAnim, LV_OBJ_FLAG_HIDDEN);

    pHourUnitAnim = lv_label_create(parent);
    lv_label_set_text(pHourUnitAnim, "0");
    lv_obj_add_style(pHourUnitAnim, &xStyleRoller, LV_PART_MAIN);
    lv_obj_set_size(pHourUnitAnim, 8, 8);
    lv_obj_align(pHourUnitAnim, LV_ALIGN_TOP_LEFT, 7, 24);
    lv_obj_add_flag(pHourUnitAnim, LV_OBJ_FLAG_HIDDEN);

    pMinTenAnim = lv_label_create(parent);
    lv_label_set_text(pMinTenAnim, "0");
    lv_obj_add_style(pMinTenAnim, &xStyleRoller, LV_PART_MAIN);
    lv_obj_set_size(pMinTenAnim, 8, 8);
    lv_obj_align(pMinTenAnim, LV_ALIGN_TOP_LEFT, 17, 24);
    lv_obj_add_flag(pMinTenAnim, LV_OBJ_FLAG_HIDDEN);

    pMinUnitAnim = lv_label_create(parent);
    lv_label_set_text(pMinUnitAnim, "0");
    lv_obj_add_style(pMinUnitAnim, &xStyleRoller, LV_PART_MAIN);
    lv_obj_set_size(pMinUnitAnim, 8, 8);
    lv_obj_align(pMinUnitAnim, LV_ALIGN_TOP_LEFT, 24, 24);
    lv_obj_add_flag(pMinUnitAnim, LV_OBJ_FLAG_HIDDEN);

    pTimerClk = lv_timer_create(timerCb, 1000, this);
}

void ClockDisplay::timerCb(lv_timer_t * timer) {
    ClockDisplay * self = (ClockDisplay *)lv_timer_get_user_data(timer);
    self->timerHandler(timer);
}

void ClockDisplay::timerHandler(lv_timer_t * timer) {
    xTime.tm_min += 1;
    if (xTime.tm_min > 59) {
        xTime.tm_min = 0;
        xTime.tm_hour += 1;
        if (xTime.tm_hour > 23) {
            xTime.tm_hour = 0;
        }
    }

    char hourTen = '0' + xTime.tm_hour / 10;
    char hourUnit = '0' + xTime.tm_hour % 10;
    char minTen = '0' + xTime.tm_min / 10;
    char minUnit = '0' + xTime.tm_min % 10;

    const char * cur;
    cur = lv_label_get_text(pHourTen);
    if (cur[0] != hourTen) {
        roll_digit(pHourTen, pHourTenAnim, hourTen);
    }
    cur = lv_label_get_text(pHourUnit);
    if (cur[0] != hourUnit) {
        roll_digit(pHourUnit, pHourUnitAnim, hourUnit);
    }
    cur = lv_label_get_text(pMinTen);
    if (cur[0] != minTen) {
        roll_digit(pMinTen, pMinTenAnim, minTen);
    }
    cur = lv_label_get_text(pMinUnit);
    if (cur[0] != minUnit) {
        roll_digit(pMinUnit, pMinUnitAnim, minUnit);
    }
}

void ClockDisplay::anim_label_y(void * var, int32_t v) {
    lv_obj_set_y((lv_obj_t *)var, v);
}

void ClockDisplay::anim_roll_ready(lv_anim_t * a) {
    lv_obj_t * next = (lv_obj_t *)a->var;
    lv_obj_t * current = (lv_obj_t *)a->user_data;
    const char * text = lv_label_get_text(next);
    lv_label_set_text(current, text);
    lv_obj_clear_flag(current, LV_OBJ_FLAG_HIDDEN);
    lv_obj_add_flag(next, LV_OBJ_FLAG_HIDDEN);
    lv_obj_set_y(next, lv_obj_get_y(current) + 8);
}

void ClockDisplay::roll_digit(lv_obj_t * current, lv_obj_t * next, char digit) {
    char buf[2] = {digit, '\0'};
    lv_label_set_text(next, buf);
    lv_obj_clear_flag(next, LV_OBJ_FLAG_HIDDEN);
    lv_obj_move_foreground(next);
    lv_obj_set_y(next, lv_obj_get_y(current) + 8);

    lv_anim_t a;
    lv_anim_init(&a);
    lv_anim_set_var(&a, next);
    lv_anim_set_exec_cb(&a, anim_label_y);
    lv_anim_set_values(&a, lv_obj_get_y(next), lv_obj_get_y(current));
    lv_anim_set_time(&a, 200);
    lv_anim_set_path_cb(&a, lv_anim_path_ease_out);
    lv_anim_set_user_data(&a, current);
    lv_anim_set_completed_cb(&a, anim_roll_ready);
    lv_anim_start(&a);
}
