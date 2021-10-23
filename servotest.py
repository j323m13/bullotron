import pindefinitions as pin

from gpiozero import PWMOutputDevice 
##from gpiozero import Servo #Does not support active_high=False
from time import sleep



#from gpiozero.pins.pigpio import PiGPIOFactory
#factory = PiGPIOFactory()
#servo = Servo(pin.SERVO, pin_factory=factory)
servo = PWMOutputDevice(pin.SERVO,active_high=False)

while True:
    servo.value =0.01
    print("mid")
    sleep(0.5)
    servo.value = 0.02
    print("min")
    sleep(1)
    servo.value = 0.01
    print("mid")
    sleep(0.5)
    servo.value = 0.2
    print("max")
    sleep(1)
