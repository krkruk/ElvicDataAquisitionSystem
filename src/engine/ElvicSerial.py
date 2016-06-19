import serial
import multiprocessing as mp


UART_DISCONNECTED = "read failed: device reports readiness " \
                    "to read but returned no data (device " \
                    "disconnected or multiple access on port?)"


class SerialMultiprocessReceiver(mp.Process):
    def __init__(self, queue=mp.Queue, serial_params=None):
        mp.Process.__init__(self)
        self.queue = queue
        self.kill_process = mp.Event()
        self.kill_process.clear()
        try:
            if serial_params:
                self.serial = serial.Serial(**serial_params)
            else:
                self.serial = serial.Serial()
        except Exception as e:
            print("Could not establish serial connection.\nAbort process: ", e)
            self.kill_process.set()

    def run(self):
        while not self.kill_process.is_set():
            self.main()

        if self.serial.is_open:
            self.serial.close()
        print("Exit run: {}.".format(self.pid))

    def main(self):
        line = ""
        try:
            line = self.serial.readline().rstrip()
        except Exception as e:
            print("Could not read a line. Continue...\n'{}'".format(e))
            if e.__str__() == UART_DISCONNECTED:
                self.kill_serial()
        except KeyboardInterrupt:
            print("Keyboard Interrupt")
        self.queue.put(line)

    def kill_serial(self):
        self.kill_process.set()
