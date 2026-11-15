/*
 * SensorAgent.h
 *
 * Display-less cut down of the Unicorn1 TileAgent. Handles:
 *  - MQTT requests: "tz" (minutes offset) and "speedtest" (HTTP POST of 100KB)
 *  - Configuration JSON received on stdin, stored in NVS
 *  - Periodic publish of sensor data to <org>/sensor/<group>/<client>
 *
 *  Author: jondurrant
 */

#ifndef FIRMWARE_SENSOR_PICO2W_SRC_SENSORAGENT_H_
#define FIRMWARE_SENSOR_PICO2W_SRC_SENSORAGENT_H_

#include "pico/stdlib.h"
#include "Agent.h"
#include "tiny-json.h"
#include "FreeRTOS.h"
#include "message_buffer.h"
#include "MQTTInterface.h"

#define REQ_BUFFER 512
#define REQ_COUNT 5
#define REQ_JSON_POOL 16
#define RESP_BUFFER 1024

#define SPEEDTEST_BYTES (100 * 1024)

#define SENSOR_PUB_MS 10000

class SensorAgent : public Agent {
public:
	static SensorAgent * singleton();
	virtual ~SensorAgent();

	/***
	 * Task main run loop
	 */
	virtual void run();

	/***
	 * Get the static depth required in words
	 * @return - words
	 */
	virtual configSTACK_DEPTH_TYPE getMaxStackSize();

	/***
	 * Queue an MQTT JSON request for processing on the agent task
	 * @param req
	 * @param length
	 */
	void processRequest(const void *req, size_t length);

	void setInterface(MQTTInterface *p);

private:
	SensorAgent();
	static SensorAgent * SELF;

	void processJSON();
	void processConfig();
	void sendSensors();
	void speedTest();

	void changeTimezone(int minOffset);

	// Temporary storage buffer so we can null terminate the string
	char pBuffer[REQ_BUFFER + 1];

	// Json decoding buffer
	json_t pJsonPool[ REQ_JSON_POOL ];

	MessageBufferHandle_t xReqBuffer = NULL;

	char * pRespBuffer = NULL;

	MQTTInterface *pInterface = NULL;

	char *pPubTopic = NULL;
};

#endif /* FIRMWARE_SENSOR_PICO2W_SRC_SENSORAGENT_H_ */
