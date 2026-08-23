import os
import glob
import json
import platform
import re
import sys
import time
import serial


def discover_pico_device():
    override = os.environ.get("PICO_SERIAL_DEVICE")
    if override:
        if not os.path.exists(override):
            raise RuntimeError(f"PICO_SERIAL_DEVICE does not exist: {override}")
        return override

    if platform.system() == "Darwin":
        candidates = sorted(glob.glob("/dev/tty.usbmodem*"))
    elif platform.system() == "Linux":
        by_id = sorted(glob.glob("/dev/serial/by-id/*"))
        pico_pattern = re.compile(r"pico|raspberry|rp2040", re.IGNORECASE)
        candidates = [path for path in by_id if pico_pattern.search(os.path.basename(path))]
        if not candidates:
            candidates = sorted(glob.glob("/dev/ttyACM*"))
    else:
        raise RuntimeError(f"Unsupported operating system: {platform.system()}")

    if len(candidates) == 1:
        return candidates[0]
    if not candidates:
        raise RuntimeError(
            "No Pico serial device found. Connect the Pico or set "
            "PICO_SERIAL_DEVICE."
        )
    raise RuntimeError(
        "Multiple serial devices found; set PICO_SERIAL_DEVICE to choose one: "
        + ", ".join(candidates)
    )


WIFI_SSID = sys.argv[1]
WIFI_PASSWORD = sys.argv[2] 
clientid = sys.argv[3]
mqtt_passwd = sys.argv[4]
MQTTServ = sys.argv[5]
MQTTPort = int(sys.argv[6])
HTTPConn = sys.argv[7]
iodev = discover_pico_device()


req = [{
        "ssid": WIFI_SSID,
        "pwd": WIFI_PASSWORD,
        "tz": 60
    },
    {
        "mqttClient": clientid,
        "mqttUser": clientid,
        "mqttPwd": mqtt_passwd
    },
    {
        "mqttHost": MQTTServ,
        "mqttPort": MQTTPort,
        "httpConn": HTTPConn,
    }, {
        "reboot": True
    }
    ]



print(f"Start provisioning {iodev}")
with serial.Serial(iodev, 115200) as f:

    for r in req:    
        f.write((json.dumps(r) + "\n").encode('utf-8') )
        f.flush()
        print(f"Provisioning request sent to {iodev} for client {clientid}: {r}")
    
        time.sleep(3)