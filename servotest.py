import pindefinitions as pin

from gpiozero import Servo
from time import sleep

#from gpiozero.pins.pigpio import PiGPIOFactory
#factory = PiGPIOFactory()
#servo = Servo(pin.SERVO, pin_factory=factory)
servo = Servo(pin.SERVO)

while True:
    servo.mid()
    print("mid")
    sleep(0.5)
    servo.min()
    print("min")
    sleep(1)
    servo.mid()
    print("mid")
    sleep(0.5)
    servo.max()
    print("max")
    sleep(1)
