#ifndef EXP_LVGLDASHBOARD_SRC_CLOCKDISPLAY_H_
#define EXP_LVGLDASHBOARD_SRC_CLOCKDISPLAY_H_

#include "lvgl.h"
#include "src/core/lv_obj.h"
#include "src/misc/lv_area.h"
#include <time.h>

class ClockDisplay {
public:
    ClockDisplay();
    virtual ~ClockDisplay();

    void init(lv_obj_t * parent);

    void show(bool b);
    void hide();

private:
    static void timerCb(lv_timer_t * timer);
    void timerHandler(lv_timer_t * timer);

    static void anim_label_y(void * var, int32_t v);
    static void anim_roll_ready(lv_anim_t * a);
    void roll_digit(lv_obj_t * current, lv_obj_t * next, char digit);

    lv_obj_t * pClock;
    lv_obj_t * pHourTen;
    lv_obj_t * pHourTenAnim;
    lv_obj_t * pHourUnit;
    lv_obj_t * pHourUnitAnim;
    lv_obj_t * pColon;
    lv_obj_t * pMinTen;
    lv_obj_t * pMinTenAnim;
    lv_obj_t * pMinUnit;
    lv_obj_t * pMinUnitAnim;

    lv_style_t xStyleRoller;
    lv_style_t xStyleColon;
    lv_style_t xStyleClock;
    lv_timer_t * pTimerClk;

    struct tm xTime;
};

#endif /* EXP_LVGLDASHBOARD_SRC_CLOCKDISPLAY_H_ */
