/***
 * main.cpp - LED Control over MQTT
 * Jon Durrant
 * 4-Oct-2022
 *
 * Control an LED over MQTT using Topic
 * TNG/<<device>>/TPC/LED
 * with JSON payload as boolean state
 * e.g. {"on": True}
 *
 */

#include "pico/cyw43_arch.h"
#include "pico/stdlib.h"
#include <stdio.h>

extern "C"{
#include "lv_port_disp.h"
}
#include "Widgets.h"

#include "lwip/ip4_addr.h"
#include "lwip/sockets.h"
#include "lwip/dns.h"

#include "FreeRTOS.h"
#include "task.h"
#include "queue.h"
#include <stdio.h>

#include "ahtxx/ahtxx.hpp"


#include "MQTTAgent.h"
#include <WifiHelper.h>
#include "BlinkAgent.h"
#include "MQTTRouterDisplay.h"
#include "DeviceState.h"
#include "TileAgent.h"

//Check these definitions where added from the makefile
#ifndef MQTT_CLIENT
#error "MQTT_CLIENT not defined"
#endif
#ifndef MQTT_USER
#error "MQTT_PASSWD not defined"
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

// LED PAD defintions
#define PULSE_LED  	   0
#define CONTROL_LED	  12


#define TASK_PRIORITY			( tskIDLE_PRIORITY + 1UL )


//Global Variables
LIB_AHTXX *pAht10 = NULL;


void runTimeStats(   ){
	//char pcWriteBuffer[120] = "";
	TaskStatus_t *pxTaskStatusArray;
	volatile UBaseType_t uxArraySize, x;
	unsigned long ulTotalRunTime;

   /* Make sure the write buffer does not contain a string. */
   //*pcWriteBuffer = 0x00;

   /* Take a snapshot of the number of tasks in case it changes while this
   function is executing. */
   uxArraySize = uxTaskGetNumberOfTasks();
   printf("Number of tasks %d\n", uxArraySize);

   /* Allocate a TaskStatus_t structure for each task.  An array could be
   allocated statically at compile time. */
   pxTaskStatusArray = (TaskStatus_t *)pvPortMalloc( uxArraySize * sizeof( TaskStatus_t ) );

   if( pxTaskStatusArray != NULL ){
      /* Generate raw status information about each task. */
      uxArraySize = uxTaskGetSystemState( pxTaskStatusArray,
                                 uxArraySize,
                                 &ulTotalRunTime );



	 /* For each populated position in the pxTaskStatusArray array,
	 format the raw data as human readable ASCII data. */
	 for( x = 0; x < uxArraySize; x++ )
	 {
		 printf("Task: %d \t cPri:%d \t bPri:%d \t hw:%d \t%s\n",
				pxTaskStatusArray[ x ].xTaskNumber ,
				pxTaskStatusArray[ x ].uxCurrentPriority ,
				pxTaskStatusArray[ x ].uxBasePriority ,
				pxTaskStatusArray[ x ].usStackHighWaterMark ,
				pxTaskStatusArray[ x ].pcTaskName
				);
	 }


      /* The array is no longer needed, free the memory it consumes. */
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


void main_task(void *params){

	printf("Main task started\n");

	//Start up pulse blink LED
	//BlinkAgent blink(PULSE_LED);
	//blink.start("Blink", TASK_PRIORITY);


	// Init Wifi Adapter
	int res = cyw43_arch_init();
	if (res) {
		printf("cyw42 init %d\n", res);
		printf("failed to initialise\n");
		return;
	}

	cyw43_wifi_pm(&cyw43_state ,CYW43_AGGRESSIVE_PM);

	cyw43_arch_enable_sta_mode();
	printf("Connecting to WiFi... %s \n",  DeviceState::singleton()->getSSID()); //WIFI_SSID);

	//Loop trying to connect to Wifi
	int r =-1;
	while (r < 0){
		r = cyw43_arch_wifi_connect_timeout_ms(WIFI_SSID, WIFI_PASSWORD, CYW43_AUTH_WPA2_AES_PSK, 60000);
		printf("Connect r %d\n", r);
		if (r){
			printf("Failed to join AP.\n");
			DeviceState::singleton()->WifiOffline();
			 vTaskDelay(2000);
		} else {
			DeviceState::singleton()->WifiOnline();
		}
	}

	//Print IP Address
	char ipStr[20];
	WifiHelper::getIPAddressStr(ipStr);
	printf("IP ADDRESS: %s\n", ipStr);

	//SNTP Activate
	WifiHelper::sntpAddServer("ntp.virginmedia.com");
	WifiHelper::sntpAddServer("ntp2.npl.co.uk");
	WifiHelper::sntpAddServer("0.uk.pool.ntp.org");
	int tz = DeviceState::singleton()->getTimeZone();
	int8_t hours = tz / 60;
	int8_t min = tz % 60;
	WifiHelper::sntpSetTimezone(hours, min);
	WifiHelper::sntpStartSync();



	// Setup for MQTT Connection
	/*
	char mqttTarget[] = MQTT_HOST;
	int mqttPort = MQTT_PORT;
	char mqttClient[] = MQTT_CLIENT;
	char mqttUser[] = MQTT_USER;
	char mqttPwd[] = MQTT_PASSWD;
	*/
	char *mqttTarget 	= DeviceState::singleton()->getMQTThost();
	int mqttPort 			= DeviceState::singleton()->getMQTTport();
	char *mqttClient 	= DeviceState::singleton()->getMQTTclient();
	char *mqttUser 		= DeviceState::singleton()->getMQTTuser();
	char *mqttPwd 		= DeviceState::singleton()->getMQTTpwd();
	MQTTRouterDisplay mqttRouter;
	MQTTAgent mqttAgent;


	mqttAgent.credentials(mqttUser, mqttPwd, mqttClient);
	mqttAgent.setRouter(&mqttRouter);

	printf("Connecting to: %s(%d)\n", mqttTarget, mqttPort);
	printf("Client id: %.4s...\n", mqttAgent.getId());
	printf("User id: %.4s...\n", mqttUser);

	mqttAgent.setObserver(DeviceState::singleton());
	mqttAgent.mqttConnect(mqttTarget, mqttPort, true);
	mqttAgent.start(tskIDLE_PRIORITY+2);



    while(true) {

    	runTimeStats();

    	if (pAht10 != NULL){
    		 DeviceState::singleton()->setTemperature(pAht10->AHT10_readTemperature(false));
    		 DeviceState::singleton()->setHumidity(pAht10->AHT10_readHumidity(false));
		} else {
			printf("No AHT10\n");
		}

        vTaskDelay(3000);



        if (cyw43_wifi_link_status(&cyw43_state, CYW43_ITF_STA) < 0){
        	DeviceState::singleton()->WifiOffline();
        	printf("AP Link is down\n");
        	while (r < 0){
				r = cyw43_arch_wifi_connect_timeout_ms(WIFI_SSID, WIFI_PASSWORD, CYW43_AUTH_WPA2_AES_PSK, 60000);
				printf("Connect r %d\n", r);
				if (r){
					printf("Failed to join AP.\n");
					 vTaskDelay(2000);
				}
			}
        }

        if (cyw43_wifi_link_status(&cyw43_state, CYW43_ITF_STA) >= 0){
        	DeviceState::singleton()->WifiOnline();
        }



    }



    cyw43_arch_deinit();
}


void lvgl_task(void* params){
	lv_init();
	lv_port_disp_init();
	Widgets *widgets = Widgets::singleton();

	lv_tick_set_cb(xTaskGetTickCount);
	widgets->init();
	TileAgent::singleton()->start("TileAgent", TASK_PRIORITY);
	for(;;){
	  for (int i=0; i < 100; i++){
		  lv_timer_handler();
		 vTaskDelay(1);
	  }
	  //printf("Tick\n");
	}
}



void vLaunch( void) {
    TaskHandle_t task, lvglTask;

    xTaskCreate(main_task, "MainThread", 1024 * 1, NULL, TASK_PRIORITY, &task);
	xTaskCreate(lvgl_task, "LVGLThread", 1024*2, NULL, TASK_PRIORITY+1, &lvglTask);

    /* Start the tasks and timer running. */
    vTaskStartScheduler();
}



int main( void )
{
    stdio_init_all();
    sleep_ms(2000);
    printf("GO\n");

    //Init Temp Sensor
    LIB_AHTXX aht10(
	  AHT10_ADDRESS_0X38,
	  i2c0,
	  4,
	  5,
	  100);
	aht10.AHT10_InitI2C(AHT10_SENSOR);
	aht10.AHT10_setCycleMode();
	busy_wait_ms(500);

	// Start the sensor comms
	pAht10 = NULL;
	for (int i=0; i < 5; i++){
		if (aht10.AHT10_begin() == true){
			pAht10 = & aht10;
			break;
		}
		printf("AHT10 not connected fail load calib coeff \r\n");
		busy_wait_ms(5000);
	}
	if (pAht10 != NULL){
		printf("Temp: %.2fC\n", pAht10->AHT10_readTemperature(true));
	}

	//lv_init();
	//v_port_disp_init();

    /* Configure the hardware ready to run the demo. */
    const char *rtos_name;
    rtos_name = "FreeRTOS";
    printf("Starting %s on core 0:\n", rtos_name);
    vLaunch();

    return 0;
}
