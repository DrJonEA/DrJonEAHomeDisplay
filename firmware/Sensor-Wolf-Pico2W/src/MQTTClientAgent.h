/*
 * MQTTClientAgent.h
 *
 * Owns the wolfMQTT client and its lwIP socket. All wolfMQTT calls are made
 * from this agent's task, so the library is used single threaded:
 *  - Connects (and reconnects) using the broker settings held in NVS
 *  - Subscribes to <org>/display, <org>/display/<group> and
 *    <org>/display/<group>/<client>, passing payloads to the SensorAgent
 *  - Publishes messages that other tasks queue with publish()
 *  - Keep-alive pings are scheduled by wolfMQTT inside WaitMessage
 *
 *  Author: jondurrant
 */

#ifndef FIRMWARE_SENSOR_WOLF_PICO2W_SRC_MQTTCLIENTAGENT_H_
#define FIRMWARE_SENSOR_WOLF_PICO2W_SRC_MQTTCLIENTAGENT_H_

#include "pico/stdlib.h"
#include "Agent.h"
#include "FreeRTOS.h"
#include "queue.h"
#include "wolfmqtt/mqtt_client.h"

#define MQTT_TX_BUF_LEN 		1024
#define MQTT_RX_BUF_LEN 		1024
#define MQTT_CMD_TIMEOUT_MS 	5000
#define MQTT_KEEP_ALIVE_SEC 	30
#define MQTT_WAIT_MS 			100
#define MQTT_RECON_DELAY_MS 	3000

#define MQTT_PUB_QUEUE_LEN 		4
#define MQTT_PUB_TOPIC_LEN 		96
#define MQTT_PUB_PAYLOAD_LEN 	256

#define MQTT_SUB_COUNT 			3
#define MQTT_MSG_BUF_LEN 		512

typedef enum {
	MQTT_STATE_INIT = 0,
	MQTT_STATE_WAIT_WIFI,
	MQTT_STATE_DNS,
	MQTT_STATE_TCP_CONNECT,
	MQTT_STATE_MQTT_CONNECT,
	MQTT_STATE_SUBSCRIBE,
	MQTT_STATE_ONLINE,
	MQTT_STATE_BACKOFF,
	MQTT_STATE_FATAL
} MQTTState;

typedef struct {
	char topic[MQTT_PUB_TOPIC_LEN];
	char payload[MQTT_PUB_PAYLOAD_LEN];
	uint16_t len;
	uint8_t qos;
} MQTTPubReq;

class MQTTClientAgent : public Agent {
public:
	MQTTClientAgent();
	virtual ~MQTTClientAgent();

	/***
	 * Queue a message for publishing. Safe to call from any task.
	 * @param topic
	 * @param payload
	 * @param len
	 * @param qos - 0 or 1
	 * @return false if the message is too big or the queue is full
	 */
	bool publish(const char *topic, const void *payload, size_t len, uint8_t qos = 1);

	/***
	 * MQTT client id in use
	 */
	const char * getId();

	bool isConnected();

	/***
	 * Telemetry: current lifecycle state and counters
	 */
	MQTTState getState();
	static const char * stateToString(MQTTState s);
	void printStatus();

protected:
	virtual void run();
	virtual configSTACK_DEPTH_TYPE getMaxStackSize();

private:
	bool brokerConnect();
	void brokerDisconnect();
	bool brokerSubscribe();
	bool sendQueued();

	int onMessage(MqttMessage *msg, ::byte msgNew, ::byte msgDone);

	// wolfMQTT callbacks
	static int netConnect(void *context, const char* host, word16 port, int timeout_ms);
	static int netRead(void *context, ::byte* buf, int buf_len, int timeout_ms);
	static int netWrite(void *context, const ::byte* buf, int buf_len, int timeout_ms);
	static int netDisconnect(void *context);
	static int msgCB(MqttClient *client, MqttMessage *msg, ::byte msgNew, ::byte msgDone);

	word16 nextPacketId();
	void setState(MQTTState s);

	volatile MQTTState xState = MQTT_STATE_INIT;
	uint32_t xStateSince = 0;
	uint32_t xAttempts = 0;
	uint32_t xFailures = 0;
	uint32_t xPubCount = 0;
	uint32_t xRxCount = 0;
	int xLastError = 0;
	char pLastErrorWhere[24] = "none";
	char pBrokerIP[16] = "";

	MqttClient xClient;
	MqttNet xNet;
	int xSock = -1;
	volatile bool xConnected = false;
	word16 xPacketId = 0;

	::byte pTxBuf[MQTT_TX_BUF_LEN];
	::byte pRxBuf[MQTT_RX_BUF_LEN];

	QueueHandle_t xPubQueue = NULL;
	MQTTPubReq xPubReq;

	char * pSubTopics[MQTT_SUB_COUNT];
	MqttTopic xSubTopics[MQTT_SUB_COUNT];

	// Reassembly of incoming payloads that span several rx buffers
	char pMsgBuf[MQTT_MSG_BUF_LEN];
	size_t xMsgLen = 0;
	bool xMsgOverflow = false;
};

#endif /* FIRMWARE_SENSOR_WOLF_PICO2W_SRC_MQTTCLIENTAGENT_H_ */
