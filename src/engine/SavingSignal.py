class SavingSinglaInterface:

    def on_save_start(self, *args):
        raise NotImplemented("on_save_start not implemented yet!")

    def on_save_stop(self, *args):
        raise NotImplemented("on_save_stop not implemented yet!")

class SavingSignalConsole(SavingSinglaInterface):
    def on_save_start(self, *args):
        print("Start saving a data into database")

    def on_save_stop(self, *args):
        print("DATA WRITTEN!")

class SavingSignalRPiLED(SavingSinglaInterface):
    pass