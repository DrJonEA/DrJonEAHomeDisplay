/***
 * main.cpp - Sensor node for Pico 2 W using wolfMQTT
 * Jon Durrant
 *
 * Display-less sensor using wolfMQTT (no twinThing / coreMQTT):
 *  - Joins WiFi, syncs time by SNTP and applies the stored timezone
 *  - Publishes temperature, humidity, rssi and mbps to
 *    <org>/sensor/<group>/<client>
 *  - Responds to {"speedtest": true} and {"tz": n} on
 *    <org>/display[/<group>[/<client>]]
 *  - Accepts JSON configuration on stdin and stores it in NVS
 */

#include "pico/cyw43_arch.h"
#include "pico/stdlib.h"
#include "hardware/watchdog.h"
#include <stdio.h>

#include "FreeRTOS.h"
#include "task.h"

#include "ahtxx/ahtxx.hpp"

#include <WifiHelper.h>
#include "MQTTClientAgent.h"
#include "DeviceState.h"
#include "SensorAgent.h"

//Check these definitions where added from the makefile
#ifndef MQTT_CLIENT
#error "MQTT_CLIENT not defined"
#endif
#ifndef MQTT_USER
#error "MQTT_USER not defined"
#endif
#ifndef MQTT_PASSWD
#error "MQTT_PASSWD not defined"
#endif
#ifndef MQTT_HOST
#error "MQTT_HOST not defined"
#endif
#ifndef MQTT_PORT
#error "MQTT_PORT not defined"
#endif
#ifndef WIFI_SSID
#error "WIFI_SSID not defined"
#endif
#ifndef WIFI_PASSWORD
#error "WIFI_PASSWORD not defined"
#endif

#define OFFLINE_REBOOT (10 * 60 * 1000)
#define SENSOR_READ_MS 3000
#define WATCHDOG_MS 5000
#define STATS_EVERY 20		// runTimeStats every N sensor loops (~1 min)

#define TASK_PRIORITY			( tskIDLE_PRIORITY + 1UL )

// AHT10 I2C wiring
#define AHT_I2C		i2c0
#define AHT_SDA		0
#define AHT_SCL		1

//#define DISABLE_WATCHDOG


//Global Variables
LIB_AHTXX *pAht10 = NULL;
volatile bool doReboot = false;


void runTimeStats(){
	TaskStatus_t *pxTaskStatusArray;
	volatile UBaseType_t uxArraySize, x;
	unsigned long ulTotalRunTime;

	uxArraySize = uxTaskGetNumberOfTasks();
	printf("Number of tasks %d\n", uxArraySize);

	pxTaskStatusArray = (TaskStatus_t *)pvPortMalloc( uxArraySize * sizeof( TaskStatus_t ) );

	if( pxTaskStatusArray != NULL ){
		uxArraySize = uxTaskGetSystemState( pxTaskStatusArray,
				uxArraySize,
				&ulTotalRunTime );

		for( x = 0; x < uxArraySize; x++ ){
			printf("Task: %d \t cPri:%d \t bPri:%d \t hw:%d \t%s\n",
					pxTaskStatusArray[ x ].xTaskNumber ,
					pxTaskStatusArray[ x ].uxCurrentPriority ,
					pxTaskStatusArray[ x ].uxBasePriority ,
					pxTaskStatusArray[ x ].usStackHighWaterMark ,
					pxTaskStatusArray[ x ].pcTaskName
					);
		}
		vPortFree( pxTaskStatusArray );
	} else {
		printf("Failed to allocate space for stats\n");
	}

	HeapStats_t heapStats;
	vPortGetHeapStats(&heapStats);
	printf("HEAP avl: %d, blocks %d, alloc: %d, free: %d\n",
			heapStats.xAvailableHeapSpaceInBytes,
			heapStats.xNumberOfFreeBlocks,
			heapStats.xNumberOfSuccessfulAllocations,
			heapStats.xNumberOfSuccessfulFrees
			);
}


/***
 * Connect to the AP using credentials held in NVS
 */
void wifiConnect(){
	DeviceState *ds = DeviceState::singleton();
	int r = -1;
	while (r != 0){
		printf("Connecting to WiFi... %s \n", ds->getSSID());
		r = cyw43_arch_wifi_connect_timeout_ms(
				ds->getSSID(),
				ds->getSSIDpwd(),
				CYW43_AUTH_WPA2_AES_PSK,
				60000);
		printf("Connect r %d\n", r);
		if (r){
			printf("Failed to join AP.\n");
			ds->WifiOffline();
			vTaskDelay(2000);
		} else {
			ds->WifiOnline();
		}
	}
}


/***
 * One line summary of the network side, for diagnosing connection issues
 */
void printNetStatus(){
	int wifi = cyw43_wifi_link_status(&cyw43_state, CYW43_ITF_STA);
	int tcpip = cyw43_tcpip_link_status(&cyw43_state, CYW43_ITF_STA);
	char ipStr[20] = "";
	if (tcpip == CYW43_LINK_UP){
		WifiHelper::getIPAddressStr(ipStr);
	}
	// wifi: 1 joined, 0 down, -1 fail, -2 no SSID, -3 bad auth
	// tcpip: 3 up with IP, 2 joined no IP, 1 joined, 0 down
	printf("[NET] wifi link %d, tcpip link %d, ip %s, rssi %d, uptime %lus\n",
			wifi, tcpip, ipStr[0] ? ipStr : "none",
			DeviceState::singleton()->getRSSI(),
			(unsigned long)(to_ms_since_boot(get_absolute_time()) / 1000));
}


void readSensors(){
	DeviceState *ds = DeviceState::singleton();

	if (pAht10 != NULL){
		float t = pAht10->AHT10_readTemperature(true);
		float h = pAht10->AHT10_readHumidity(true);

		if ((t > -1.0) && (t < 80.0)){
			ds->setTemperature(t);
		}
		if ((h >= 0.0) && (h <= 100.0)){
			ds->setHumidity(h);
		}
		printf("Update temp %.2fC, humid %.2f%%\n", t, h);
	} else {
		printf("No AHT10\n");
	}

	int32_t rssi;
	if (cyw43_wifi_get_rssi(&cyw43_state, &rssi) == 0){
		printf("WifiRSSI %d\n", rssi);
		ds->setRSSI(rssi);
	} else {
		printf("WifiRSSI fail\n");
		ds->setRSSI(0);
	}

}


void main_task(void *params){
	printf("[LIFE] main task started\n");

	// Init Wifi Adapter
	int res = cyw43_arch_init();
	if (res) {
		printf("cyw43 init %d\n", res);
		printf("failed to initialise\n");
		return;
	}

	cyw43_arch_enable_sta_mode();
	// Must follow enable_sta_mode, which resets power management to
	// CYW43_DEFAULT_PM (power save). Power save delays and drops inbound
	// packets, losing MQTT messages and ICMP echoes.
	cyw43_wifi_pm(&cyw43_state, CYW43_NONE_PM);

	// Start agent early so config can be received on stdin even if WiFi fails
	SensorAgent::singleton()->start("SensorAgent", TASK_PRIORITY);
	printf("[LIFE] sensor agent started, joining WiFi\n");

	wifiConnect();

	//Print IP Address
	char ipStr[20];
	WifiHelper::getIPAddressStr(ipStr);
	printf("[LIFE] WiFi joined, IP ADDRESS: %s\n", ipStr);

	//SNTP Activate
	WifiHelper::sntpAddServer("0.uk.pool.ntp.org");
	WifiHelper::sntpAddServer("ntp.virginmedia.com");
	WifiHelper::sntpAddServer("ntp2.npl.co.uk");

	int tz = DeviceState::singleton()->getTimeZone();
	int8_t hours = tz / 60;
	int8_t min = tz % 60;
	WifiHelper::sntpSetTimezone(hours, min);
	WifiHelper::sntpStartSync();
	printf("[LIFE] SNTP started, timezone %d minutes\n", tz);

	// MQTT client: connects, subscribes and reconnects on its own task
	DeviceState *ds = DeviceState::singleton();
	static MQTTClientAgent mqttAgent;
	SensorAgent::singleton()->setInterface(&mqttAgent);
	mqttAgent.start("MQTTClient", tskIDLE_PRIORITY + 2);
	printf("[LIFE] MQTT agent started\n");

	uint32_t online = to_ms_since_boot(get_absolute_time());
	uint32_t loops = 0;
	for (;;) {
		if ((loops++ % STATS_EVERY) == 0){
			runTimeStats();
		}
		readSensors();
		printNetStatus();
		mqttAgent.printStatus();

		vTaskDelay(SENSOR_READ_MS);

		if (cyw43_wifi_link_status(&cyw43_state, CYW43_ITF_STA) < 0){
			ds->WifiOffline();
			printf("[LIFE] AP link is down (%d), rejoining\n",
					cyw43_wifi_link_status(&cyw43_state, CYW43_ITF_STA));
			wifiConnect();
		}

		if (cyw43_wifi_link_status(&cyw43_state, CYW43_ITF_STA) >= 0){
			ds->WifiOnline();
		}

		if (ds->isMQTTOnline()){
			online = to_ms_since_boot(get_absolute_time());
		} else {
			uint32_t now = to_ms_since_boot(get_absolute_time());
			if ((now - online) > OFFLINE_REBOOT) {
				printf("[LIFE] MQTT offline for %lus, rebooting\n",
						(unsigned long)((now - online) / 1000));
				doReboot = true;
			}
		}
	}

	cyw43_arch_deinit();
}


/***
 * Keep the watchdog fed unless a reboot has been requested
 */
void watchdog_task(void *params){
#ifndef DISABLE_WATCHDOG
	watchdog_enable(WATCHDOG_MS, 1);
#endif
	for (;;){
#ifndef DISABLE_WATCHDOG
		if (!doReboot){
			watchdog_update();
		}
#endif
		vTaskDelay(100);
	}
}


void vLaunch(void) {
	TaskHandle_t task, wdTask;

	xTaskCreate(main_task, "MainThread", 1024 * 2, NULL, TASK_PRIORITY, &task);
	xTaskCreate(watchdog_task, "Watchdog", 256, NULL, TASK_PRIORITY + 1, &wdTask);

	/* Start the tasks and timer running. */
	vTaskStartScheduler();
}


int main(void){
	stdio_init_all();
	sleep_ms(2000);
	printf("GO\n");

	if (watchdog_caused_reboot()) {
		printf("Rebooted by Watchdog!\n");
	}

	//Init Temp Sensor
	static LIB_AHTXX aht10(
			AHT10_ADDRESS_0X38,
			AHT_I2C,
			AHT_SDA,
			AHT_SCL,
			100);
	aht10.AHT10_InitI2C(AHT10_SENSOR);
	aht10.AHT10_setCycleMode();
	busy_wait_ms(500);

	// Start the sensor comms
	pAht10 = NULL;
	for (int i=0; i < 5; i++){
		if (aht10.AHT10_begin() == true){
			pAht10 = &aht10;
			break;
		}
		printf("AHT10 not connected fail load calib coeff \r\n");
		busy_wait_ms(5000);
	}
	if (pAht10 != NULL){
		printf("Temp: %.2fC\n", pAht10->AHT10_readTemperature(true));
	}

	printf("Starting FreeRTOS on core 0:\n");
	vLaunch();

	return 0;
}
