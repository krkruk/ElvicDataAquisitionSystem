class SavingSingalInterface:
    def on_save_start(self, *args):
        raise NotImplemented("on_save_start not implemented yet!")

    def on_save_stop(self, *args):
        raise NotImplemented("on_save_stop not implemented yet!")


class SavingSignalConsole(SavingSingalInterface):
    def on_save_start(self, *args):
        print("Start saving a data into database")

    def on_save_stop(self, *args):
        print("DATA WRITTEN!")

try:
    import RPi.GPIO as GPIO
except ImportError:
    pass


class SavingSignalRPiLED(SavingSingalInterface):
    LED = 4

    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.LED, GPIO.OUT)

    def on_save_start(self, *args):
        GPIO.output(self.LED, 1)

    def on_save_stop(self, *args):
        GPIO.output(self.LED, 0)
