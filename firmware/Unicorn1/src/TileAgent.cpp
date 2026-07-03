/*
 * TileAgent.cpp
 *
 *  Created on: 3 Jul 2026
 *      Author: jondurrant
 */

#include "TileAgent.h"
#include <cstdio>
#include <cstring>
#include "FreeRTOS.h"
#include "Widgets.h"
#include "Request.h"

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
}

TileAgent::~TileAgent() {
	// TODO Auto-generated destructor stub
}

void TileAgent::run(){
	uint32_t now;
	uint32_t last = to_ms_since_boot (get_absolute_time());
	for (;;){
		size_t length = xMessageBufferReceive(
				xReqBuffer,
				pBuffer,
				REQ_BUFFER,
				1000);

		if (length > 0){
			pBuffer[length] = 0;
			printf("Received %s\n", pBuffer);

			processJSON();
			last = to_ms_since_boot (get_absolute_time());
		}
		now = to_ms_since_boot (get_absolute_time());
		if ((last + TILE_TIME_MS) < now){
			Widgets::singleton()->setLayout(0);
			last = now;
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

	}
}
