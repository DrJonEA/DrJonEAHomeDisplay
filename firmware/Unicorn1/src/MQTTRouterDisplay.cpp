/*
 * MQTTRouterDisplay.cpp
 *
 *  Created on: 1 Jul 2026
 *      Author: jondurrant
 */

#include "MQTTRouterDisplay.h"
#include "FreeRTOS.h"
#include <cstring>
#include "MQTTConfig.h"
#include "TileAgent.h"

MQTTRouterDisplay::MQTTRouterDisplay() {
	// TODO Auto-generated constructor stub

}

MQTTRouterDisplay::~MQTTRouterDisplay() {
	// TODO Auto-generated destructor stub
}

void MQTTRouterDisplay::subscribe(MQTTInterface *interface){
	interface->subToTopic(DISPLAY_TOPIC, 1);
}

void MQTTRouterDisplay::route(const char *topic,
		size_t topicLen,
		const void * payload,
		size_t payloadLen,
		MQTTInterface *interface){

		printf("TOPIC: %s, Payload(%d) %.*s\n", topic, payloadLen, payloadLen, (const char *)payload);
		TileAgent::singleton()->processRequest(payload, payloadLen);

}
