"""Entrypoint for the display manager Flask app.

Application logic lives in the app/ package (config, mqtt_service, images,
weather, routes); this module just wires it together and runs the server.
"""
import logging

from app import create_app
from app.config import Config, masked

config = Config()
print("MQTT %s:%d" % (config.MQTT_HOST, config.MQTT_PORT))
print("Client: %s" % masked(config.MQTT_CLIENT_ID))
print("User: %s" % masked(config.MQTT_USER))

app = create_app(config)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    app.mqtt_service.start_background_thread()
    app.scheduler.start()
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
