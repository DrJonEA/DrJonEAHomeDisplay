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
#include "Widgets.h"
#include "Request.h"

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

	if (payloadLen >= DISPLAY_BUFFER){
		LogError(("Payload >= than %d", DISPLAY_BUFFER));
		return;
	}
	memcpy(pBuffer, payload, payloadLen);
	pBuffer[payloadLen] = 0;

	printf("Received %s\n", pBuffer);

	json_t const* json = json_create(pBuffer, pJsonPool, DISPLAY_JSON_POOL);
	if ( !json ) {
	 LogError(("Error json create."));
	 return ;
	}

	json_t const* item;
	json_t const* widgets;
	json_t const* widget;


	item = json_getProperty( json, "layout" );
	if (item){
		if (strcmp(json_getValue(item), "layout1") != 0){
			return;
		}
	}

	widgets = json_getProperty( json, "widgets" );
	if (!widgets  || JSON_ARRAY != json_getType(widgets)){
		 LogError(("Error, the property is not found."));
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

		if (item && strcmp(json_getValue(item), "img")==0){
			char *buf = (char *)pvPortMalloc(2500);
			Request *req = new Request(buf, 2500);
			req->get("http://jons-mbp.local.jondurrant.com:5080/img");
			printf("HTTP GET Result %d\n", req->getStatusCode());
			Widgets::singleton()->img((void *)req->getPayload(), req->getPayloadLen());
			delete(req);
			//vPortFree(buf);

		}

		widget = json_getSibling(widget);
	}


}
