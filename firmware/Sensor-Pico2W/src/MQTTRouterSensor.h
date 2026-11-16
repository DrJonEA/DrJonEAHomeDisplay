/*
 * MQTTRouterSensor.h
 *
 * Router for a display-less sensor node. Subscribes to the same
 * <org>/display, <org>/display/<group> and <org>/display/<group>/<client>
 * topics as the Unicorn display, so the manager can send commands
 * (e.g. {"speedtest": true}, {"tz": 60}) to sensor nodes unchanged.
 *
 *  Author: jondurrant
 */

#ifndef FIRMWARE_SENSOR_PICO2W_SRC_MQTTROUTERSENSOR_H_
#define FIRMWARE_SENSOR_PICO2W_SRC_MQTTROUTERSENSOR_H_

#include "pico/stdlib.h"
#include "MQTTRouter.h"
#include "MQTTRouterTwin.h"
#include "DeviceState.h"


class MQTTRouterSensor : public MQTTRouterTwin {
public:
	MQTTRouterSensor();
	virtual ~MQTTRouterSensor();

	/***
	 * Use the interface to setup all the subscriptions
	 * @param interface
	 */
	virtual void subscribe(MQTTInterface *interface);

	/***
	 * Route the message the appropriate part of the application
	 * @param topic
	 * @param topicLen
	 * @param payload
	 * @param payloadLen
	 * @param interface
	 */
	virtual void route(const char *topic, size_t topicLen, const void * payload,
			size_t payloadLen, MQTTInterface *interface);

private:
	bool isTopic(const char *target, const char *topic, size_t topicLen);
	char * pDisplayTopic = NULL;
	char * pGroupTopic = NULL;
	char * pDeviceTopic = NULL;
};

#endif /* FIRMWARE_SENSOR_PICO2W_SRC_MQTTROUTERSENSOR_H_ */
