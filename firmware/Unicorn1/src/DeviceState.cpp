/*
 * DeviceState.cpp
 *
 *  Created on: 2 Jul 2026
 *      Author: jondurrant
 */

#include "DeviceState.h"
#include <string.h>
#include "json-maker/json-maker.h"
#include "pico/cyw43_arch.h"

#define SEN_TEMP_SLOT 3
#define SEN_HUMID_SLOT 4
#define SENSOR_TEMPERATURE 	"sensorTemp"
#define SENSOR_HUMIDITY 	"sensorHumid"
#define WIFI_RSSI_SLOT 5
#define WIFI_RSSI 			"wifiRSSI"
#define NET_MBPS_SLOT 6
#define NET_MBPS			"mbps"

DeviceState *DeviceState::SELF = NULL ;
DeviceState::DeviceState(): StateTemp() {
	elements = 7;
	jsonHelpers[SEN_TEMP_SLOT] = (StateFunc)&DeviceState::jsonSensorTemp;
	jsonHelpers[SEN_HUMID_SLOT] = (StateFunc)&DeviceState::jsonSensorHumid;
	jsonHelpers[WIFI_RSSI_SLOT] = (StateFunc)&DeviceState::jsonWifiRSSI;
	jsonHelpers[NET_MBPS_SLOT] = (StateFunc)&DeviceState::jsonMBPS;

	setupDefaults();

}

DeviceState::~DeviceState() {
	// TODO Auto-generated destructor stub
}

DeviceState * DeviceState::singleton(){
	if (SELF == NULL){
		SELF = new DeviceState;
	}
	return SELF;
}

void DeviceState::MQTTOffline(){
	xMQTTOnline = false;
}
void DeviceState::MQTTOnline(){
	xMQTTOnline = true;
}

bool DeviceState::isMQTTOnline(){
	return xMQTTOnline;
}

void DeviceState::WifiOnline(bool b){
	xWifiOnline = b;
}
void DeviceState::WifiOffline(){
	WifiOnline(false);
}
bool DeviceState::isWifiOnline(){
	return xWifiOnline;
}


void DeviceState::setTemperature(float c){
	xTemperature = c;
	setDirty(SEN_TEMP_SLOT);
	setDirty(WIFI_RSSI_SLOT); // Force RSSI to be reread every time temp is updated
}
void DeviceState::setHumidity(float p){
	xHumidity = p;
	setDirty(SEN_HUMID_SLOT);
}
float DeviceState::getTemperature(){
	return xTemperature;
}
float DeviceState::getHumidity(){
	return xHumidity;
}

void DeviceState::setDefCon(uint8_t d){
	xDefCon = d;
}
uint8_t DeviceState::getDefCon(){
	return xDefCon;
}

int DeviceState::getTimeZone(){
	int32_t tz;
	NVSOnboard::getInstance()->get_i32 ( DEV_TS , &tz);
	return tz;
}

void DeviceState::setTimeZone(int tz){
	int32_t oldTZ, newTZ;
	NVSOnboard *nvs = NVSOnboard::getInstance();
	nvs->get_i32 ( DEV_TS , &oldTZ);
	newTZ = tz;
	if (oldTZ != newTZ){
		nvs->set_i32 ( DEV_TS , tz);
	}
}

char * DeviceState::getSSID(){
	pSSID = nvsGet(DEV_SSID, pSSID);
	return pSSID;
}
void DeviceState::setSSID(const char *s){
	pSSID = nvsSet(DEV_SSID,  s,  pSSID);
}

char * DeviceState::getSSIDpwd(){
	pSSIDpwd = nvsGet(DEV_SSID_PWD, pSSIDpwd);
	return pSSIDpwd;
}
void DeviceState::setSSIDpwd(const char *s){
	pSSIDpwd = nvsSet(DEV_SSID_PWD,  s,  pSSIDpwd);
}

char * DeviceState::getMQTThost(){
	pMQTThost = nvsGet(DEV_MQTT_HOST, pMQTThost);
	return pMQTThost;
}
void DeviceState::setMQTThost(const char *s){
	pMQTThost = nvsSet(DEV_MQTT_HOST,  s,  pMQTThost);
}

char * DeviceState::getMQTTclient(){
	pMQTTclient = nvsGet(DEV_MQTT_CLIENT, pMQTTclient);
	return pMQTTclient;
}
void DeviceState::setMQTTclient(const char *s){
	pMQTTclient = nvsSet(DEV_MQTT_CLIENT,  s,  pMQTTclient);
}

char * DeviceState::getMQTTuser(){
	pMQTTuser = nvsGet(DEV_MQTT_USER, pMQTTuser);
	return pMQTTuser;
}
void DeviceState::setMQTTuser(const char *s){
	pMQTTuser = nvsSet(DEV_MQTT_USER,  s,  pMQTTuser);
}

char * DeviceState::getMQTTpwd(){
	pMQTTpwd = nvsGet(DEV_MQTT_PWD, pMQTTpwd);
	return pMQTTpwd;
}
void DeviceState::setMQTTpwd(const char *s){
	pMQTTpwd = nvsSet(DEV_MQTT_PWD,  s,  pMQTTpwd);
}

char * DeviceState::getHTTPconn(){
	pHTTPconn = nvsGet(DEV_HTTP_STR, pHTTPconn);
	return pHTTPconn;
}
void DeviceState::setHTTPconn(const char *s){
	pHTTPconn = nvsSet(DEV_HTTP_STR,  s,  pHTTPconn);
}

int DeviceState::getMQTTport(){
	int32_t p;
	NVSOnboard::getInstance()->get_i32 ( DEV_MQTT_PORT , &p);
	return p;
}
void DeviceState::setMQTTport(int p){
	NVSOnboard *nvs = NVSOnboard::getInstance();
	nvs->set_i32 ( DEV_TS , p);
}

char * DeviceState::getTopicOrg(){
	pTopicOrg = nvsGet(DEV_TOPIC_ORG, pTopicOrg);
	return pTopicOrg;
}
void DeviceState::setTopicOrg(const char *s){
	pTopicOrg = nvsSet(DEV_TOPIC_ORG,  s,  pTopicOrg);
}

char * DeviceState::getTopicGroup(){
	pTopicGroup = nvsGet(DEV_TOPIC_GROUP, pTopicGroup);
	return pTopicGroup;
}
void DeviceState::setTopicGroup(const char *s){
	pTopicGroup = nvsSet(DEV_TOPIC_GROUP,  s,  pTopicGroup);
}



char *DeviceState::nvsGet(const char * id, char *str){
	char * res = str;
	if (res == NULL){
		NVSOnboard *nvs = NVSOnboard::getInstance();
		size_t length = nvs->size(id);
		res = (char *)pvPortMalloc(length);
		nvs->get_str ( id, res, &length);
	}
	return res;
}

char *DeviceState::nvsSet(const char * id,  const char * newVal, char *oldVal){
	if (oldVal != NULL){
		vPortFree(oldVal);
	}
	NVSOnboard *nvs = NVSOnboard::getInstance();
	size_t length = strlen(newVal) + 1;
	char * res  =(char*) pvPortMalloc(length);
	strcpy(res, newVal);
	nvs->set_str ( id, res);
	return res;
}


void DeviceState::setupDefaults(){
	NVSOnboard *nvs = NVSOnboard::getInstance();

	if (!nvs->contains(DEV_TS)){
		nvs->set_i32 ( DEV_TS , 0);
	}

	if (!nvs->contains(DEV_SSID)){
		nvs->set_str ( DEV_SSID , WIFI_SSID);
	}

	if (!nvs->contains(DEV_SSID_PWD)){
		nvs->set_str ( DEV_SSID_PWD , WIFI_PASSWORD);
	}

	if (!nvs->contains(DEV_MQTT_HOST)){
		nvs->set_str ( DEV_MQTT_HOST , MQTT_HOST);
	}

	if (!nvs->contains(DEV_MQTT_PORT)){
		nvs->set_i32 ( DEV_MQTT_PORT , MQTT_PORT);
	}

	if (!nvs->contains(DEV_MQTT_CLIENT)){
		nvs->set_str ( DEV_MQTT_CLIENT , MQTT_CLIENT);
	}

	if (!nvs->contains(DEV_MQTT_USER)){
		nvs->set_str ( DEV_MQTT_USER , MQTT_USER);
	}

	if (!nvs->contains(DEV_MQTT_PWD)){
		nvs->set_str ( DEV_MQTT_PWD , MQTT_PASSWD);
	}

	if (!nvs->contains(DEV_HTTP_STR)){
		nvs->set_str ( DEV_HTTP_STR , "http://jons-mbs:5080/");
	}

	if (!nvs->contains(DEV_TOPIC_ORG)){
		nvs->set_str ( DEV_TOPIC_ORG , "drjonea");
	}
	if (!nvs->contains(DEV_TOPIC_GROUP)){
		nvs->set_str ( DEV_TOPIC_GROUP , "cosmic");
	}

	if (nvs->isDirty()){
		if (nvs->commit() != NVS_OK){
			printf("NVS Setup Default Failed\n");
		}
	}

}

void DeviceState::storeConfig(){
	NVSOnboard *nvs = NVSOnboard::getInstance();
	if (nvs->isDirty()){
		if (nvs->commit() != NVS_OK){
			printf("NVS Store Config Failed\n");
		}
	}
}


char* DeviceState::jsonSensorTemp(char *buf, unsigned int len){
	char *p = buf;
	size_t l = len;
	p = json_double( p, SENSOR_TEMPERATURE, (double)getTemperature(), &l);
	return p;
}


char* DeviceState::jsonSensorHumid(char *buf, unsigned int len){
	char *p = buf;
	size_t l = len;
	p = json_double( p, SENSOR_HUMIDITY, (double)getHumidity(), &l);

	return p;
}

char* DeviceState::jsonWifiRSSI(char *buf, unsigned int len){
	char *p = buf;
	size_t l = len;
	int32_t rssi;

	if (cyw43_wifi_get_rssi(&cyw43_state, &rssi) == 0){
		printf("jsonWifiRSSI %d\n", rssi);
		p = json_int( p, WIFI_RSSI, rssi, &l);
	} else {
		printf("jsonWifiRSSI fail\n", rssi);
		p = json_int( p, WIFI_RSSI, 0, &l);
	}
	return p;
}


char* DeviceState::jsonMBPS(char *buf, unsigned int len){
	char *p = buf;
	size_t l = len;
	p = json_double( p, NET_MBPS, (double)xMBPS, &l);

	return p;
}

void DeviceState::setNetSpeed(float mbps){
	xMBPS = mbps;
	setDirty(NET_MBPS_SLOT);
}
float DeviceState::getNetSpeed(){
	return xMBPS;
}
