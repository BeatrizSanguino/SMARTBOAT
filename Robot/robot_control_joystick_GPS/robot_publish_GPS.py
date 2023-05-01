#!/usr/bin/python
# -*- coding:utf-8 -*-
import random
import RPi.GPIO as GPIO
import serial
import time
import paho.mqtt.client as mqtt
import numpy as np


def start_gps_session():
    f = open('/home/pi/SmartBoat/robot_control_joystick_GPS/robot_publish_GPS.log','a')
    f.write('Starting GPS session\n')
    f.close()
    send_at_command('AT+CGPS=1,1')
    while not is_gps_ready():
        pass
    f = open('/home/pi/SmartBoat/robot_control_joystick_GPS/robot_publish_GPS.log','a')
    f.write('GPS session started.\n')
    f.close()

def is_gps_ready():
    response = send_at_command('AT+CGPSINFO')
    f = open('/home/pi/SmartBoat/robot_control_joystick_GPS/robot_publish_GPS.log','a')
    f.write("response in is_ready:"+response+"\n")
    f.close()
    if response.find("+CGPSINFO:")!=-1:
        if ',,,,,,' in response:
            f = open('/home/pi/SmartBoat/robot_control_joystick_GPS/robot_publish_GPS.log','a')
            f.write('GPS is not ready\n')
            f.close()
            return False
        else:
            return True
    else:
        f = open('/home/pi/SmartBoat/robot_control_joystick_GPS/robot_publish_GPS.log','a')
        f.write('Error getting GPS info\n')
        f.close()
        return False

def send_at_command(command):
   # with serial.Serial('/dev/ttyUSB2', 115200) as ser:
    f = open('/home/pi/SmartBoat/robot_control_joystick_GPS/robot_publish_GPS.log','a')
    f.write("send_at_command:"+command+"\n")
    f.close()
    ser.write((command + '\r\n').encode())
    #time.sleep(2)
    f = open('/home/pi/SmartBoat/robot_control_joystick_GPS/robot_publish_GPS.log','a')
    f.write("send_at_command-number of characters: "+str(ser.in_waiting)+"\n")
    f.close()
    #if ser.in_waiting:
#    time.sleep(0.01)
    #    response = ser.read(ser.in_waiting).decode()
        
    while not ser.in_waiting:
        pass
    f = open('/home/pi/SmartBoat/robot_control_joystick_GPS/robot_publish_GPS.log','a')
    f.write("send_at_command-number of characters after: "+str(ser.in_waiting)+"\n")
    f.close()
    while ser.in_waiting:
        response = ser.read_all().decode()
        f = open('/home/pi/SmartBoat/robot_control_joystick_GPS/robot_publish_GPS.log','a')
        f.write("send_at_command-response: "+str(response)+"\n")
        f.close()
        return response
    

def get_gps_position():
    f = open('/home/pi/SmartBoat/robot_control_joystick_GPS/robot_publish_GPS.log','a')
    f.write("get_gps_position\n")
    f.close()
    response = send_at_command('AT+CGPSINFO')
    if response.find("+CGPSINFO:")!=-1:
        if ',,,,,,' in response:
            f = open('/home/pi/SmartBoat/robot_control_joystick_GPS/robot_publish_GPS.log','a')
            f.write('get_fps_position-GPS is not ready\n')
            f.close()
            return None
        else:
            index = response.find("+CGPSINFO:")
            cleaned = response[11+index:]
            f=open('/home/pi/SmartBoat/robot_control_joystick_GPS/robot_publish_GPS.log','a')
            f.write("get_gps_position-cleaned:"+cleaned+"\n")
            f.close()
            latitude = float(cleaned[:2]) + (float(cleaned[2:11])/60)
            NorthOrSouth = cleaned[12]
			
            longitude = float(cleaned[14:17]) + (float(cleaned[17:26])/60)
            EastOrWest = cleaned[27]

            if NorthOrSouth == 'S': latitude = -latitude
            if EastOrWest == 'W': longitude = -longitude
			
            #print(latitude,longitude)
			
            pos = str(latitude) + ", " + str(longitude)
            client.publish(topic="robot/GPS_position", payload=pos, qos=2, retain=False)
            f = open('/home/pi/SmartBoat/robot_control_joystick_GPS/robot_publish_GPS.log','a')
            f.write('get_gps_position-Latitude:'+str(latitude)+"Longitude:"+str(longitude)+"\n")
            f.close()
            return (latitude, longitude)	
    else:
        f = open('/home/pi/SmartBoat/robot_control_joystick_GPS/robot_publish_GPS.log','a')
        f.write('get_gps_position-Error getting GPS position\n')
        f.close()
        return None

def power_on(power_key):
        f = open('/home/pi/SmartBoat/robot_control_joystick_GPS/robot_publish_GPS.log','a')
        f.write('Power_on: SIM7600X is starting\n')
        f.close()
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(power_key,GPIO.OUT)
        time.sleep(0.1)
        GPIO.output(power_key,GPIO.HIGH)
        time.sleep(2)
        GPIO.output(power_key,GPIO.LOW)
        time.sleep(20)
        ser.flushInput()
        ser.flushOutput()
        f = open('/home/pi/SmartBoat/robot_control_joystick_GPS/robot_publish_GPS.log','a')
        f.write('Power_on: SIM7600X is ready\n')
        f.close()

def power_down(power_key):
	#print('SIM7600X is loging off:')
	GPIO.output(power_key,GPIO.HIGH)
	time.sleep(3)
	GPIO.output(power_key,GPIO.LOW)
	time.sleep(18)
	#print('Good bye')

def on_connect(client, userdata, flags, rc):
    if rc==0:
        client.connected_flag=True
        print("Connected OK")
    else:
        print("Bad connection. Return code=", rc)

def on_disconnect(client, userdata, flags, rc):
    print("Disconnected result code "+str(rc))


# Serial port configuration
ser = serial.Serial('/dev/ttyUSB2',115200) #open serial port
ser.flushInput()

power_key = 6
rec_buff = ''
time_count = 0


ser.flushInput()
r = send_at_command('AT+CPIN="6866"')
#ser.write('AT+CPIN="6866"\r\n'.encode())

f = open('/home/pi/SmartBoat/robot_control_joystick_GPS/robot_publish_GPS.log','w')
f.write("Response to AT pin:"+r+"\n")
f.close()

time.sleep(5)

mqtt.Client.connected_flag=False
    
broker = "broker.hivemq.com"
client_id_name = "robot_gps"+str(np.random.random()*1000)
client = mqtt.Client(client_id=client_id_name, clean_session=True, userdata=None)
    
client.on_connect = on_connect
client.on_disconnect = on_disconnect
    
client.connect(broker, port=1883, keepalive=60)
    
client.loop_start()
    
while not client.connected_flag:
    f = open('/home/pi/SmartBoat/robot_control_joystick_GPS/robot_publish_GPS.log','a')
    f.write("MQTT: in wait loop\n")
    f.close()
    time.sleep(1)
    
f = open('/home/pi/SmartBoat/robot_control_joystick_GPS/robot_publish_GPS.log','a')
f.write("MQTT: connected\n")
f.close()

time.sleep(2)

power_on(power_key)
start_gps_session()
freq = 0.5
period = 1/freq
t0 = time.perf_counter()
time_counter=t0
while True:
    now = time.perf_counter()
    time_elapse = now - t0
    if time_elapse > period:
        f = open('/home/pi/SmartBoat/robot_control_joystick_GPS/robot_publish_GPS.log','a')
        f.write("time:"+str(time_elapse)+"\n")
        f.close()
        get_gps_position()
        t0 = time.perf_counter()

