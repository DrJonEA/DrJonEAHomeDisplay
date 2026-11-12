# DrJonEAHomeDisplay

![A Cosmic Unicorn showing the weather tile: new display tiles, no new firmware](images/banner.jpg)

A display control architecture for my home. Initially using the 
[PIMORONI Cosmic Unicorn V1](https://shop.pimoroni.com/products/space-unicorns?variant=40842626596947).
Each device is a IoT devices publishing temperature and humidity (from AHT10) over MQTT. 
Then responding to commands over MQTT to provide details of what to share.

To allow a Cosmic Unicorn to adapt to different data to visualise I went with a simple LVGL two tile 
architecture. A local tile that just displays local data: Clock, Temperature, Humidity and Status. Plus a 
Image tile that pulls an image of HTTP to display. Overlays of clock and scroll text are also supported.

![The local tile, weather, sun and moon, and calendar tiles on a Cosmic Unicorn](images/tiles-in-action.jpg)

![Local tile and image tile](images/two-tiles.jpg)

MQTT carries sensor data out and announcements in. When a new tile is ready, the display pulls the image over HTTP.

![MQTT for sensor data and announcements, HTTP to pull images](images/mqtt-http.jpg)

## Cloning and Building
This is a Pico SDK based project in C++. Where libraries are included as submodules. When cloning please
recurse submodules. 

I have a blog that explains how to clone repos and build my projects on 
[drjonea.co.uk](https://drjonea.co.uk/2025/12/15/building-my-projects-from-repo/).

## Libraries
The libraries I am using for this is PIMORONI's driver for the Cosmic Unicorn plus LVGL v9.5. For MQTT
I am using CoreMQTT and coreMQTT-Agent from FreeRTOS plus FreeRTOS Kernel. For HTTP I am using
coreHTTP. Plus some libraries for JSON and URL decoding.

Right now I am not securing the data transport but that is a longer term plan. WolfSSL is in the build as a
TLS library for when I add this capability.

The server for this architecture is the Display Manager in the *manager* folder, written in Python with
Flask, Paho and Pillow (see [Server](#server-display-manager) below). Earlier experiments are in the *exp* folder.

The MQTT broker, TLS proxy and digital twin infrastructure are in a separate repo,
[oracIoTHub](https://github.com/DrJonEA/oracIoTHub) (EMQX, HAProxy, TwinThing and Ansible roles).

![Displays talk MQTT and HTTP to the EMQX and HAProxy infrastructure and the Display Manager service](images/architecture.jpg)

## Firmware

### Cosmic Unicorn V1
Firmware build is targetted at the Cosmic Unicorn using a Pico W. Other firmware may be added over time.

Unit can be configured over USB Serial by sending a JSON string. See *exp/pyConfig* as example.

![Config JSON with Wi-Fi and MQTT credentials sent over serial USB to the display](images/config-usb.jpg)

### Network speed test
A display can measure its own network upload speed and report it in its device state.

To start a test, send a display command over MQTT that contains a `speedtest` key. The value is
ignored, for example:
```json
{"speedtest": true}
```
The display then POSTs 100 KB to `<httpConn>/speedtest`, where `<httpConn>` is the display's
configured HTTP server. It times the request, and if the server answers `200` it sets `mbps` in the
device state to the upload speed in megabits per second. The new value goes out with the next state
update, alongside `wifiRSSI`, so you can compare speed and signal strength.

- The payload is just a copy of the Pico's RAM, so the server should accept any body and ignore its
  content. The request is sent as `Content-Type: application/json`, so the endpoint must not try to
  parse it.
- The time includes connecting, sending the headers and waiting for the response, so `mbps` slightly
  understates the raw transfer rate.
- To give TCP enough memory for a fast upload, lwIP's `MEM_SIZE` is now 16 KB (it was 4000 bytes) in
  *port/lwip/lwipopts.h*.
- The Display Manager doesn't provide a `/speedtest` endpoint yet. You need a server that accepts the
  POST and returns `200`.

## Server: Display Manager
The Display Manager (*manager/*) is a Flask app that generates the 32x32 tiles the displays download,
publishes display commands and clock data over MQTT, and serves a web dashboard.

![Data sources: local time, time zone, weather now, forecast, solar and lunar](images/data-sources.jpg)

### Running
```
cd manager
pip install -r requirements.txt
python main.py
```
It listens on port 5000. Configuration is by environment variable:

| Variable | Purpose | Default |
|---|---|---|
| `MQTT_HOST`, `MQTT_PORT` | MQTT broker | port 1883 |
| `MQTT_CLIENT`, `MQTT_USER`, `MQTT_PASSWD` | MQTT credentials | |
| `SMARTCLOCKGOOGLE` | Google Weather API key | |
| `WEATHER_LAT`, `WEATHER_LNG` | Location for weather and sun/moon times | Brighton, UK |
| `DISPLAY_TIMEZONE` | IANA timezone for the clock offset and calendar date | `Europe/London` |
| `CALENDAR_THEMES_DIR` | Calendar theme collections | `manager/calendar_themes` |
| `CALENDAR_IMAGE_DIR` | Calendar theme images | `manager/static/img/calendar` |

Run it detached from a terminal (for example as a systemd service, or with `nohup ... > manager.log 2>&1`).
All runtime output goes through `logging`.

### Tiles
Each tile is available as a PNG for viewing and as BRG565 for the displays:

| Tile | PNG | Display |
|---|---|---|
| Current weather | `/weather.png` | `/32x32/weather.brg565` |
| Today's forecast | `/forecast.png` | `/32x32/forecast.brg565` |
| Sun and moon paths | `/solar.png` | `/32x32/solar.brg565` |
| Calendar | `/32x32/cal.png` | `/32x32/cal.brg565` |
| Pride flag | `/32x32/pride.png` | `/32x32/pride.brg565` |

The calendar tile accepts `?date=dd/mm/yyyy` to preview any day, e.g. `/32x32/cal.png?date=25/12/2026`.

### Schedule
A background scheduler refreshes data and re-announces display presets on fixed minutes past the hour:
weather every 15 minutes, forecast every 30, and the calendar preset hourly. Every minute it publishes
`{"tz": <UTC offset in minutes>, "blue": <bool>}` to `drjonea/display`, so the displays keep local time
across daylight saving changes; `blue` is true during the night window (20:00 to 05:00 local).

### Web dashboard
`http://<server>:5000/` shows the uplink status, the active widgets, all tiles, and preset and console
controls for publishing commands. The **Today's Calendar Theme** panel shows today's date and tile, the
theme's description, the set it came from, the rule that chose it, and any other themes that also match
today but were outranked.

### Calendar themes
![Eight calendar tiles: Alan Turing, Mendeleev, Easter, summer solstice, two advent days, Dickens and Monday: the Moon](images/calendar-themes.png)

*Calendar tiles rendered from the theme collections (the clock fills the blank bottom rows on the display).*

The calendar tile shows the day of week, date and month over a themed 32x22 background image. The bottom
10 rows are left clear, because the display draws its clock there. Themes are defined in JSON
*collections*, one file per set, in *manager/calendar_themes/*. They are re-read on every request, so
edits take effect without a restart.

```json
{
    "description": "Family birthdays.",
    "priority": 100,
    "defaults": {"outline": "#000000"},
    "annual": {
        "13/01": {"title": "Kevin's Birthday", "image": "birthday_kevin.png"}
    }
}
```

A collection can contain any of these rule kinds. When several rules match a day, the **rule kind** decides
first, in this order:

1. `dates`: one specific day, `"dd/mm/yyyy"`
2. `events`: dates calculated each year. These are `easter`, `spring_equinox`, `summer_solstice`,
   `autumn_equinox` and `winter_solstice`. Solstices and equinoxes are placed on the local date.
3. `annual`: the same day every year, `"dd/mm"`
4. `weekdays`: the day of the week, e.g. `"monday"`

If two rules of the same kind match, the collection with the higher `priority` wins. So an entry in
`overrides.json` (a specific date) always wins, and the weekday themes only show on otherwise free days.
Each rule holds a theme: `title`, `image`, an optional text `outline` colour, and optional per-field
`text` colour and position overrides. A collection can also define named `themes` that any collection
reuses by name, and can be switched off with `"enabled": false`. The full format is documented in
*manager/app/calendar_themes.py*.

The current sets, highest priority first:

| Collection | Priority | Contents |
|---|---|---|
| overrides | 1000 | One-off specific dates (empty) |
| birthdays | 100 | Family birthdays |
| seasonal | 80 | Easter, spring and autumn equinoxes, summer solstice |
| advent | 70 | A theme for every day of December |
| tolkien | 50 | The Hobbit and Lord of the Rings anniversaries |
| doctorwho | 45 | Doctor Who episodes and milestones |
| bladerunner, blakes7, scifi, terminator | 40 | Blade Runner, Blake's 7, Alien/Prometheus/Star Trek/Matrix, Terminator |
| marvel | 30 | MCU dates and Marvel debut days |
| midkemia | 20 | Raymond E. Feist's Midkemian calendar |
| computing | 18 | History of computing (Unix and open technology) |
| chemistry | 17 | History of chemistry |
| dickens | 15 | Charles Dickens and the Victorian era |
| weekdays | 10 | Norse and planetary day-of-week themes, and the default |

### Calendar tools
- **`python manager/tools/calendar_report.py [YEAR] [--all]`** lists every themed day of a year, with the
  rule that chose it and anything it hides. It then checks for missing images, unknown theme names,
  duplicate keys and unused images, and exits non-zero on a problem, so it can be run as a check before
  deploying.
- **`python manager/tools/make_calendar_images.py`** regenerates the theme images in
  *manager/static/img/calendar/*. Each image is drawn from a 12x12 ASCII pixel-art sprite in the
  `*_images.py` modules next to it, placed in the corner the text leaves free. To change an image, edit its
  sprite and rerun. Images can also be drawn by hand: any 32x22 PNG works, and other sizes are scaled to
  fit.

## Topics Used
Relative to topic <ORG> which can be set as a parameter. Defaults to drjonea

![Topic hierarchy: one display, all Cosmic Unicorns, or every display](images/topics.jpg)

- drjonea/display/cosmic/<clientid>	
- drjonea/display/cosmic
- drjonea/display
- drjonea/sensor/cosmic/<clientid>

---

## More from Dr Jon EA

- 📺 **Videos:** [Part 1: MQTT + HTTP: The Unusual Architecture Behind My Pico W Display](https://youtu.be/Bp9ovLeLuKA) · [Part 2: EMQX + HAProxy + Ansible: The IoT Stack Behind My Pico W Display](https://youtu.be/ck1F96P57RM)
- 📝 **Write-up:** [New Tiles, No New Firmware: My Pico W Cosmic Unicorn Display and the IoT Stack Behind It](https://drjonea.co.uk/2026/11/09/cosmic-unicorn-pico-w-home-display-mqtt-http-emqx-haproxy-ansible/)
- 🛠️ **Building my projects:** [How to clone and build from my repos](https://drjonea.co.uk/2025/12/15/building-my-projects-from-repo/)
- 🎓 **Courses and training:** [drjonea.co.uk/training](https://drjonea.co.uk/training/)

Made by [Dr Jon Durrant](https://jondurrant.com) at [Dr Jon EA Ltd](https://drjonea.co.uk) · [YouTube](https://www.youtube.com/@drjonea)
