import time
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
    global M1
    global M2
    msg_aux = message.payload.decode("utf-8")
    msg = msg_aux.split(",")
    M1=float(msg[0])
    M2=float(msg[1])
 

time.sleep(30)

# Initialization of motor actions
M1=0.0
M2=0.0
    
# Set the GPIO modes
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Set variables for the GPIO motor pins
pinMotorA1 = 19
pinMotorA2 = 13
pinMotorA_EN = 26
pinMotorB1 = 6
pinMotorB2 = 5
pinMotorB_EN = 12

freq = 40 # how many times to turn the pin on and off each second
speed_factor = 10.0 # percentage of the maximum speed

# Set the GPIO Pin mode to be Output
GPIO.setup(pinMotorA1, GPIO.OUT)
GPIO.setup(pinMotorA2, GPIO.OUT)
GPIO.setup(pinMotorA_EN, GPIO.OUT)
GPIO.setup(pinMotorB1, GPIO.OUT)
GPIO.setup(pinMotorB2, GPIO.OUT)
GPIO.setup(pinMotorB_EN, GPIO.OUT)


pwm_B = GPIO.PWM(pinMotorB_EN, freq)
pwm_A = GPIO.PWM(pinMotorA_EN, freq)


# Start the software PWM with a duty cycle of 0 (i.e. not moving)
pwm_B.start(0)
pwm_A.start(0)


# MQTT Connection
mqtt.Client.connected_flag=False

broker = "broker.hivemq.com" #external broker

client_id_name = "robot_"+str(np.random.random()*1000)
client = mqtt.Client(client_id=client_id_name, clean_session=True, userdata=None)
print("created a new client")

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

# Subscribing to motor action topic
topic1="robot/motor/action"
print("subscribing to topic",topic1)
client.subscribe(topic1,qos=2)


while True:
    #print(M1,M2)
    
    # Action for motor 1
    if M1<0: # motor 1 backward
        if round(M1,4)<-1:
            M1=-1.0
        GPIO.output(pinMotorA1, GPIO.HIGH)
        GPIO.output(pinMotorA2, GPIO.LOW)
        dutycycle = abs(round(M1,4))*speed_factor #how long the pin stays on each cycle, as a percentage
        pwm_A.ChangeDutyCycle(dutycycle)
    
    elif M1>0: # motor 1 forward
        if round(M1,4)>1:
            M1=1
        GPIO.output(pinMotorA1, GPIO.LOW)
        GPIO.output(pinMotorA2, GPIO.HIGH)
        dutycycle = abs(round(M1,4))*speed_factor
        pwm_A.ChangeDutyCycle(dutycycle)
    
    elif M1==0: # motor 1 stopped
        GPIO.output(pinMotorA1, GPIO.LOW)
        GPIO.output(pinMotorA2, GPIO.LOW)
        
	# Action for motor 2
    if M2<0: # motor 2 backward
        if round(M2,4)<-1:
            M2=-1.0
        GPIO.output(pinMotorB1, GPIO.HIGH)
        GPIO.output(pinMotorB2, GPIO.LOW)
        dutycycle = abs(round(M2,4))*speed_factor
        pwm_B.ChangeDutyCycle(dutycycle)
    
    elif M2>0: # motor 2 forward
        if round(M2,4)>1:
            M2=1
        GPIO.output(pinMotorB1, GPIO.LOW)
        GPIO.output(pinMotorB2, GPIO.HIGH)
        dutycycle = abs(round(M2,4))*speed_factor
        pwm_B.ChangeDutyCycle(dutycycle)
    
    elif M2==0: # motor 2 stopped
        GPIO.output(pinMotorB1, GPIO.LOW)
        GPIO.output(pinMotorB2, GPIO.LOW)


client.loop_stop()
client.disconnect()
