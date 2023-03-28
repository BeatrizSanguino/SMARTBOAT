import time
from gpiozero import CamJamKitRobot
import paho.mqtt.client as mqtt


def on_log(client, userdata, level, buf):
    print("log: "+buf)

def on_connect(client, userdata, flags, rc):
    if rc==0:
        client.connected_flag=True
        print("connected OK")
    else:
        print("Bad connection Return code=", rc)

def on_disconnect(client, userdata, flags, rc=0):
    print("Diconnected result code "+str(rc))

def on_message(client, userdata, message):
	print("message received ", str(message.payload.decode("utf-8")))
	print("message topic= ",message.topic)
	print("message qos= ", message.qos)
	print("message retain flag= ",message.retain)


mqtt.Client.connected_flag=False

broker = "broker.hivemq.com" #external broker
client = mqtt.Client(client_id="P1", clean_session=True, userdata=None)
print("create a new instance")

client.on_connect = on_connect
client.on_disconnect = on_disconnect
#client.on_log = on_log
client.on_message = on_message

print("connecting to broker")
client.connect(broker, port=1883, keepalive=60)

client.loop_start()

while not client.connected_flag:
    print("in wait loop")
    time.sleep(1)

print("in main loop")

print("subscribing to topic","house/bulbs/bulb1")
client.subscribe("house/bulbs/bulb1",qos=2)

print("Publish message to topic","house/bulbs/bulb1")
client.publish(topic="house/bulbs/bulb1",payload="OFF", qos=2, retain=False)

time.sleep(4)
client.loop_stop()

client.disconnect()
