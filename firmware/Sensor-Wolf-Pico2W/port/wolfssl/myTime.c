#include "pico/stdlib.h"
#include "pico/aon_timer.h"

#include "wolfssl/wolfcrypt/camellia.h"
#include <time.h>


/***
 * Wall clock in seconds since the epoch, used by wolfSSL (XTIME) to check
 * certificate validity dates. The AON timer is set by SNTP; until then this
 * returns 0, and certificates fail as not yet valid.
 * Note WifiHelper sets the AON timer to local time (UTC + timezone offset).
 */
unsigned long my_time(time_t* timer){
	unsigned long t = 0;
	struct timespec ts;
	if (aon_timer_is_running() && aon_timer_get_time(&ts)){
		t = (unsigned long)ts.tv_sec;
	}
	if (timer){
		*timer = (time_t)t;
	}
	return t;
}

word32 LowResTimer(void) {
   /*
   write your own clock tick function if don't want time(0)
   needs second accuracy but doesn't have to correlated to EPOCH
   */
   return (word32) (to_ms_since_boot (get_absolute_time()) / 1000);
}



//https://deemocean.com/2022/10/02/rp2040-randomness-and-ring-oscillator/

// ROSC address and RANDOMBIT offset differ between RP2040 and RP2350,
// so take them from the SDK register headers for the target chip
#include "hardware/regs/addressmap.h"
#include "hardware/regs/rosc.h"

// return random number by ROSC between 0-2^N
// N should be in [0,32]
unsigned int ROrand(int N)
{
  static volatile uint32_t *randbit_reg = (uint32_t *)(ROSC_BASE + ROSC_RANDOMBIT_OFFSET);
  unsigned int random = 0;
  for (int i = 0; i < N; i++)
  {
    unsigned int random_bit = 0x1 & (*randbit_reg);
    random = random << 1 | random_bit;
  }
  return random;
}


unsigned int my_rng_seed_gen(void){
	return ROrand(32);

}


