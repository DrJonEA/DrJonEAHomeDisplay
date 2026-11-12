import paho.mqtt.client as mqtt
import json
import time
import os
import sys
from icmplib import multiping



user=os.environ.get("MQTT_USER")
passwd=os.environ.get("MQTT_PASSWD")
host= os.environ.get("MQTT_HOST")
port=int(os.environ.get("MQTT_PORT"))
print("MQTT %s:%d - %s\n"%(host,port, user))

ping_topic = "GRP/ALL/TPC/PING"
connected_topic = "TNG/" + user + "/LC/ON"
disconnected_topic = "TNG/" + user + "/LC/OFF"

#pong_topic = "TNG/" + targetId + "/TPC/PONG"
pong_topic = "TNG/+/TPC/PONG"
#lc_topic = "TNG/" + targetId + "/LC/#"

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    


pingStart = None   # monotonic time the ping was sent
responses = {}     # nodeId -> round-trip time in ms
nodeIps = {}       # nodeId -> IP address reported in the pong (if any)

ICMP_COUNT = 10    # echo requests per node

# The callback for when a PUBLISH message is received from the server.

def on_message(client, userdata, msg):
    rcvTime = time.monotonic()
    print("Rcv topic=" +msg.topic+" msg="+str(msg.payload))
    if pingStart is None:
        return
    # Topic is TNG/<nodeId>/TPC/PONG
    nodeId = msg.topic.split("/")[1]
    if nodeId not in responses:
        responses[nodeId] = (rcvTime - pingStart) * 1000.0
    try:
        ip = json.loads(msg.payload).get("ip")
        if ip:
            nodeIps[nodeId] = ip
    except (ValueError, AttributeError):
        pass

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
client.subscribe( pong_topic )
    
print("publishing connect")
j = {'online':1}
p = json.dumps(j)
client.publish(connected_topic,p,retain=False,qos=1)

pingId = 0;
j = {'id': pingId}
p = json.dumps(j)
print("Publishing ping %s"%p)
pingStart = time.monotonic()
infot = client.publish(ping_topic, p,retain=False, qos=1)
infot.wait_for_publish()
pingId = pingId + 1

time.sleep(3)

print("\nMQTT responses after 10s: %d node(s)"%len(responses))
for nodeId, ms in sorted(responses.items(), key=lambda kv: kv[1]):
    print("  %-30s %-16s %8.1f ms"%(nodeId, nodeIps.get(nodeId, "-"), ms))

j = {'online':0}
p = json.dumps(j)
infot = client.publish(disconnected_topic, p, retain=False, qos=1)
infot.wait_for_publish()
client.disconnect()
client.loop_stop()

# ICMP ping the nodes that reported an IP address
if nodeIps:
    print("\nICMP ping %d node(s), %d echoes each..."%(len(nodeIps), ICMP_COUNT))
    ipToNode = {ip: nodeId for nodeId, ip in nodeIps.items()}
    hosts = multiping(list(ipToNode.keys()), count=ICMP_COUNT, interval=0.2,
                      timeout=1, privileged=False)
    print("  %-30s %-16s %8s %8s %8s %8s %6s %10s"%(
        "node", "ip", "min", "avg", "max", "jitter", "loss", "mqtt"))
    for h in sorted(hosts, key=lambda h: (not h.is_alive, h.avg_rtt)):
        nodeId = ipToNode[h.address]
        if not h.is_alive:
            print("  %-30s %-16s %35s %6s %8.1f ms"%(
                nodeId, h.address, "no reply", "100%", responses[nodeId]))
            continue
        print("  %-30s %-16s %8.1f %8.1f %8.1f %8.1f %5.0f%% %8.1f ms"%(
            nodeId, h.address, h.min_rtt, h.avg_rtt, h.max_rtt, h.jitter,
            h.packet_loss * 100, responses[nodeId]))
else:
    print("\nNo nodes reported an IP address; skipping ICMP ping")

