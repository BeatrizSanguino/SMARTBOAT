import time

from gpiozero import CamJamKitRobot
from gpiozero import DistanceSensor
import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt
import numpy as np


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
	print("message topic= ",message.topic, "message= ", str(message.payload.decode("utf-8")))
	global message_flag
	message_flag=str(message.payload.decode("utf-8"))
	

robot=CamJamKitRobot()

mqtt.Client.connected_flag=False

broker = "broker.hivemq.com" #external broker
client = mqtt.Client(client_id="robo_5533", clean_session=True, userdata=None)
print("create a new instance")

client.on_connect = on_connect
client.on_disconnect = on_disconnect
#client.on_log = on_log
client.on_message = on_message

print("connecting to broker")
client.connect(broker, port=1883, keepalive=60)

client.loop_start() #client.loop_forever()

while not client.connected_flag:
    print("in wait loop")
    time.sleep(1)

print("in main loop")
message_flag="stop"
	
topic="robot/motor/action"
print("subscribing to topic",topic)
client.subscribe(topic,qos=2)

print(message_flag)

while True:
    if message_flag== "stop":
	    #print("robot stop")
	    robot.stop()
    elif message_flag=="forward":
	    robot.forward()
	    #print("robot moving forward")
    elif message_flag=="backward":
	    robot.backward()
	    #print("robot moving backward")
    elif message_flag=="left":
	    robot.left()
	    #print("robot moving left")
    elif message_flag=="right":
	    robot.right()


client.loop_stop()
client.disconnect()
