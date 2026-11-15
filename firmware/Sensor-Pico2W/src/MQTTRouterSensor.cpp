/*
 * MQTTRouterSensor.cpp
 *
 *  Author: jondurrant
 */

#include "MQTTRouterSensor.h"
#include "FreeRTOS.h"
#include <cstring>
#include <cstdio>
#include "MQTTConfig.h"
#include "SensorAgent.h"

MQTTRouterSensor::MQTTRouterSensor(): MQTTRouterTwin() {
	int l;
	const char *s;

	s = DeviceState::singleton()->getTopicOrg();
	l = strlen(s) + strlen("/display") + 1;
	pDisplayTopic = (char *)pvPortMalloc(l);
	if (pDisplayTopic)
		sprintf(pDisplayTopic, "%s/display", s);
	else
		printf("ERROR: MQTTRouterSensor:: Malloc Failed\n");

	s = DeviceState::singleton()->getTopicGroup();
	l += strlen(s) + 1;
	pGroupTopic = (char *)pvPortMalloc(l);
	if (pGroupTopic && pDisplayTopic){
		sprintf(pGroupTopic, "%s/%s", pDisplayTopic, s);
	} else {
		printf("ERROR: MQTTRouterSensor:: Malloc Failed\n");
	}

	s = DeviceState::singleton()->getMQTTclient();
	l += strlen(s) + 1;
	pDeviceTopic = (char *)pvPortMalloc(l);
	if (pDeviceTopic && pGroupTopic){
		sprintf(pDeviceTopic, "%s/%s", pGroupTopic, s);
	} else {
		printf("ERROR: MQTTRouterSensor:: Malloc Failed\n");
	}
}

MQTTRouterSensor::~MQTTRouterSensor() {
	if (pDisplayTopic)
		vPortFree(pDisplayTopic);
	if (pGroupTopic)
		vPortFree(pGroupTopic);
	if (pDeviceTopic)
		vPortFree(pDeviceTopic);
}

void MQTTRouterSensor::subscribe(MQTTInterface *interface){
	MQTTRouterTwin::subscribe(interface);
	if (pDisplayTopic)
		interface->subToTopic(pDisplayTopic, 1);
	if (pGroupTopic)
		interface->subToTopic(pGroupTopic, 1);
	if (pDeviceTopic)
		interface->subToTopic(pDeviceTopic, 1);
}

void MQTTRouterSensor::route(const char *topic,
		size_t topicLen,
		const void * payload,
		size_t payloadLen,
		MQTTInterface *interface){
	MQTTRouterTwin::route(topic, topicLen, payload, payloadLen, interface);

	printf("TOPIC: %.*s, Payload(%d) %.*s\n",
			topicLen, topic, payloadLen, payloadLen, (const char *)payload);
	SensorAgent::singleton()->processRequest(payload, payloadLen);
}
