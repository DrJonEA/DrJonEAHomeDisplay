"""Preset MQTT display commands shown as quick-action buttons in the dashboard.

Add a new preset here to get a matching button in the Quick Commands panel -
no template or route changes needed.
"""
import json

DISPLAY_TOPIC = "drjonea/display"

PRESETS = [
    {
        "key": "weather",
        "label": "WEATHER",
        "topic": DISPLAY_TOPIC,
        "payload": {
            "layout": "layout2",
            "widgets": [
                {"type": "img", "data": "weather.brg565"},
            ],
        },
    },
    {
        "key": "forecast",
        "label": "FORECAST",
        "topic": DISPLAY_TOPIC,
        "payload": {
            "layout": "layout2",
            "widgets": [
                {"type": "img", "data": "forecast.brg565"},
            ],
        },
    },
    {
        "key": "solar",
        "label": "SOLAR",
        "topic": DISPLAY_TOPIC,
        "payload": {
            "layout": "layout2",
            "widgets": [
                {"type": "img", "data": "solar.brg565"},
            ],
        },
    },
    {
        "key": "calendar",
        "label": "CALENDAR",
        "topic": DISPLAY_TOPIC,
        "payload": {
            "layout": "layout2",
            "widgets": [
                {"type": "img", "data": "cal.brg565"},
                {"type": "clock"},
            ],
        },
    },
    {
        "key": "sensors",
        "label": "SENSORS",
        "topic": DISPLAY_TOPIC,
        "payload": {
            "layout": "layout2",
            "widgets": [
                {"type": "img", "data": "env.brg565"},
            ],
        },
    },
    {
        "key": "network",
        "label": "NETWORK",
        "topic": DISPLAY_TOPIC,
        "payload": {
            "layout": "layout2",
            "widgets": [
                {"type": "img", "data": "net.brg565"},
            ],
        },
    },
    {
        "key": "ping",
        "label": "PING",
        "topic": DISPLAY_TOPIC,
        "payload": {
            "layout": "layout2",
            "widgets": [
                {"type": "img", "data": "ping.brg565"},
            ],
        },
    },
    {
        "key": "pride",
        "label": "PRIDE",
        "topic": DISPLAY_TOPIC,
        "payload": {
            "layout": "layout2",
            "widgets": [
                {"type": "img", "data": "pride.brg565"},
                {"type": "txt", "data": "Pride"},
                {"type": "clock"},
            ],
        },
    },
]


def preset_payload_json(preset):
    return json.dumps(preset["payload"])


def get_preset(key):
    for preset in PRESETS:
        if preset["key"] == key:
            return preset
    raise KeyError(f"Unknown preset: {key}")
