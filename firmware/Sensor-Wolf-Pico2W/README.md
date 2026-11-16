# Sensor-Wolf-Pico2W

A sensor node for the Raspberry Pi Pico 2 W that has no display. It reports temperature, humidity, WiFi
signal strength and network upload speed to the Display Manager over MQTT.

It does the same job as *Sensor-Pico2W* but uses [wolfMQTT](https://github.com/wolfSSL/wolfMQTT)
instead of the TwinThing framework and coreMQTT. It only uses the `<ORG>/display` and `<ORG>/sensor`
topics, not the TwinThing `GRP/...` and `TNG/...` topics.

Back to the [main README](../../README.md).

## What it does
- Joins WiFi, sets the clock from NTP and applies the stored timezone.
- Reads an AHT10 temperature and humidity sensor and the WiFi RSSI every 3 seconds.
- Every 10 seconds, publishes a sensor report to `<ORG>/sensor/<group>/<clientid>`:
  ```json
  {"id": "studysensor", "temperature": 21.57, "humidity": 46.84, "mbps": 8.08, "rssi": -58}
  ```
- Accepts commands on its display topics (see [Topics](#topics)).
- Accepts configuration as JSON on USB serial and stores it in flash (see [Configuration](#configuration)).
- Reboots itself through the watchdog if MQTT has been offline for 10 minutes.

## Hardware
- Raspberry Pi Pico 2 W (RP2350).
- AHT10 on `i2c0`, with SDA on GP0 and SCL on GP1. If the sensor isn't found at boot, the node still
  runs and reports RSSI and speed only.
- The debug UART is on GP16 (TX) and GP17 (RX). Logs also go to USB serial.

## Topics
`<ORG>` defaults to `drjonea` and `<group>` defaults to `sensor`.

| Topic | Direction | Use |
|---|---|---|
| `<ORG>/display` | in | Commands to every display and sensor |
| `<ORG>/display/<group>` | in | Commands to the group |
| `<ORG>/display/<group>/<clientid>` | in | Commands to this node |
| `<ORG>/sensor/<group>/<clientid>` | out | Sensor reports, QoS 1 |

The node subscribes to these three topics rather than `<ORG>/display/#`. With a wildcard it would also
receive commands meant for other nodes, so a speed test sent to one node would start one on every node.

Commands it acts on:

| Key | Example | Effect |
|---|---|---|
| `tz` | `{"tz": 60}` | Set the UTC offset in minutes and store it |
| `speedtest` | `{"speedtest": true}` | Run the upload speed test |

Display-only keys such as `layout`, `brightness` and `defcon` are ignored.

### Speed test
The node POSTs 100 KB to `<httpConn>/speedtest` and times the request. If the server answers `200`, it
sets `mbps` and sends a sensor report straight away. The Display Manager provides this endpoint and runs
the test as part of its network sweep.

The payload is the first 100 KB of flash (`XIP_BASE`), sent over plain HTTP. It used to be the start of
RAM, which almost certainly holds the Wi-Fi and MQTT credentials. Flash is safer but not guaranteed
clean, as the credentials are stored in flash too, so only point `httpConn` at a server you own.

## What it does not do
Because the TwinThing topics are not used:

- **No MQTT ping.** The node doesn't answer pings on `GRP/display/TPC/PING`, so the Display Manager's
  network sweep records no `mqtt_ms` or `mqtt_loss` for it, and gets no IP address from a pong. The
  ICMP ping stage needs that IP address, so it may have nothing to ping either. The speed test and
  sensor reports still work.
- **No TwinThing state.** There are no online/offline lifecycle messages and no device twin.
- **No last will.** The broker doesn't announce when the node drops off.
- **No TLS.** MQTT runs over plain TCP. wolfSSL is in the build for the HTTP client, ready for later.

A sensor report published while the broker is unreachable is dropped. The next report follows 10
seconds later.

## Configuration
Settings are stored in flash (NVS). On first boot they are filled in from the build environment variables
and the defaults below. To change them, send a JSON object over USB serial; *exp/pyConfig/connReq.py* is
an example. Every key is optional:

| Key | Meaning | First boot default |
|---|---|---|
| `ssid`, `pwd` | WiFi network and password | `WIFI_SSID`, `WIFI_PASSWORD` |
| `mqttHost`, `mqttPort` | Broker host name or IP address, and port | `MQTT_HOST`, `MQTT_PORT` |
| `mqttClient` | MQTT client ID, also used as `<clientid>` in topics | `MQTT_CLIENT` |
| `mqttUser`, `mqttPwd` | Broker user name and password | `MQTT_USER`, `MQTT_PASSWD` |
| `httpConn` | Base URL of the Display Manager, used for the speed test | `http://jons-mbs:5080` |
| `org` | Topic root `<ORG>` | `drjonea` |
| `group` | Topic group `<group>` | `sensor` |
| `tz` | UTC offset in minutes | `0` |
| `reboot` | Any value reboots the node after storing the settings | |

For example:
```json
{"mqttHost": "broker.local", "mqttPort": 1883, "group": "sensor", "reboot": true}
```
Topic and broker changes take effect after a reboot.

## Building
Clone the repo with submodules; wolfMQTT is the `lib/wolfmqtt` submodule. The build needs Pico SDK 2.x
and these environment variables, which only set the first boot defaults:
`WIFI_SSID`, `WIFI_PASSWORD`, `MQTT_CLIENT`, `MQTT_USER`, `MQTT_PASSWD`, `MQTT_HOST`, `MQTT_PORT`.

```sh
cd firmware/Sensor-Wolf-Pico2W
mkdir build && cd build
cmake ..
make
```
The output is *build/src/SensorWolfPico2W.uf2*.

## How it works
Four FreeRTOS tasks:

- **Main** (`main.cpp`) connects WiFi, starts NTP and the other tasks, then reads the sensors and logs
  status every 3 seconds. It rejoins WiFi if the link drops.
- **MQTTClient** (`MQTTClientAgent.cpp`) owns the wolfMQTT client. Every wolfMQTT call runs on this task,
  so wolfMQTT is used in single-threaded mode. It connects, subscribes, waits for messages in 100 ms
  slices, and sends queued publishes. If anything fails it closes the connection, waits 3 seconds and
  starts again. wolfMQTT sends the keep-alive pings (every 30 seconds) itself.
- **SensorAgent** (`SensorAgent.cpp`) handles commands and serial configuration, runs the speed test and
  builds the sensor reports. Other tasks hand messages to the MQTT task with `publish()`, which puts them
  on a queue of four.
- **Watchdog** keeps the 5 second hardware watchdog fed until a reboot is requested.

### wolfMQTT port
- **Network callbacks.** `MQTTClientAgent.cpp` provides plain TCP connect, read, write and close
  callbacks using lwIP sockets. Reads use `select()` with a timeout.
- **Build options.** wolfMQTT normally reads `user_settings.h`, which would clash with wolfSSL's file of
  the same name. Instead, *port/wolfmqtt/wolfmqtt/options.h* holds the settings, and
  *wolfmqtt_import.cmake* builds the library from the submodule unchanged.
- **Keep-alive clock.** wolfMQTT times keep-alives with `time(NULL)`, which jumps when NTP sets the
  clock. `options.h` points it at time since boot instead.

## Diagnostics
The serial log follows the node through its lifecycle:

- `[LIFE]` lines mark startup steps (WiFi joined with its IP address, NTP started, MQTT task started),
  WiFi drops and the offline reboot.
- `[MQTT] state A -> B` lines show each step of a connection: `WAIT_WIFI`, `DNS`, `TCP_CONNECT`,
  `MQTT_CONNECT`, `SUBSCRIBE`, `ONLINE`, then `BACKOFF` after a failure.
- Each connection attempt logs the host, port, client ID and user, and whether a password is set (never
  the password itself). A failure logs where it happened:
  - DNS lookup, with how long it took.
  - TCP connect, with the error number. 113 means the host is unreachable; 104 or 111 means nothing is
    listening on that port.
  - Broker refusal, decoded, for example `bad user name or password` or `client id rejected`.
  - Subscription, marked `REFUSED` if the broker's access control blocks it.
- Every 3 seconds, a `[NET]` line gives the WiFi and IP link states, the IP address and the RSSI, and a
  `[MQTT] status:` line gives the state, how long it has been in it, the resolved broker IP, counts of
  attempts, failures, messages published and messages received, and the last error.
- Task stack and heap statistics print about once a minute.

For packet-level detail, uncomment `WOLFMQTT_DEBUG_CLIENT` and `WOLFMQTT_DEBUG_SOCKET` in
*port/wolfmqtt/wolfmqtt/options.h*.
