import serial
from serial.tools import list_ports
import multiprocessing as mp
import time
import datetime


class SerialMultiprocessReceiver(mp.Process):
    def __init__(self, serial_params=None):
        mp.Process.__init__(self)
        self.kill_process = mp.Event()
        self.kill_process.clear()
        try:
            self.serial = serial.Serial(**serial_params) if serial_params else serial.Serial()
        except Exception as e:
            print("Could not establish serial connection. Abort process: ", e)
            self.kill_process.set()

        self.t1 = None
        self.t2 = None

    def run(self):
        while not self.kill_process.is_set():
            self.main()
        print("Exit run {}".format(self.pid))

    def main(self):
        line = ""
        t1 = datetime.datetime.now()
        try:
            line = self.serial.readline().decode("ascii").rstrip()
        except Exception as e:
            print("Could not read a line. Continue ", e)
        t2 = datetime.datetime.now()
        time_diff_ms = (t2 - t1)
        print(line, "- in time: {}".format(time_diff_ms))

    def kill_serial(self):
        self.kill_process.set()


def read_serial_bruteforce():
    with serial.Serial(port=port_list[0].device) as uart:
        for i in range(10):
            line = uart.readline().decode("ascii").rstrip()
            print(line)


def main_func():
    port_list = list_ports.comports()
    for port in port_list:
        print(port.device)

    process_pool = []
    for port in port_list:
        serial_params = {"port": port.device}
        process_pool.append(SerialMultiprocessReceiver(serial_params))

    t1 = datetime.datetime.now()
    for process in process_pool:
        process.start()

    time.sleep(5)

    for process in process_pool:
        process.kill_serial()
        process.join()

    t2 = datetime.datetime.now()
    print("Total app time: ", t2-t1)


if __name__ == "__main__":
    main_func()
