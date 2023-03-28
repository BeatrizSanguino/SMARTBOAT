import time
import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt
import numpy as np


M1=0.0
M2=0.0
	
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
    global M1
    global M2
    msg_aux = message.payload.decode("utf-8")
    msg = msg_aux.split(",")
    M1=float(msg[0])
    M2=float(msg[1])
    
    
    
	

# Set the GPIO modes
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Set variables for the GPIO motor pins
pinMotorA1 = 8
pinMotorA2 = 7
pinMotorB1 = 10
pinMotorB2 = 9

freq = 40 # how many times to turn the pin on and off each second
#dutyCycle = 30 # how long the pin stays on each cycle, as a percentage

# Set the GPIO Pin mode to be Output
GPIO.setup(pinMotorA1, GPIO.OUT)
GPIO.setup(pinMotorA2, GPIO.OUT)
GPIO.setup(pinMotorB1, GPIO.OUT)
GPIO.setup(pinMotorB2, GPIO.OUT)

# Set the GPIO to software PWM with a duty cycle of 0 (i.e. not moving)
pwmMotorA1 = GPIO.PWM(pinMotorA1, freq)
pwmMotorA2 = GPIO.PWM(pinMotorA2, freq)
pwmMotorB1 = GPIO.PWM(pinMotorB1, freq)
pwmMotorB2 = GPIO.PWM(pinMotorB2, freq)

# Start the software PWM with a duty cycle of 0 (i.e. not moving)
pwmMotorA1.start(0)
pwmMotorA2.start(0)
pwmMotorB1.start(0)
pwmMotorB2.start(0)


mqtt.Client.connected_flag=False

broker = "broker.hivemq.com" #external broker

client_id_name = "robot_"+str(np.random.random()*1000)
client = mqtt.Client(client_id=client_id_name, clean_session=True, userdata=None)
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

	
topic1="robot/motor/action"
print("subscribing to topic",topic1)
client.subscribe(topic1,qos=2)


while True:
    #print(M1,M2)
    if M1<0:
        if round(M1,4)<-1:
            M1=-1.0
        dutycycle = abs(round(M1,4))*10.0
        pwmMotorA1.ChangeDutyCycle(dutycycle)
        pwmMotorA2.ChangeDutyCycle(0)
    elif M1>0:
        if round(M1,4)>1:
            M1=1
        pwmMotorA1.ChangeDutyCycle(0)
        pwmMotorA2.ChangeDutyCycle(abs(round(M1,4))*10)
    elif M1==0:
        pwmMotorA1.ChangeDutyCycle(0)
        pwmMotorA2.ChangeDutyCycle(0)
	
    if M2<0:
        if round(M2,4)<-1:
            M2=-1.0
        pwmMotorB1.ChangeDutyCycle(abs(round(M2,4))*10)
        pwmMotorB2.ChangeDutyCycle(0)
    
    elif M2>0:
        if round(M2,4)>1:
            M2=1
        pwmMotorB1.ChangeDutyCycle(0)
        pwmMotorB2.ChangeDutyCycle(abs(round(M2,4))*10)
    
    elif M2==0:
        pwmMotorB1.ChangeDutyCycle(0)
        pwmMotorB2.ChangeDutyCycle(0)

client.loop_stop()
client.disconnect()
