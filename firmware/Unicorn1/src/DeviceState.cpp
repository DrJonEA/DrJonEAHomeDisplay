/*
 * DeviceState.cpp
 *
 *  Created on: 2 Jul 2026
 *      Author: jondurrant
 */

#include "DeviceState.h"

DeviceState *DeviceState::SELF = NULL ;
DeviceState::DeviceState() {
	// TODO Auto-generated constructor stub

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
}
void DeviceState::setHumidity(float p){
	xHumidity = p;
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
