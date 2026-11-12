/*
 * DeviceState.h
 *
 *  Created on: 2 Jul 2026
 *      Author: jondurrant
 */

#ifndef FIRMWARE_UNICORN1_SRC_DEVICESTATE_H_
#define FIRMWARE_UNICORN1_SRC_DEVICESTATE_H_

#include "pico/stdlib.h"
#include "MQTTAgentObserver.h"
#include "NVSOnboard.h"

#include "StateTemp.h"

#define DEV_TS 				"TS"
#define DEV_SSID 			"SSID"
#define DEV_SSID_PWD 		"SSID_PWD"
#define DEV_MQTT_HOST 		"MQTT_HOST"
#define DEV_MQTT_PORT 		"MQTT_PORT"
#define DEV_MQTT_CLIENT 	"MQTT_CLIENT"
#define DEV_MQTT_USER 		"MQTT_USER"
#define DEV_MQTT_PWD 		"MQTT_PWD"
#define DEV_HTTP_STR 		"HTTP_REQ"
#define DEV_TOPIC_ORG 		"ORG"
#define DEV_TOPIC_GROUP 	"GRP"


class DeviceState : public MQTTAgentObserver, public StateTemp{
public:
	static DeviceState * singleton();

	virtual ~DeviceState();

	//MQTT Observer CB
	virtual void MQTTOffline();
	virtual void MQTTOnline();
	bool isMQTTOnline();

	void WifiOnline(bool b = true);
	void WifiOffline();
	bool isWifiOnline();

	void setTemperature(float c);
	void setHumidity(float p);
	float getTemperature();
	float getHumidity();

	void setDefCon(uint8_t d=5);
	uint8_t getDefCon();

	int getTimeZone();
	void setTimeZone(int tz);

	void setNetSpeed(float mbps);
	float getNetSpeed();

	void setRSSI(int32_t rssi);
	int32_t getRSSI();

	char * getSSID();
	void setSSID(const char *s);

	char * getSSIDpwd();
	void setSSIDpwd(const char *s);

	int getMQTTport();
	void setMQTTport(int p);

	char * getMQTThost();
	void setMQTThost(const char *s);

	char * getMQTTclient();
	void setMQTTclient(const char *s);

	char * getMQTTuser();
	void setMQTTuser(const char *s);

	char * getMQTTpwd();
	void setMQTTpwd(const char *s);

	void setHTTPconn(const char *s);
	char * getHTTPconn();

	void setTopicOrg(const char *s);
	char * getTopicOrg();

	void setTopicGroup(const char *s);
	char * getTopicGroup();

	void storeConfig();

protected:
	/***
	 * get temperature in json format
	 * @param buf
	 * @param len
	 * @return
	 */
	virtual char* jsonSensorTemp(char *buf, unsigned int len);

	/***
	 * get temperature in json format
	 * @param buf
	 * @param len
	 * @return
	 */
	virtual char* jsonSensorHumid(char *buf, unsigned int len);

	/***
	 * get temperature in json format
	 * @param buf
	 * @param len
	 * @return
	 */
	virtual char* jsonWifiRSSI(char *buf, unsigned int len);

		/***
	 * get temperature in json format
	 * @param buf
	 * @param len
	 * @return
	 */
	virtual char* jsonMBPS(char *buf, unsigned int len);

private:
	static DeviceState* SELF ;
	DeviceState();
	void setupDefaults();

	char *nvsGet(const char * id, char *str);
	char *nvsSet(const char * id,  const char * newVal, char *oldVal);

	bool xMQTTOnline = false;
	bool xWifiOnline = false;
	float xTemperature = -100.0;
	float xHumidity = -100.0;
	uint8_t xDefCon=5;
	float xMBPS = 0.0;
	int32_t xRSSI = 0;

	char *pSSID = NULL;
	char *pSSIDpwd = NULL;
	char *pMQTThost = NULL;
	char *pMQTTclient = NULL;
	char *pMQTTuser = NULL;
	char *pMQTTpwd = NULL;
	char *pHTTPconn = NULL;

	char *pTopicOrg = NULL;
	char *pTopicGroup = NULL;

};

#endif /* FIRMWARE_UNICORN1_SRC_DEVICESTATE_H_ */
