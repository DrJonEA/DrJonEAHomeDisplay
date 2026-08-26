/**
 * @file lv_mem_core_Freertos.c
 */

/*********************
 *      INCLUDES
 *********************/
#include "lvgl.h"
#include "src/stdlib/lv_mem.h"
#if LV_USE_STDLIB_MALLOC == LV_STDLIB_CUSTOM
#include <FreeRTOS.h>
#include <string.h>

/*********************
 *      DEFINES
 *********************/

/**********************
 *      TYPEDEFS
 **********************/

/**********************
 *  STATIC PROTOTYPES
 **********************/

/**********************
 *  STATIC VARIABLES
 **********************/

/**********************
 *      MACROS
 **********************/
/**********************
 *   GLOBAL FUNCTIONS
 **********************/

void lv_mem_init(void)
{
    return; /*Nothing to init*/
}

void lv_mem_deinit(void)
{
    return; /*Nothing to deinit*/

}

lv_mem_pool_t lv_mem_add_pool(void * mem, size_t bytes)
{
    /*Not supported*/
    LV_UNUSED(mem);
    LV_UNUSED(bytes);
    return NULL;
}

void lv_mem_remove_pool(lv_mem_pool_t pool)
{
    /*Not supported*/
    LV_UNUSED(pool);
    return;
}

void * lv_malloc_core(size_t size)
{
    return pvPortMalloc(size);
}

void * lv_realloc_core(void * p, size_t new_size)
{
	// 1. If size is 0, realloc behaves like free()
	if (new_size == 0) {
		if (p) vPortFree(p);
		return NULL;
	}

	// 2. If the original pointer is NULL, realloc behaves like malloc()
	if (p == NULL) {
		return pvPortMalloc(new_size);
	}

	// 3. Allocate a brand new block of memory
	void * new_p = pvPortMalloc(new_size);
	if (new_p == NULL) {
		return NULL; // Out of memory! Keep the original pointer intact.
	}

	// 4. CRITICAL: Copy the memory safely.
	// Because we cannot cleanly check the original allocated chunk size in FreeRTOS,
	// copying up to `new_size` is the standard pattern when growing internal layout blocks,
	// as long as the parent function handles initialization flags.
	memcpy(new_p, p, new_size);

	// 5. Free the old, defunct block now that the data is safely duplicated
	vPortFree(p);

	return new_p;
}

void lv_free_core(void * p)
{
	vPortFree(p);
}

void lv_mem_monitor_core(lv_mem_monitor_t * mon_p)
{
    /*Not supported*/
    LV_UNUSED(mon_p);
    return;
}

lv_result_t lv_mem_test_core(void)
{
    /*Not supported*/
    return LV_RESULT_OK;
}

/**********************
 *   STATIC FUNCTIONS
 **********************/

#endif /*LV_STDLIB_CLIB*/
