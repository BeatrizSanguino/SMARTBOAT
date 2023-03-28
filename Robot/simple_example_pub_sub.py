import time
from gpiozero import CamJamKitRobot
import paho.mqtt.client as mqtt


def on_message(client, userdata, message):
	print("message received ", str(message.payload.decode("utf-8")))
	print("message topic= ",message.topic)
	print("message qos= ", message.qos)
	print("message retain flag= ",message.retain)


broker = "broker.hivemq.com" #external broker

client = mqtt.Client(client_id="P1", clean_session=True, userdata=None)
print("create a new instance")

client.on_message = on_message

client.connect(broker, port=1883, keepalive=60)
print("connecting to broker")

client.loop_start()

print("subscribing to topic","house/bulbs/bulb1")
client.subscribe("house/bulbs/bulb1",qos=2)

print("Publish message to topic","house/bulbs/bulb1")
client.publish("house/bulbs/bulb1",payload="OFF", qos=2, retain=False)

time.sleep(4)
client.loop_stop()



#robot=CamJamKitRobot()

# turn the motors on
#robot.forward()

# wait 1 second
#time.sleep(1)

# turn the motors off
#robot.stop()

