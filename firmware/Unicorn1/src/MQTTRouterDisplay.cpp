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
	int l;
	const char *s;

	s =DeviceState::singleton()->getTopicOrg();
	l = strlen(s) + strlen("/display") + 1;
	pDisplayTopic = (char *)pvPortMalloc(l);
	if (pDisplayTopic)
		sprintf(pDisplayTopic, "%s/display", s);
	else
		printf("ERROR: MQTTRouterDisplay:: Malloc Failed\n");

	s = DeviceState::singleton()->getTopicOrg();
	l += strlen(s) + 1;
	pGroupTopic = (char *)pvPortMalloc(l);
	if (pGroupTopic){
		sprintf(pGroupTopic, "%s/%s",
				pDisplayTopic,
				s);
	} else {
		printf("ERROR: MQTTRouterDisplay:: Malloc Failed\n");
	}

	s = DeviceState::singleton()->getMQTTclient();
	l += strlen(s) + 1;
	pDeviceTopic = (char *)pvPortMalloc(l);
	if (pDeviceTopic){
		sprintf(pDeviceTopic, "%s/%s",
				pGroupTopic,
				s);
	} else {
		printf("ERROR: MQTTRouterDisplay:: Malloc Failed\n");
	}
}

MQTTRouterDisplay::~MQTTRouterDisplay() {
	if (pDisplayTopic)
		vPortFree(pDisplayTopic);
	if (pGroupTopic)
		vPortFree(pGroupTopic);
	if (pDeviceTopic)
		vPortFree(pDeviceTopic);
}

void MQTTRouterDisplay::subscribe(MQTTInterface *interface){
	if (pDisplayTopic)
		interface->subToTopic(pDisplayTopic, 1);
	if (pGroupTopic)
		interface->subToTopic(pGroupTopic, 1);
	if (pDeviceTopic)
		interface->subToTopic(pDeviceTopic, 1);
}

void MQTTRouterDisplay::route(const char *topic,
		size_t topicLen,
		const void * payload,
		size_t payloadLen,
		MQTTInterface *interface){

		printf("TOPIC: %s, Payload(%d) %.*s\n", topic, payloadLen, payloadLen, (const char *)payload);
		TileAgent::singleton()->processRequest(payload, payloadLen);

}
