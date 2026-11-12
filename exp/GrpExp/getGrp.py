import paho.mqtt.client as mqtt
import json
import time
import sys
import os


if (len(sys.argv) != 2):
    print("Require target ID as param")
    sys.exit()


targetId = sys.argv[1]


    
user=os.environ.get("MQTT_USER")
passwd=os.environ.get("MQTT_PASSWD")
host= os.environ.get("MQTT_HOST")
port=int(os.environ.get("MQTT_PORT"))
print("MQTT %s:%d - %s\n"%(host,port, user))

connected_topic = "TNG/" + user + "/LC/ON"
disconnected_topic = "TNG/" + user + "/LC/OFF"

lc_topic = "TNG/" + targetId + "/LC/#"
twin_topics = "TNG/+/TWIN/#"
state_topics = "TNG/+/STATE/#"
grp_topics = "GRP/" + targetId + "/#"
get_topic = "GRP/" + targetId + "/TWIN/GET"
set_topic = "GRP/" + targetId + "/TWIN/SET"

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

#client.subscribe( lc_topic )

#client.subscribe( state_topics )
#client.subscribe( twin_topics )
client.subscribe( grp_topics )
    
print("publishing connect")
j = {'online':1}
p = json.dumps(j)
client.publish(connected_topic,p,retain=False,qos=1)


#j = {'select': ["clientId", "reported.temp"], 'as':["id", "temp"], 'query':13,
#     'where': {'column': "reported.temp", 'op': ">", 'value': 10} }
j = {'select': ["clientId"], 'query':14}
p = json.dumps(j)
print("Publishing Set %s"%p)
infot = client.publish(get_topic, p,retain=False, qos=1)
infot.wait_for_publish()

time.sleep(30)