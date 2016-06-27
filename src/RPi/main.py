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
import os.path

ACQUIRE_TIME_SECONDS = 5
ACQUIRE_ITERATIONS = 1
TEXT_DEFAULT_SETTINGS = """
{
    "ACQUIRE_ITERATIONS": 1,
    "ACQUIRE_TIME_SECONDS": 5,
    "db_name": "elvicdb.db",
    "gps_param": {
        "vid": 9025,
        "pid": 66,
        "serial_params": {}
    },
    "invert_param": {
        "vid": 6790,
        "pid": 29987,
        "serial_params": {}
    },
    "xmpp_param": {
        "jid": "",
        "password": "",
        "send_to": ""
    }
}
"""


def until_timeout(start_at_time=time.time(), seconds=0):
    """Measure time and return whether elapsed time satisfies condition.
    Requires start_at_time - time in useconds; seconds - timeout"""
    return time.time() - start_at_time <= seconds


class Engine:
    def __init__(self, db_name, gps_param, invert_param, xmpp_param, **kwargs):
        self.queue_gps = mp.JoinableQueue()
        self.queue_inverter = mp.JoinableQueue()
        self.serial_pool = []
        self.gps = Device.GPS(**gps_param)
        self.inverter = Device.Inverter(**invert_param)
        self.db = db.ElvicDatabase(db_name)
        self.save_info = SavingSignal.SavingSignalConsole()
        self.xmpp = XMPPSender.MultiprocessingSender(**xmpp_param)

        try:                                    #every new start of the program starts a new recording instance into db
            self.db.insert_into_DataRecords()
        except sqlite3.OperationalError as e:
            print("Could not connect to the database:\n'{}'".format(e))
            return

        self._assign_serial_ports()

    def _assign_serial_ports(self):
        """Assigns serial ports in the following order:
        * Checks if port name was given. If true then it opens serial by name
        * Looks up for the matching vid and pid parameters and discovers the name
            of the serial port automatically."""
        if self.gps.get_port():
            self.serial_pool.append(es.SerialMultiprocessReceiver(self.queue_gps, self.gps.serial_params))
        elif self.inverter.get_port():
            self.serial_pool.append(es.SerialMultiprocessReceiver(self.queue_inverter, self.inverter.serial_params))
        else:
            for vid_pid, port_name in self.discover_devices((self.gps.vid_pid, self.inverter.vid_pid)):
                print(vid_pid, port_name)
                if self.gps.match_device_url(vid_pid) and not self.gps.get_port():
                    self.gps.serial_params["port"] = port_name
                    self.serial_pool.append(es.SerialMultiprocessReceiver(self.queue_gps, self.gps.serial_params))
                if self.inverter.match_device_url(vid_pid) and not self.inverter.get_port():
                    self.inverter.serial_params["port"] = port_name
                    self.serial_pool.append(es.SerialMultiprocessReceiver(self.queue_inverter, self.inverter.serial_params))

    def __del__(self):
        """Clean up"""
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
            for i in range(ACQUIRE_ITERATIONS):
                time.sleep(ACQUIRE_TIME_SECONDS)
                self.acquire_data()
                msg = self.create_xmpp_msg()
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
    SETTINGS_FILE = "settings.json"
    if os.path.isfile(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r') as file:
            settings = json.load(file)
        print("Settings loaded")
    else:
        with open(SETTINGS_FILE, 'w') as file:
            file.write(TEXT_DEFAULT_SETTINGS)
        settings = json.loads(TEXT_DEFAULT_SETTINGS)

    ACQUIRE_ITERATIONS = settings["ACQUIRE_ITERATIONS"]
    ACQUIRE_TIME_SECONDS = settings["ACQUIRE_TIME_SECONDS"]

    engine = Engine(**settings)
    try:
        engine.main()
    except KeyboardInterrupt:
        del engine
