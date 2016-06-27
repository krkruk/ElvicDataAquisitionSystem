from engine import ElvicSerial as es
from engine import ElvicDB as db
from engine import SavingSignal
from serial.tools import list_ports
import sqlite3
import multiprocessing as mp
import queue
import time


SLEEP_TIME_SECONDS = 30


def until_timeout(start_at_time=time.time(), seconds=0):
    """Measure time and return whether elapsed time satisfies condition.
    Requires start_at_time - time in useconds; seconds - timeout"""
    return time.time() - start_at_time <= seconds


class GPS:
    """GPS Serial constants. These allow finding the best uart device
    and assign it to the proper queue and the database"""
    vid = 0x2341
    pid = 0x0042
    vid_pid = (vid, pid)


class Inverter:
    """GPS Serial constants. These allow finding the best uart device
    and assign it to the proper queue and the database"""
    vid = 0x1A86
    pid = 0x7523
    vid_pid = (vid, pid)


class Engine:
    def __init__(self):
        self.queue_gps = mp.JoinableQueue()
        self.queue_inverter = mp.JoinableQueue()
        self.serial_pool = []
        self.data_gps = []
        self.data_inverter = []
        self.db = db.ElvicDatabase("/home/krzysztof/Programming/Python/Elvic/elvicdb.db")
        self.save_info = SavingSignal.SavingSignalConsole()

        #every new start of the program starts a new recording instance into db
        try:
            self.db.insert_into_DataRecords()
        except sqlite3.OperationalError as e:
            print("Could not connect to the database:\n'{}'".format(e))
            return

        for url, device in self.discover_devices((GPS.vid_pid, Inverter.vid_pid)):
            print(url, device)
            if GPS.vid_pid == url:
                self.serial_pool.append(es.SerialMultiprocessReceiver(self.queue_gps, {"port": device}))
            if Inverter.vid_pid == url:
                self.serial_pool.append(es.SerialMultiprocessReceiver(self.queue_inverter, {"port": device}, ))

    def __del__(self):
        for process in self.serial_pool:
            process.kill_serial()
        self.db.commit()
        del self.db

    def _queue_gps_iter(self):
        """Allow iterating over a queue until the queue is empty. When empty
        StopIteration exception is raised"""
        try:
            yield from iter(self.queue_gps.get_nowait, None)
        except queue.Empty:
            raise StopIteration()

    def _queue_inverter_iter(self):
        """Allow iterating over a queue until the queue is empty. When empty
        StopIteration exception is raised"""
        try:
            yield from iter(self.queue_inverter.get_nowait, None)
        except queue.Empty:
            raise StopIteration()

    def acquire_data(self):
        self.save_info.on_save_start()

        for elem in self._queue_gps_iter():
            self.db.insert_into_gps(elem)

        for elem in self._queue_inverter_iter():
            self.db.insert_into_power_inverter(elem)

        self.db.commit()
        self.save_info.on_save_stop()

    def any_serials_alive(self):
        """Checks whether there is any active serial opened. The method returns
        number of active serials. If none is active, 0 is returned."""
        return sum([process.is_alive() for process in self.serial_pool])

    def main(self):
        for process in self.serial_pool:
            process.start()

        while self.any_serials_alive():
            time.sleep(SLEEP_TIME_SECONDS)
            self.acquire_data()
        else:
            print("No serials. Program terminate.")

    @staticmethod
    def discover_devices(devices):
        """Allows discovering a uart device based on VID and PID info. The method
        returns a list formed as [(vid, pid), device_url]. The function requires
        a tuple 'devices' as (vid, pid)."""
        for device in list_ports.comports():
            device_vid_pid = (device.vid, device.pid)
            if device_vid_pid in devices:
                dev = [item for item in devices if item == device_vid_pid]
                dev.append(device.device)
                yield dev


if __name__ == "__main__":
    engine = Engine()
    try:
        engine.main()
    except KeyboardInterrupt:
        del engine
