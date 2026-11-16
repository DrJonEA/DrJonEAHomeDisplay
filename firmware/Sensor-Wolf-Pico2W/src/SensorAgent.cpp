/*
 * SensorAgent.cpp
 *
 *  Author: jondurrant
 */

#include "SensorAgent.h"
#include <cstdio>
#include <cstring>
#include "pico/aon_timer.h"
#include "hardware/watchdog.h"
#include "FreeRTOS.h"
#include "WifiHelper.h"
#include "Request.h"

#include "DeviceState.h"

#include <json-maker/json-maker.h>


SensorAgent * SensorAgent::SELF = NULL;

SensorAgent * SensorAgent::singleton(){
	if (!SELF){
		SELF = new SensorAgent;
	}
	return SELF;
}

SensorAgent::SensorAgent() {
	xReqBuffer = xMessageBufferCreate(REQ_BUFFER * REQ_COUNT );
	if (!xReqBuffer){
		printf("ERROR: could not allocate Request Buffer\n");
	}
	pRespBuffer = (char *)pvPortMalloc(RESP_BUFFER);
	if (!pRespBuffer){
		printf("ERROR: could not allocate Response Buffer\n");
	}

	DeviceState *ds = DeviceState::singleton();
	size_t l =
			strlen(ds->getTopicOrg()) +
			strlen("/sensor/") +
			strlen(ds->getTopicGroup()) +
			1 + // /
			strlen(ds->getMQTTclient()) +
			1 ;// NULL;
	pPubTopic = (char *)pvPortMalloc(l);
	if (pPubTopic){
		sprintf(pPubTopic, "%s/sensor/%s/%s",
				ds->getTopicOrg(),
				ds->getTopicGroup(),
				ds->getMQTTclient()
				);
		printf("Sensor publish topic: %s\n", pPubTopic);
	}
}

SensorAgent::~SensorAgent() {
	if (pPubTopic)
		vPortFree(pPubTopic);
	if (xReqBuffer)
		vMessageBufferDelete(xReqBuffer);
	if (pRespBuffer)
		vPortFree(pRespBuffer);
}

void SensorAgent::run(){
	uint32_t now;
	uint32_t last = to_ms_since_boot (get_absolute_time());
	for (;;){
		// MQTT requests
		if (xReqBuffer){
			size_t length = xMessageBufferReceive(
					xReqBuffer,
					pBuffer,
					REQ_BUFFER,
					10);

			if (length > 0){
				pBuffer[length] = 0;
				printf("Received %s\n", pBuffer);
				processJSON();
			}
		}

		// Configuration on stdin
		int pos = 0;
		int count = stdio_get_until (pBuffer, REQ_BUFFER,  make_timeout_time_ms(100));
		while (count > 0){
			pos += count;
			if (pos >= REQ_BUFFER){
				break;
			}
			count = stdio_get_until (&pBuffer[pos], REQ_BUFFER - pos,  make_timeout_time_ms(100));
		}
		if (pos > 0){
			if (pos > REQ_BUFFER){
				pos = REQ_BUFFER;
			}
			pBuffer[pos] = 0;
			printf("Have Config(%d): %s\n", pos, pBuffer);
			processConfig();
		}

		// Periodic sensor publish
		now = to_ms_since_boot (get_absolute_time());
		if ((now - last) > SENSOR_PUB_MS){
			last = now;
			sendSensors();
		}
		vTaskDelay(1000);
	}
}

configSTACK_DEPTH_TYPE SensorAgent::getMaxStackSize(){
	return 1024;
}

void SensorAgent::processRequest(const void *req, size_t length){
	if (!xReqBuffer){
		return;
	}
	if (length > REQ_BUFFER){
		printf("ERROR request too long %u > %u\n", length, REQ_BUFFER);
		return;
	}
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

void SensorAgent::processJSON(){
	json_t const* json = json_create(pBuffer, pJsonPool, REQ_JSON_POOL);
	if ( !json ) {
		 printf("Error json create.\n");
		 return ;
	}

	json_t const* item;

	item = json_getProperty( json, "tz" );
	if (item && JSON_INTEGER == json_getType(item)){
		int tz =  json_getInteger(  item );
		changeTimezone(tz);
	}

	item = json_getProperty( json, "speedtest" );
	if (item){
		speedTest();
	}
}

/***
 * POST 100KB to <httpConn>/speedtest and record the upload rate in Mbps
 */
void SensorAgent::speedTest(){
	if (!pRespBuffer){
		return;
	}
	char url[128];
	snprintf(url, sizeof(url), "%s/speedtest",
			DeviceState::singleton()->getHTTPconn());

	Request *req = new Request(pRespBuffer, RESP_BUFFER);
	// Any 100KB will do as the payload, so just send the start of SRAM
	const char * data = (const char *) SRAM_BASE;
	uint32_t start = to_ms_since_boot (get_absolute_time());
	if (req->postPayload(url, data, SPEEDTEST_BYTES)){
		uint32_t stop = to_ms_since_boot (get_absolute_time());
		printf("HTTP POST %s Result %d in %lums\n", url, req->getStatusCode(), (stop - start));
		if ((req->getStatusCode() == 200) && (stop > start)){
			float seconds = (float)(stop - start) / 1000.0;
			float mbps = 0.1 / seconds * 8.0;
			DeviceState::singleton()->setNetSpeed(mbps);
			printf("Speed test %.2f Mbps\n", mbps);
			sendSensors();
		}
	} else {
		printf("HTTP POST %s failed\n", url);
	}
	delete(req);
}

void SensorAgent::processConfig(){
	json_t const* json = json_create(pBuffer, pJsonPool, REQ_JSON_POOL);
	if ( !json ) {
		 printf("Error json create.\n");
		 return ;
	}

	DeviceState *ds = DeviceState::singleton();
	json_t const* item;

	item = json_getProperty( json, "tz" );
	if (item  && JSON_INTEGER == json_getType(item)){
		int tz = json_getInteger(  item );
		changeTimezone(tz);
	} else {
		printf("TZ not found or wrong format\n");
	}

	item = json_getProperty( json, "ssid" );
	if (item ){
		ds->setSSID(json_getValue(item));
	}

	item = json_getProperty( json, "pwd" );
	if (item ){
		ds->setSSIDpwd(json_getValue(item));
	}

	item = json_getProperty( json, "mqttHost" );
	if (item ){
		ds->setMQTThost(json_getValue(item));
	}

	item = json_getProperty( json, "mqttClient" );
	if (item ){
		ds->setMQTTclient(json_getValue(item));
	}

	item = json_getProperty( json, "mqttUser" );
	if (item ){
		ds->setMQTTuser(json_getValue(item));
	}

	item = json_getProperty( json, "mqttPwd" );
	if (item ){
		ds->setMQTTpwd(json_getValue(item));
	}

	item = json_getProperty( json, "httpConn" );
	if (item ){
		ds->setHTTPconn(json_getValue(item));
	}

	item = json_getProperty( json, "mqttPort" );
	if (item  && JSON_INTEGER == json_getType(item)){
		int p = json_getInteger(  item );
		ds->setMQTTport(p);
	}

	item = json_getProperty( json, "org" );
	if (item ){
		ds->setTopicOrg(json_getValue(item));
	}

	item = json_getProperty( json, "group" );
	if (item ){
		ds->setTopicGroup(json_getValue(item));
	}

	ds->storeConfig();

	item = json_getProperty( json, "reboot" );
	if (item ){
		printf("Rebooting\n");
		vTaskDelay(100);
		watchdog_reboot(0, 0, 0);
		for (;;){
			// Wait for reboot
		}
	}
}

void SensorAgent::sendSensors(){
	char *s = pBuffer;
	size_t rem = REQ_BUFFER;

	if (!pInterface || !pInterface->isConnected()){
		return;
	}
	if (!pPubTopic){
		return;
	}

	DeviceState *ds = DeviceState::singleton();

	s = json_objOpen( s , NULL, &rem );
	s = json_str(s, "id", pInterface->getId(), &rem);
	s = json_double(s, "temperature", ds->getTemperature(), &rem );
	s = json_double(s, "humidity", ds->getHumidity(), &rem );
	s = json_double(s, "mbps", ds->getNetSpeed(), &rem );
	s = json_int(s, "rssi", ds->getRSSI(), &rem );
	s = json_objClose( s , &rem );
	s = json_end( s, &rem );

	pInterface->publish(
			pPubTopic,
			pBuffer,
			strlen(pBuffer),
			1);
}


void SensorAgent::setInterface(MQTTClientAgent *p){
	pInterface = p;
}

void SensorAgent::changeTimezone(int tz){
	int oldTZ = DeviceState::singleton()->getTimeZone();
	if (tz != oldTZ){
		int8_t hours = tz / 60;
		int8_t min = tz % 60;
		WifiHelper::sntpSetTimezone(hours, min);

		if(aon_timer_is_running()){
			struct timespec ts;
			aon_timer_get_time (&ts);
			ts.tv_sec -= oldTZ * 60;
			ts.tv_sec += tz * 60;
			aon_timer_set_time (&ts);
		}

		DeviceState::singleton()->setTimeZone(tz);
		DeviceState::singleton()->storeConfig();
		printf("Timezone set to %d minutes\n", tz);
	}
}
