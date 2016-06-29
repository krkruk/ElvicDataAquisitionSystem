import serial
import multiprocessing as mp


UART_DISCONNECTED = "read failed: device reports readiness " \
                    "to read but returned no data (device " \
                    "disconnected or multiple access on port?)"


class SerialMultiprocessReceiver(mp.Process):
    def __init__(self, queue=mp.Queue, serial_params={}):
        """Initializes a serial device.
        queue - multiprocessing queue. It comprises the data
                received form the device
        serial_params - a dictionary of parameters required by PySerial"""
        super(SerialMultiprocessReceiver, self).__init__()
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
        """Kill a process if it is needed. Exits the main process loop."""
        self.kill_process.set()


if __name__ == "__main__":
    import pynmea2
    queue = mp.Queue()
    p = SerialMultiprocessReceiver(queue, {"port": "/dev/ttyUSB0"})
    p.start()
    omit = True

    while True:
        data = ""
        line = ""
        try:
            data = queue.get()
        except KeyboardInterrupt:
            break
        try:
            if omit:
                omit = False
            else:
                line = data.decode("ascii")
        except KeyboardInterrupt:
            break

        if "$GPGGA" in line:
            parsed = pynmea2.parse(line)
            print(line, "------", "lon/lat:", "{}/{}".format(parsed.longitude, parsed.latitude), parsed.num_sats)


    p.kill_serial()
