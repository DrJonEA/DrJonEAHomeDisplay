import paho.mqtt.client as mqtt
import json
import time
import sys
import os




user=os.environ.get("MQTT_USER")
passwd=os.environ.get("MQTT_PASSWD")
host= os.environ.get("MQTT_HOST")
port=int(os.environ.get("MQTT_PORT"))
print("MQTT %s:%d - %s\n"%(host,port, user))

connected_topic = "TNG/" + user + "/LC/ON"
disconnected_topic = "TNG/" + user + "/LC/OFF"

sen_topic = "drjonea/sensor/#"

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print("Rcv topic=" +msg.topic+" msg="+str(msg.payload))

client = mqtt.Client(client_id=user)
client.username_pw_set(username=user, password=passwd)
client.on_connect = on_connect
client.on_message = on_message
j = {'online':0}
p = json.dumps(j)
client.will_set(disconnected_topic, p, qos=1, retain=False) #set will

client.connect(host, port, 60)

client.loop_start()


client.subscribe( sen_topic )

    
print("publishing connect")
j = {'online':1}
p = json.dumps(j)
client.publish(connected_topic,p,retain=False,qos=1)


time.sleep(5 * 60)