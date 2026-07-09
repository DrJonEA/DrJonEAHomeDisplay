/*
 * TileAgent.h
 *
 *  Created on: 3 Jul 2026
 *      Author: jondurrant
 */

#ifndef FIRMWARE_UNICORN1_TILEAGENT_H_
#define FIRMWARE_UNICORN1_TILEAGENT_H_

#include "pico/stdlib.h"
#include "Agent.h"
#include "tiny-json.h"
#include "FreeRTOS.h"
#include "message_buffer.h"

#define REQ_BUFFER 256
#define REQ_COUNT 5
#define REQ_JSON_POOL 10
#define IMG_BUFFER 2500

#define TILE_TIME_MS 10000

class TileAgent : public Agent {
public:
	static TileAgent * singleton();
	virtual ~TileAgent();


	/***
	 * Task main run loop
	 */
	virtual void run();

	/***
	 * Get the static depth required in words
	 * @return - words
	 */
	virtual configSTACK_DEPTH_TYPE getMaxStackSize();

	void processRequest(const void *req, size_t length);

private:
	TileAgent();
	static TileAgent * SELF;

	void processJSON();
	void processConfig();

	// Temporaty storage buffer so we can null terminate the string
	char pBuffer[REQ_BUFFER];

	// Json decoding buffer
	json_t pJsonPool[ REQ_JSON_POOL ];

	MessageBufferHandle_t xReqBuffer;

	char * pImgBuffer = NULL;

};

#endif /* FIRMWARE_UNICORN1_TILEAGENT_H_ */
