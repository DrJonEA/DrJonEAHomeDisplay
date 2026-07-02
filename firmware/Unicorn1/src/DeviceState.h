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

class DeviceState : public MQTTAgentObserver{
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




private:
	static DeviceState* SELF ;
	DeviceState();

	bool xMQTTOnline = false;
	bool xWifiOnline = false;
	float xTemperature = -100.0;
	float xHumidity = -100.0;
	uint8_t xDefCon=5;

};

#endif /* FIRMWARE_UNICORN1_SRC_DEVICESTATE_H_ */
