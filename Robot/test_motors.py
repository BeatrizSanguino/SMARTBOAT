# Motor test code

import time
from gpiozero import CamJamKitRobot

robot=CamJamKitRobot()

# turn the motors on
robot.forward()

# wait 1 second
time.sleep(1)

# turn the motors off
robot.stop()
