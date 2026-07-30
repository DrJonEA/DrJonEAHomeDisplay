# DrJonEAHomeDisplay
A display control architecture for my home. Initially using the 
[PIMORONI Cosmic Unicorn V1](https://shop.pimoroni.com/products/space-unicorns?variant=40842626596947).
Each device is a IoT devices publishing temperature and humidity (from AHT10) over MQTT. 
Then responding to commands over MQTT to provide details of what to share.

To allow a Cosmic Unicorn to adapt to different data to visualise I went with a simple LVGL two tile 
architecture. A local tile that just displays local data: Clock, Temperature, Humidity and Status. Plus a 
Image tile that pulls an image of HTTP to display. Overlays of clock and scroll text are also supported.

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

The server for this architecture is a work in progress. It will uses Python, Paho and Pillow. Experiments 
towards this are included in the *exp* folder.

## Firmware

### Cosmic Unicorn V1
Firmware build is targetted at the Cosmic Unicorn using a Pico W. Other firmware may be added over time.

Unit can be configured over USB Serial by sending a JSON string.  See *ex[/pyConofig* as example.

## Server
Server is still WIP current experiment is *exp/WebDSP/app.py*.



