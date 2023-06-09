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
	
time.sleep(30)
# Set variables for the GPIO pins
PIN_TRIGGER=17
PIN_ECHO=18

maxTime = 0.04

# Set the GPIO modes
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(PIN_TRIGGER, GPIO.OUT)
GPIO.setup(PIN_ECHO,GPIO.IN)


# MQTT Connection
mqtt.Client.connected_flag=False

broker = "broker.hivemq.com" #external broker
client_id_name = "robot_sensor_distance"+str(np.random.random()*1000)
client = mqtt.Client(client_id=client_id_name, clean_session=True, userdata=None)
print("create a new client")

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


GPIO.output(PIN_TRIGGER, GPIO.LOW)
time.sleep(2) # Waiting for sensor to settle

freq = 10
period = 1/freq
t0 = time.perf_counter()
time_counter=t0
while True:
    GPIO.output(PIN_TRIGGER, GPIO.LOW)

    GPIO.output(PIN_TRIGGER, GPIO.HIGH)

    time.sleep(0.00001)

    GPIO.output(PIN_TRIGGER, GPIO.LOW)

    pulse_start = time.time()
    timeout = pulse_start + maxTime
    #print("before while pulse start")
    while GPIO.input(PIN_ECHO)==0 and pulse_start < timeout:
	    pulse_start = time.time()
    #print("after while pulse start", pulse_start, timeout)
	    
    
    pulse_end = time.time()
    timeout = pulse_end + maxTime
    #print("before while pulse end")
    while GPIO.input(PIN_ECHO)==1 and pulse_end < timeout:
	    pulse_end = time.time()
    #print("after while pulse end", pulse_end, timeout)
    
    pulse_duration = pulse_end - pulse_start
    distance = round(pulse_duration * 17150, 2)
    #print("Distance:",distance,"cm")
    
    # Publish distance on MQTT topic with 10Hz frequency
    now = time.perf_counter()
    time_elapse = now - t0
    if time_elapse > period:
	    client.publish(topic="robot/sensor_distance",payload=distance, qos=2, retain=False)
	    t0 = time.perf_counter()
	    print("Distance:",distance,"cm")


client.loop_stop()
client.disconnect()
