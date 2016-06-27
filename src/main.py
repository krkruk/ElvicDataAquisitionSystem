from engine import ElvicSerial as es
from engine import ElvicDB as db
from engine import SavingSignal
from engine import XMPPSender
from engine import Device
from serial.tools import list_ports
import sqlite3
import multiprocessing as mp
import queue
import time
import json


AQUIRE_TIME_SECONDS = 5
AQUIRE_ITERATIONS = 1


def until_timeout(start_at_time=time.time(), seconds=0):
    """Measure time and return whether elapsed time satisfies condition.
    Requires start_at_time - time in useconds; seconds - timeout"""
    return time.time() - start_at_time <= seconds


class Engine:
    def __init__(self):
        self.queue_gps = mp.JoinableQueue()
        self.queue_inverter = mp.JoinableQueue()
        self.serial_pool = []
        self.gps = Device.GPS(vid=0x2341, pid=0x0042)
        self.inverter = Device.Inverter(vid=0x1A86, pid=0x7523)
        self.db = db.ElvicDatabase("elvicdb.db")
        self.save_info = SavingSignal.SavingSignalConsole()
        self.xmpp = XMPPSender.MultiprocessingSender("elvic01@jappix.com", "elvic", "elvic02@jappix.com")

        #every new start of the program starts a new recording instance into db
        try:
            self.db.insert_into_DataRecords()
        except sqlite3.OperationalError as e:
            print("Could not connect to the database:\n'{}'".format(e))
            return

        for url, device in self.discover_devices((self.gps.vid_pid, self.inverter.vid_pid)):
            print(url, device)
            if self.gps.match_device_url(url):
                self.serial_pool.append(es.SerialMultiprocessReceiver(self.queue_gps, {"port": device}))
            if self.inverter.match_device_url(url):
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
        for elem in self._queue_gps_iter():
            self.gps.data.append(elem)

        for elem in self._queue_inverter_iter():
            self.inverter.data.append(elem)

    def export_to_database(self):
        self.save_info.on_save_start()
        for elem in self.gps.data:
            self.db.insert_into_gps(elem)

        for elem in self.inverter.data:
            self.db.insert_into_inverter(elem)

        self.db.commit()
        self.gps.data.clear()
        self.inverter.data.clear()
        self.save_info.on_save_stop()

    def create_xmpp_msg(self):
        gps_vtg = self.gps.get_last_VTG()
        gps_gga = self.gps.get_last_GGA()
        inverter = self.inverter.get_last_element()
        gps = {"VTG": gps_vtg, "GGA": gps_gga}
        msg = {"inv": inverter, "gps": gps}
        return json.dumps(msg)

    def any_serials_alive(self):
        """Checks whether there is any active serial opened. The method returns
        number of active serials. If none is active, 0 is returned."""
        return sum([process.is_alive() for process in self.serial_pool])

    def main(self):
        self.xmpp.start()
        for process in self.serial_pool:
            process.start()

        while self.any_serials_alive():
            for i in range(AQUIRE_ITERATIONS):
                time.sleep(AQUIRE_TIME_SECONDS)
                self.acquire_data()
                msg = self.create_xmpp_msg()
                print(msg)
                self.xmpp.send_msg(msg)

            self.export_to_database()
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
