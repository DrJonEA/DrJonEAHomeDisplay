/*
 * MQTTClientAgent.cpp
 *
 *  Author: jondurrant
 */

#include "MQTTClientAgent.h"
#include <cstdio>
#include <cstring>
#include <cerrno>

#include "pico/cyw43_arch.h"
#include "DeviceState.h"
#include "SensorAgent.h"

// lwIP socket headers last: their compatibility macros (connect, poll, ...)
// would otherwise rewrite names in the SDK and project headers
#include "lwip/sockets.h"
#include "lwip/netdb.h"


MQTTClientAgent::MQTTClientAgent() {
	memset(&xClient, 0, sizeof(xClient));
	memset(&xNet, 0, sizeof(xNet));
	memset(xSubTopics, 0, sizeof(xSubTopics));

	xPubQueue = xQueueCreate(MQTT_PUB_QUEUE_LEN, sizeof(MQTTPubReq));
	if (!xPubQueue){
		printf("ERROR: MQTTClientAgent could not allocate publish queue\n");
	}

	// Subscriptions within the <org>/display hierarchy
	DeviceState *ds = DeviceState::singleton();
	const char *org = ds->getTopicOrg();
	const char *grp = ds->getTopicGroup();
	const char *client = ds->getMQTTclient();
	size_t l = strlen(org) + strlen("/display/") + strlen(grp) + 1 + strlen(client) + 1;

	for (int i=0; i < MQTT_SUB_COUNT; i++){
		pSubTopics[i] = (char *)pvPortMalloc(l);
		if (!pSubTopics[i]){
			printf("ERROR: MQTTClientAgent malloc failed\n");
		}
	}
	if (pSubTopics[0])
		sprintf(pSubTopics[0], "%s/display", org);
	if (pSubTopics[1])
		sprintf(pSubTopics[1], "%s/display/%s", org, grp);
	if (pSubTopics[2])
		sprintf(pSubTopics[2], "%s/display/%s/%s", org, grp, client);
}

MQTTClientAgent::~MQTTClientAgent() {
	for (int i=0; i < MQTT_SUB_COUNT; i++){
		if (pSubTopics[i])
			vPortFree(pSubTopics[i]);
	}
	if (xPubQueue)
		vQueueDelete(xPubQueue);
}

const char * MQTTClientAgent::getId(){
	return DeviceState::singleton()->getMQTTclient();
}

bool MQTTClientAgent::isConnected(){
	return xConnected;
}

MQTTState MQTTClientAgent::getState(){
	return xState;
}

const char * MQTTClientAgent::stateToString(MQTTState s){
	switch(s){
	case MQTT_STATE_INIT:			return "INIT";
	case MQTT_STATE_WAIT_WIFI:		return "WAIT_WIFI";
	case MQTT_STATE_DNS:			return "DNS";
	case MQTT_STATE_TCP_CONNECT:	return "TCP_CONNECT";
	case MQTT_STATE_MQTT_CONNECT:	return "MQTT_CONNECT";
	case MQTT_STATE_SUBSCRIBE:		return "SUBSCRIBE";
	case MQTT_STATE_ONLINE:			return "ONLINE";
	case MQTT_STATE_BACKOFF:		return "BACKOFF";
	case MQTT_STATE_FATAL:			return "FATAL";
	}
	return "?";
}

void MQTTClientAgent::setState(MQTTState s){
	if (s != xState){
		uint32_t now = to_ms_since_boot(get_absolute_time());
		printf("[MQTT] state %s -> %s (after %lums)\n",
				stateToString(xState), stateToString(s),
				(unsigned long)(now - xStateSince));
		xState = s;
		xStateSince = now;
	}
}

void MQTTClientAgent::printStatus(){
	uint32_t now = to_ms_since_boot(get_absolute_time());
	printf("[MQTT] status: state=%s for %lus, broker=%s(%s):%d, "
			"attempts=%lu, failures=%lu, pub=%lu, rx=%lu, "
			"lastErr=%d at %s\n",
			stateToString(xState),
			(unsigned long)((now - xStateSince) / 1000),
			DeviceState::singleton()->getMQTThost(),
			pBrokerIP[0] ? pBrokerIP : "unresolved",
			DeviceState::singleton()->getMQTTport(),
			(unsigned long)xAttempts, (unsigned long)xFailures,
			(unsigned long)xPubCount, (unsigned long)xRxCount,
			xLastError, pLastErrorWhere);
}

configSTACK_DEPTH_TYPE MQTTClientAgent::getMaxStackSize(){
	return 1536;
}

word16 MQTTClientAgent::nextPacketId(){
	xPacketId++;
	if (xPacketId == 0){
		xPacketId = 1;
	}
	return xPacketId;
}

bool MQTTClientAgent::publish(const char *topic, const void *payload, size_t len, uint8_t qos){
	if (!xPubQueue){
		return false;
	}
	if ((strlen(topic) >= MQTT_PUB_TOPIC_LEN) || (len > MQTT_PUB_PAYLOAD_LEN)){
		printf("ERROR: MQTT publish too large for queue\n");
		return false;
	}
	MQTTPubReq req;
	strcpy(req.topic, topic);
	memcpy(req.payload, payload, len);
	req.len = len;
	req.qos = qos;
	if (xQueueSendToBack(xPubQueue, &req, 0) != pdTRUE){
		printf("[MQTT] WARNING: publish queue full (state %s), message dropped\n",
				stateToString(xState));
		return false;
	}
	return true;
}


void MQTTClientAgent::run(){
	printf("[MQTT] agent task started\n");
	xStateSince = to_ms_since_boot(get_absolute_time());
	xNet.context = this;
	xNet.connect = MQTTClientAgent::netConnect;
	xNet.read = MQTTClientAgent::netRead;
	xNet.write = MQTTClientAgent::netWrite;
	xNet.disconnect = MQTTClientAgent::netDisconnect;

	int rc = MqttClient_Init(&xClient, &xNet, MQTTClientAgent::msgCB,
			pTxBuf, MQTT_TX_BUF_LEN,
			pRxBuf, MQTT_RX_BUF_LEN,
			MQTT_CMD_TIMEOUT_MS);
	if (rc != MQTT_CODE_SUCCESS){
		printf("[MQTT] ERROR: MqttClient_Init %s (%d)\n",
				MqttClient_ReturnCodeToString(rc), rc);
		setState(MQTT_STATE_FATAL);
		vTaskDelete(NULL);
		return;
	}
	xClient.ctx = this;

	int lastLink = 99;
	for (;;){
		if (!xConnected){
			// cyw43_wifi_link_status() never reports LINK_UP, only JOIN.
			// The tcpip status reports UP once we also have an IP address.
			int link = cyw43_tcpip_link_status(&cyw43_state, CYW43_ITF_STA);
			if (link != CYW43_LINK_UP){
				setState(MQTT_STATE_WAIT_WIFI);
				if (link != lastLink){
					printf("[MQTT] waiting for network, tcpip link status %d\n", link);
					lastLink = link;
				}
				vTaskDelay(MQTT_RECON_DELAY_MS);
				continue;
			}
			lastLink = link;
			if (!brokerConnect()){
				xFailures++;
				brokerDisconnect();
				setState(MQTT_STATE_BACKOFF);
				printf("[MQTT] connect attempt %lu failed at %s (%d), retry in %dms\n",
						(unsigned long)xAttempts, pLastErrorWhere, xLastError,
						MQTT_RECON_DELAY_MS);
				vTaskDelay(MQTT_RECON_DELAY_MS);
				continue;
			}
		}

		// Receive messages, wolfMQTT also sends keep-alive pings from here
		rc = MqttClient_WaitMessage(&xClient, MQTT_WAIT_MS);
		if ((rc != MQTT_CODE_SUCCESS) && (rc != MQTT_CODE_ERROR_TIMEOUT)){
			printf("[MQTT] WaitMessage failed: %s (%d)\n",
					MqttClient_ReturnCodeToString(rc), rc);
			xLastError = rc;
			strcpy(pLastErrorWhere, "WaitMessage");
			brokerDisconnect();
			continue;
		}

		if (!sendQueued()){
			brokerDisconnect();
		}
	}
}

bool MQTTClientAgent::brokerConnect(){
	DeviceState *ds = DeviceState::singleton();
	const char *host = ds->getMQTThost();
	int port = ds->getMQTTport();

	xAttempts++;
	printf("[MQTT] connect attempt %lu to %s:%d client '%s' user '%s' pwd %s\n",
			(unsigned long)xAttempts, host, port,
			ds->getMQTTclient(), ds->getMQTTuser(),
			(strlen(ds->getMQTTpwd()) > 0) ? "set" : "EMPTY");
	if ((strlen(host) == 0) || (port <= 0) || (port > 65535)){
		printf("[MQTT] ERROR: broker host/port not configured\n");
		xLastError = MQTT_CODE_ERROR_BAD_ARG;
		strcpy(pLastErrorWhere, "config");
		return false;
	}

	// DNS and TCP states are set inside netConnect
	int rc = MqttClient_NetConnect(&xClient, host, (word16)port,
			MQTT_CMD_TIMEOUT_MS, 0, NULL);
	if (rc != MQTT_CODE_SUCCESS){
		printf("[MQTT] NetConnect failed: %s (%d)\n",
				MqttClient_ReturnCodeToString(rc), rc);
		xLastError = rc;
		if (xState == MQTT_STATE_DNS){
			strcpy(pLastErrorWhere, "DNS");
		} else {
			strcpy(pLastErrorWhere, "TCP connect");
		}
		return false;
	}
	printf("[MQTT] TCP connected to %s:%d\n", pBrokerIP, port);
	setState(MQTT_STATE_MQTT_CONNECT);

	MqttConnect conn;
	memset(&conn, 0, sizeof(conn));
	conn.keep_alive_sec = MQTT_KEEP_ALIVE_SEC;
	conn.clean_session = 1;
	conn.client_id = ds->getMQTTclient();
	conn.username = ds->getMQTTuser();
	conn.password = ds->getMQTTpwd();
	conn.protocol_level = MQTT_CONNECT_PROTOCOL_LEVEL_4;

	rc = MqttClient_Connect(&xClient, &conn);
	if (rc != MQTT_CODE_SUCCESS){
		printf("[MQTT] CONNECT failed: %s (%d)\n",
				MqttClient_ReturnCodeToString(rc), rc);
		xLastError = rc;
		strcpy(pLastErrorWhere, "MQTT CONNECT");
		return false;
	}
	if (conn.ack.return_code != MQTT_CONNECT_ACK_CODE_ACCEPTED){
		const char *why = "unknown";
		switch (conn.ack.return_code){
		case 1: why = "unacceptable protocol version"; break;
		case 2: why = "client id rejected"; break;
		case 3: why = "server unavailable"; break;
		case 4: why = "bad user name or password"; break;
		case 5: why = "not authorised"; break;
		}
		printf("[MQTT] CONNACK refused by broker: %d (%s)\n",
				conn.ack.return_code, why);
		xLastError = conn.ack.return_code;
		strcpy(pLastErrorWhere, "CONNACK");
		return false;
	}
	printf("[MQTT] CONNACK accepted, client '%s'\n", conn.client_id);

	setState(MQTT_STATE_SUBSCRIBE);
	if (!brokerSubscribe()){
		xLastError = -1;
		strcpy(pLastErrorWhere, "SUBSCRIBE");
		return false;
	}

	xConnected = true;
	ds->MQTTOnline();
	setState(MQTT_STATE_ONLINE);
	return true;
}

bool MQTTClientAgent::brokerSubscribe(){
	int count = 0;
	for (int i=0; i < MQTT_SUB_COUNT; i++){
		if (pSubTopics[i]){
			memset(&xSubTopics[count], 0, sizeof(MqttTopic));
			xSubTopics[count].topic_filter = pSubTopics[i];
			xSubTopics[count].qos = MQTT_QOS_1;
			count++;
		}
	}
	if (count == 0){
		return true;
	}

	MqttSubscribe sub;
	memset(&sub, 0, sizeof(sub));
	sub.packet_id = nextPacketId();
	sub.topic_count = count;
	sub.topics = xSubTopics;

	int rc = MqttClient_Subscribe(&xClient, &sub);
	if (rc != MQTT_CODE_SUCCESS){
		printf("[MQTT] SUBSCRIBE failed: %s (%d)\n",
				MqttClient_ReturnCodeToString(rc), rc);
		return false;
	}
	for (int i=0; i < count; i++){
		// SUBACK return code: 0-2 granted QoS, 0x80 refused (e.g. ACL)
		printf("[MQTT] subscribed %s suback 0x%02x%s\n",
				xSubTopics[i].topic_filter, xSubTopics[i].return_code,
				(xSubTopics[i].return_code == 0x80) ? " REFUSED" : "");
	}
	return true;
}

/***
 * Publish everything waiting in the queue
 * @return false on a network failure
 */
bool MQTTClientAgent::sendQueued(){
	if (!xPubQueue){
		return true;
	}
	while (xQueueReceive(xPubQueue, &xPubReq, 0) == pdTRUE){
		MqttPublish pub;
		memset(&pub, 0, sizeof(pub));
		pub.topic_name = xPubReq.topic;
		pub.qos = (xPubReq.qos > 0) ? MQTT_QOS_1 : MQTT_QOS_0;
		pub.packet_id = (pub.qos == MQTT_QOS_0) ? 0 : nextPacketId();
		pub.buffer = (::byte *)xPubReq.payload;
		pub.total_len = xPubReq.len;

		int rc = MqttClient_Publish(&xClient, &pub);
		if (rc != MQTT_CODE_SUCCESS){
			printf("[MQTT] PUBLISH to %s failed: %s (%d)\n",
					xPubReq.topic, MqttClient_ReturnCodeToString(rc), rc);
			xLastError = rc;
			strcpy(pLastErrorWhere, "PUBLISH");
			return false;
		}
		xPubCount++;
		printf("[MQTT] published %u bytes to %s\n", xPubReq.len, xPubReq.topic);
	}
	return true;
}

void MQTTClientAgent::brokerDisconnect(){
	if (xConnected){
		MqttClient_Disconnect(&xClient);
	}
	MqttClient_NetDisconnect(&xClient);
	if (xConnected){
		printf("[MQTT] disconnected after %lus online\n",
				(unsigned long)((to_ms_since_boot(get_absolute_time()) - xStateSince) / 1000));
	}
	xConnected = false;
	DeviceState::singleton()->MQTTOffline();
}


int MQTTClientAgent::msgCB(MqttClient *client, MqttMessage *msg, ::byte msgNew, ::byte msgDone){
	MQTTClientAgent *self = (MQTTClientAgent *)client->ctx;
	if (!self){
		return MQTT_CODE_SUCCESS;
	}
	return self->onMessage(msg, msgNew, msgDone);
}

int MQTTClientAgent::onMessage(MqttMessage *msg, ::byte msgNew, ::byte msgDone){
	if (msgNew){
		xMsgLen = 0;
		xMsgOverflow = (msg->total_len > MQTT_MSG_BUF_LEN);
		xRxCount++;
		printf("[MQTT] rx TOPIC: %.*s, Payload(%u)\n",
				msg->topic_name_len, msg->topic_name, msg->total_len);
	}

	if (!xMsgOverflow){
		if ((msg->buffer_pos + msg->buffer_len) <= MQTT_MSG_BUF_LEN){
			memcpy(&pMsgBuf[msg->buffer_pos], msg->buffer, msg->buffer_len);
			xMsgLen = msg->buffer_pos + msg->buffer_len;
		} else {
			xMsgOverflow = true;
		}
	}

	if (msgDone){
		if (xMsgOverflow){
			printf("ERROR: MQTT payload too large (%u), ignored\n", msg->total_len);
		} else if (xMsgLen > 0){
			SensorAgent::singleton()->processRequest(pMsgBuf, xMsgLen);
		}
		xMsgLen = 0;
	}
	return MQTT_CODE_SUCCESS;
}


/***
 * Network callbacks: plain TCP over lwIP sockets
 */
int MQTTClientAgent::netConnect(void *context, const char* host, word16 port, int timeout_ms){
	MQTTClientAgent *self = (MQTTClientAgent *)context;
	(void)timeout_ms;

	struct addrinfo hints;
	struct addrinfo *result = NULL;
	memset(&hints, 0, sizeof(hints));
	hints.ai_family = AF_INET;
	hints.ai_socktype = SOCK_STREAM;

	self->setState(MQTT_STATE_DNS);
	self->pBrokerIP[0] = 0;
	uint32_t t0 = to_ms_since_boot(get_absolute_time());
	int rc = lwip_getaddrinfo(host, NULL, &hints, &result);
	if ((rc != 0) || (result == NULL)){
		printf("[MQTT] DNS lookup failed for '%s' (%d) after %lums\n", host, rc,
				(unsigned long)(to_ms_since_boot(get_absolute_time()) - t0));
		return MQTT_CODE_ERROR_NETWORK;
	}

	struct sockaddr_in addr;
	memset(&addr, 0, sizeof(addr));
	addr.sin_family = AF_INET;
	addr.sin_port = lwip_htons(port);
	addr.sin_addr = ((struct sockaddr_in *)result->ai_addr)->sin_addr;
	lwip_freeaddrinfo(result);
	ip4addr_ntoa_r((const ip4_addr_t *)&addr.sin_addr, self->pBrokerIP, sizeof(self->pBrokerIP));
	printf("[MQTT] DNS %s -> %s in %lums\n", host, self->pBrokerIP,
			(unsigned long)(to_ms_since_boot(get_absolute_time()) - t0));
	self->setState(MQTT_STATE_TCP_CONNECT);

	int sock = lwip_socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
	if (sock < 0){
		printf("[MQTT] socket create failed errno %d\n", errno);
		return MQTT_CODE_ERROR_NETWORK;
	}

	t0 = to_ms_since_boot(get_absolute_time());
	if (lwip_connect(sock, (struct sockaddr *)&addr, sizeof(addr)) < 0){
		// errno 113 EHOSTUNREACH, 104 ECONNRESET/111 refused = nothing on port
		printf("[MQTT] TCP connect to %s:%d failed errno %d after %lums\n",
				self->pBrokerIP, port, errno,
				(unsigned long)(to_ms_since_boot(get_absolute_time()) - t0));
		lwip_close(sock);
		return MQTT_CODE_ERROR_NETWORK;
	}

	self->xSock = sock;
	return MQTT_CODE_SUCCESS;
}

int MQTTClientAgent::netRead(void *context, ::byte* buf, int buf_len, int timeout_ms){
	MQTTClientAgent *self = (MQTTClientAgent *)context;
	if (self->xSock < 0){
		return MQTT_CODE_ERROR_NETWORK;
	}

	int bytes = 0;
	uint32_t start = to_ms_since_boot(get_absolute_time());

	while (bytes < buf_len){
		int elapsed = (int)(to_ms_since_boot(get_absolute_time()) - start);
		int remain = timeout_ms - elapsed;
		if (remain <= 0){
			break;
		}

		fd_set readSet;
		FD_ZERO(&readSet);
		FD_SET(self->xSock, &readSet);
		struct timeval tv;
		tv.tv_sec = remain / 1000;
		tv.tv_usec = (remain % 1000) * 1000;

		int sel = lwip_select(self->xSock + 1, &readSet, NULL, NULL, &tv);
		if (sel < 0){
			printf("[MQTT] select failed errno %d\n", errno);
			return MQTT_CODE_ERROR_NETWORK;
		}
		if (sel == 0){
			break; // timeout
		}

		int rc = lwip_recv(self->xSock, &buf[bytes], buf_len - bytes, 0);
		if (rc <= 0){
			// Readable but no data: connection closed or failed
			printf("[MQTT] socket closed by peer (recv %d, errno %d)\n", rc, errno);
			return MQTT_CODE_ERROR_NETWORK;
		}
		bytes += rc;
	}

	if (bytes == 0){
		return MQTT_CODE_ERROR_TIMEOUT;
	}
	return bytes;
}

int MQTTClientAgent::netWrite(void *context, const ::byte* buf, int buf_len, int timeout_ms){
	MQTTClientAgent *self = (MQTTClientAgent *)context;
	(void)timeout_ms;
	if (self->xSock < 0){
		return MQTT_CODE_ERROR_NETWORK;
	}

	int sent = 0;
	while (sent < buf_len){
		int rc = lwip_send(self->xSock, &buf[sent], buf_len - sent, 0);
		if (rc <= 0){
			printf("[MQTT] send failed (%d, errno %d)\n", rc, errno);
			return MQTT_CODE_ERROR_NETWORK;
		}
		sent += rc;
	}
	return sent;
}

int MQTTClientAgent::netDisconnect(void *context){
	MQTTClientAgent *self = (MQTTClientAgent *)context;
	if (self->xSock >= 0){
		lwip_close(self->xSock);
		self->xSock = -1;
	}
	return MQTT_CODE_SUCCESS;
}
