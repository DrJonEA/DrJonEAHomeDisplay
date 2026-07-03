/*
 * MQTTRouterDisplay.h
 *
 *  Created on: 1 Jul 2026
 *      Author: jondurrant
 */

#ifndef EXP_PICOWMQTT_SRC_MQTTROUTERDISPLAY_H_
#define EXP_PICOWMQTT_SRC_MQTTROUTERDISPLAY_H_

#include "pico/stdlib.h"
#include "MQTTRouter.h"


#define DISPLAY_TOPIC "home/display"

class MQTTRouterDisplay : public MQTTRouter {
public:
	MQTTRouterDisplay();
	virtual ~MQTTRouterDisplay();

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


};

#endif /* EXP_PICOWMQTT_SRC_MQTTROUTERDISPLAY_H_ */
