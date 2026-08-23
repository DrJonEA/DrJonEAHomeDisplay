import os
import json
import sys
import time
import serial

if len(sys.argv) == 1:
    print("Need IO Device as first parameter")
    sys.exit(1)

iodev = sys.argv[1]

req = {
    "req": "connect",
    "ssid": os.environ['WIFI_SSID'],
    "pwd": os.environ['WIFI_PASSWORD'],
    "tz": 60,
    "mqttHost": "",
    "mqttClient": "",
    "mqttUser": "",
    "mqttPwd": "",
    "mqttPort": 0,
    "httpConn": "",
    "reboot": True
}



print("Start")
with serial.Serial(iodev, 115200) as f:
    while True:
        
        print(json.dumps(req))
        f.write((json.dumps(req) + "\n").encode('utf-8') )
        f.flush()
        
        time.sleep(60)
f.close()