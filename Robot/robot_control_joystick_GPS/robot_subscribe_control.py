#!/usr/bin/python
# -*- coding:utf-8 -*-
import random
import RPi.GPIO as GPIO
import serial
import time
import paho.mqtt.client as mqtt
import numpy as np


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

f = open('/home/pi/SmartBoat/robot_control_joystick_GPS/test.log','w')

ser.write(('ATE0' + '\r\n').encode())
    
f = open('/home/pi/SmartBoat/robot_control_joystick_GPS/test.log','a')
f.write("ser_in_wainting"+str(ser.in_waiting)+"\n")
f.close()
#print(ser.in_waiting)
while not ser.in_waiting:
    pass

f = open('/home/pi/SmartBoat/robot_control_joystick_GPS/test.log','a')
f.write("ser_in_wainting-after"+str(ser.in_waiting)+"\n")
f.close()
#print(ser.in_waiting)
while ser.in_waiting:
    #response = ser.read(ser.in_waiting).decode()
    response = ser.read_all().decode()
    f = open('/home/pi/SmartBoat/robot_control_joystick_GPS/test.log','a')
    f   .write("response:"+response+"\n")
    f.close()
    #print("response:",response)
    
        

ser.write(('AT+CPIN="6866"' + '\r\n').encode())
f = open('/home/pi/SmartBoat/robot_control_joystick_GPS/test.log','a')
f.write('PIN-waiting response\n')
f.close()
#print("waiting response\n")

f = open('/home/pi/SmartBoat/robot_control_joystick_GPS/test.log','a')
f.write("ser_in_wainting"+str(ser.in_waiting)+"\n")
f.close()
#print(ser.in_waiting)
while not ser.in_waiting:
    pass

f = open('/home/pi/SmartBoat/robot_control_joystick_GPS/test.log','a')
f.write("ser_in_wainting-after"+str(ser.in_waiting)+"\n")
f.close()
#print(ser.in_waiting)
while ser.in_waiting:
    response = ser.read(ser.in_waiting).decode()
    #response = ser.read_all().decode()
    f = open('/home/pi/SmartBoat/robot_control_joystick_GPS/test.log','a')
    f   .write("response:"+response+"\n")
    f.close()
    #print("response:",response)
    
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
    f = open('/home/pi/SmartBoat/robot_control_joystick_GPS/test.log','a')
    f.write("MQTT: in wait loop\n")
    f.close()
    time.sleep(1)
    
f = open('/home/pi/SmartBoat/robot_control_joystick_GPS/test.log','a')
f.write("MQTT: connected\n")
f.close()

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(6,GPIO.OUT)
time.sleep(0.1)
GPIO.output(6,GPIO.HIGH)
time.sleep(2)
GPIO.output(6,GPIO.LOW)
time.sleep(20)

command='AT+CGPS=1,1'
ser.write((command + '\r\n').encode())
f = open('/home/pi/SmartBoat/robot_control_joystick_GPS/test.log','a')
f.write("ser_in_wainting-AT+CGPS=1,1"+str(ser.in_waiting)+"\n")
f.close()
#print(ser.in_waiting)
while not ser.in_waiting:
    pass

f = open('/home/pi/SmartBoat/robot_control_joystick_GPS/test.log','a')
f.write("ser_in_wainting-AT+CGPS1,1-after"+str(ser.in_waiting)+"\n")
f.close()
#print(ser.in_waiting)
while ser.in_waiting:
    #response = ser.read(ser.in_waiting).decode()
    response = ser.read_all().decode()
    f = open('/home/pi/SmartBoat/robot_control_joystick_GPS/test.log','a')
    f   .write("response-AT+CGPS1,1:"+response+"\n")
    f.close()
    #print("response:",response)

freq = 0.5
period = 1/freq
t0 = time.perf_counter()
time_counter=t0
aux=True
while aux:
    now = time.perf_counter()
    time_elapse = now - t0
    
    ser.flushInput()
    ser.flushOutput()
    command="AT+CGPSINFO"
    ser.write((command + '\r\n').encode())
    
    f = open('/home/pi/SmartBoat/robot_control_joystick_GPS/test.log','a')
    f.write("waiting GPS-AT+CGPSINFO\n")
    f.close()
    #print("waiting GPS")

    while not ser.in_waiting:
        pass
        
    f = open('/home/pi/SmartBoat/robot_control_joystick_GPS/test.log','a')
    f.write("AT+CGPSINFO-ser_in_waiting:"+str(ser.in_waiting)+"\n")
    f.close()
    #while ser.in_waiting:
    response = ser.read(ser.in_waiting).decode()
    f = open('/home/pi/SmartBoat/robot_control_joystick_GPS/test.log','a')
    f.write("AT+CGPSINFO-response:"+response+"\n")
    f.close()

    if response.find("+CGPSINFO:")!=-1:
        if ',,,,,,' in response:
            f = open('/home/pi/SmartBoat/robot_control_joystick_GPS/test.log','a')
            f.write('get_fps_position-GPS is not ready\n')
            f.close()
        else:
            index = response.find("+CGPSINFO:")
            cleaned = response[11+index:]
            f=open('/home/pi/SmartBoat/robot_control_joystick_GPS/test.log','a')
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
            if time_elapse > period:
                client.publish(topic="robot/GPS_position", payload=pos, qos=2, retain=False)
                t0 = time.perf_counter()
            f = open('/home/pi/SmartBoat/robot_control_joystick_GPS/test.log','a')
            f.write('get_gps_position-Latitude:'+str(latitude)+"Longitude:"+str(longitude)+"\n")
            f.close()
            
