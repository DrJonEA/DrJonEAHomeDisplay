/*
 * TileAgent.cpp
 *
 *  Created on: 3 Jul 2026
 *      Author: jondurrant
 */

#include "TileAgent.h"
#include <cstdio>
#include <cstring>
#include "pico/aon_timer.h"
#include "FreeRTOS.h"
#include "cosmic_unicorn.hpp"
#include "WifiHelper.h"
#include "Widgets.h"
#include "Request.h"

#include "DeviceState.h"
#include "hardware/watchdog.h"

#include <json-maker/json-maker.h>

#include "lv_port_disp.h"


extern pimoroni::CosmicUnicorn cosmic_unicorn;



TileAgent * TileAgent::SELF = NULL;

TileAgent * TileAgent::singleton(){
	if (!SELF){
		SELF = new TileAgent;
	}
	return SELF;
}

TileAgent::TileAgent() {
	xReqBuffer = xMessageBufferCreate(REQ_BUFFER * REQ_COUNT );
	if (!xReqBuffer){
		printf("ERROR: could not allocate Request Buffer\n");
	}
	pImgBuffer = (char *)pvPortMalloc(IMG_BUFFER);
	if (!pImgBuffer){
		printf("ERROR: could not allocate Image Buffer\n");
	}

	size_t l =
			strlen(DeviceState::singleton()->getTopicOrg()) +
			strlen("/sensor/") +
			strlen(DeviceState::singleton()->getTopicGroup()) +
			1 + // /
			strlen(DeviceState::singleton()->getMQTTclient()) +
			1 ;// NULL;
	pPubTopic = (char *)pvPortMalloc(l);
	if (pPubTopic){
		sprintf(pPubTopic, "%s/sensor/%s/%s",
				DeviceState::singleton()->getTopicOrg(),
				DeviceState::singleton()->getTopicGroup(),
				DeviceState::singleton()->getMQTTclient()
				);
	}
}

TileAgent::~TileAgent() {
	if (pPubTopic)
		vPortFree(pPubTopic);
	if (xReqBuffer)
		vPortFree(xReqBuffer);
	if (pImgBuffer)
		vPortFree(pImgBuffer);
}

void TileAgent::run(){
	uint32_t now;
	uint32_t last = to_ms_since_boot (get_absolute_time());
	for (;;){
		size_t length = xMessageBufferReceive(
				xReqBuffer,
				pBuffer,
				REQ_BUFFER,
				10);

		if (length > 0){
			pBuffer[length] = 0;
			printf("Received %s\n", pBuffer);

			processJSON();
			last = to_ms_since_boot (get_absolute_time());
		}

		int count = stdio_get_until (pBuffer, REQ_BUFFER,  make_timeout_time_ms(100));
		if (count > 0){
			count += stdio_get_until (&pBuffer[count], REQ_BUFFER - count,  make_timeout_time_ms(100));
			pBuffer[count] = 0;
			printf("Have Config(%d): %s\n", count, pBuffer);
			processConfig();
		}

		now = to_ms_since_boot (get_absolute_time());
		if ((last + TILE_TIME_MS) < now){
			Widgets::singleton()->setLayout(0);
			last = now;
			sendSensors();
		}
		vTaskDelay(1000);
	}



}

configSTACK_DEPTH_TYPE TileAgent::getMaxStackSize(){
	return 1024;
}

void TileAgent::processRequest(const void *req, size_t length){
	size_t written = xMessageBufferSend(
			xReqBuffer,
			req,
			length,
			0
			);
	if (written != length){
		printf("ERROR Can't process JSON due to message buffer. Wrote %u of %u\n",
				written, length);
	}
}

void TileAgent::processJSON(){
	json_t const* json = json_create(pBuffer, pJsonPool, REQ_JSON_POOL);
	if ( !json ) {
		 printf("Error json create.\n");
		 return ;
	}

	json_t const* item;
	json_t const* widgets;
	json_t const* widget;

	item = json_getProperty( json, "layout" );
	if (item){
		if (strcmp(json_getValue(item), "layout1") == 0){
			widgets = json_getProperty( json, "widgets" );
			if (!widgets  || JSON_ARRAY != json_getType(widgets)){
				 printf("Error, the property is not found.\n");
				 return ;
			}

			widget = json_getChild(widgets);
			while (widget){
				item = json_getProperty(widget, "type");
				if (item && strcmp(json_getValue(item), "txt")==0){
					item = json_getProperty(widget, "data");

					const char *s =  json_getValue(item);
					printf("Mesg: %s\n",s);
					Widgets::singleton()->message(s);
				}

				widget = json_getSibling(widget);
			} //while
		} //if layout1

		if (strcmp(json_getValue(item), "layout2") == 0){
				widgets = json_getProperty( json, "widgets" );
				if (!widgets  || JSON_ARRAY != json_getType(widgets)){
					 printf("Error, the property is not found.\n");
					 return ;
				}

				widget = json_getChild(widgets);
				const char *msgStr = NULL;
				const char *imgName = NULL;
				while (widget){
					item = json_getProperty(widget, "type");
					if (item && strcmp(json_getValue(item), "txt")==0){
						item = json_getProperty(widget, "data");
						if (item){
							msgStr  =  json_getValue(item);
						}
					}

					if (item && strcmp(json_getValue(item), "img")==0){
						item = json_getProperty(widget, "data");
						if (item){
							imgName = json_getValue(item);
						}
					}

					widget = json_getSibling(widget);
				} //while

				if (imgName != NULL){
					Request *req = new Request(pImgBuffer, IMG_BUFFER);
					sprintf(pBuffer, "%s/32x32/%s",
							"http://jons-mbp.local.jondurrant.com:5080",
							imgName
							);
					req->get(pBuffer);
					printf("HTTP GET Result %d\n", req->getStatusCode());
					if ( req->getStatusCode() == 200){
						Widgets::singleton()->img(
								(void *)req->getPayload(),
								req->getPayloadLen(),
								msgStr
								);
					}
					delete(req);
				}
			} //if layout2
	} //LAYOUT

	item = json_getProperty( json, "brightness" );
	if (item && JSON_REAL == json_getType(item)){
		float f =  json_getReal(  item );
		if (( f <= 1.0) && ( f >= 0.0)){
			printf("Brightness set to %f\n", f);
			cosmic_unicorn.set_brightness(f);
			lv_obj_invalidate(lv_scr_act());
		} else {
			printf("Warning invalid Brightness %f\n", f);
		}
	}

	item = json_getProperty( json, "blue" );
	if (item && JSON_BOOLEAN == json_getType(item)){
		bool b =  json_getBoolean(  item );
		lv_port_reduce_blue(b);
		lv_obj_invalidate(lv_scr_act());
	}

	item = json_getProperty( json, "defcon" );
	if (item && JSON_INTEGER == json_getType(item)){
		int i =  json_getInteger(  item );
		if (i > 0 && i <=5){
			DeviceState::singleton()->setDefCon(i);
		}
	}

}

void TileAgent::processConfig(){
	json_t const* json = json_create(pBuffer, pJsonPool, REQ_JSON_POOL);
	if ( !json ) {
		 printf("Error json create.\n");
		 return ;
	}

	json_t const* item;


	item = json_getProperty( json, "tz" );
	if (item  && JSON_INTEGER == json_getType(item)){
		int tz = json_getInteger(  item );
		int oldTZ = DeviceState::singleton()->getTimeZone();
		if (tz != oldTZ){
			int8_t hours = tz / 60;
			int8_t min = tz % 60;
			WifiHelper::sntpSetTimezone(hours, min);

			struct timespec ts;
			aon_timer_get_time (&ts);
			ts.tv_sec -= oldTZ * 60;
			ts.tv_sec += tz * 60;
			aon_timer_set_time (&ts);

			DeviceState::singleton()->setTimeZone(tz);
		}
	} else {
		printf("TZ not found or wrong format\n");
	}

	item = json_getProperty( json, "ssid" );
	if (item ){
		DeviceState::singleton()->setSSID(json_getValue(item));
	}

	item = json_getProperty( json, "pwd" );
	if (item ){
		DeviceState::singleton()->setSSIDpwd(json_getValue(item));
	}

	item = json_getProperty( json, "mqttHost" );
	if (item ){
		DeviceState::singleton()->setMQTThost(json_getValue(item));
	}

	item = json_getProperty( json, "mqttClientt" );
	if (item ){
		DeviceState::singleton()->setMQTTclient(json_getValue(item));
	}

	item = json_getProperty( json, "mqttUser" );
	if (item ){
		DeviceState::singleton()->setMQTTuser(json_getValue(item));
	}

	item = json_getProperty( json, "mqttPwd" );
	if (item ){
		DeviceState::singleton()->setMQTTpwd(json_getValue(item));
	}

	item = json_getProperty( json, "httpConn" );
	if (item ){
		DeviceState::singleton()->setHTTPconn(json_getValue(item));
	}

	item = json_getProperty( json, "mqttPort" );
	if (item  && JSON_INTEGER == json_getType(item)){
		int p = json_getInteger(  item );
		DeviceState::singleton()->setMQTTport(p);
	}



	item = json_getProperty( json, "reboot" );
	if (item ){
		watchdog_enable(100, 1);
	}
}

void TileAgent::sendSensors(){
	char *s = pBuffer;
	size_t rem = REQ_BUFFER;

	if (!pInterface){
		return;
	}
	if (!pPubTopic){
		return;
	}

	s = json_objOpen( s , NULL, &rem );

	s = json_str(s, "id", pInterface->getId(), &rem);
	s =  json_double(
			s,
			"temperature",
			DeviceState::singleton()->getTemperature(),
			&rem );
	s =  json_double(
			s,
			"humidity",
			DeviceState::singleton()->getHumidity(),
			&rem );

	s = json_objClose( s , &rem );
	s = json_objClose(s, &rem);

	pInterface->pubToTopic(
			pPubTopic,
			pBuffer,
			strlen(pBuffer),
			1,
			false);
}


void TileAgent::setInterface(MQTTInterface *p){
	pInterface = p;
}
