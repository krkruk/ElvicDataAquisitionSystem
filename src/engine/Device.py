def decode(data, decode="utf-8"):
    if isinstance(data, bytes): return data.decode(decode)
    else: return data


class Device:
    def __init__(self, vid, pid, uart=""):
        self.vid = vid
        self.pid = pid
        self.uart = uart
        self.vid_pid = (vid, pid)
        self.data = []

    def match_device_url(self, url):
        return self.vid_pid == url

    def get_last_element(self):
        return decode(self.data[-1] if self.data else "")


class GPS(Device):
    """GPS Serial constants. These allow finding the best uart device
    and assign it to the proper queue and the database"""

    VTG = "$GPVTG"  #from:
    GGA = "$GPGGA"  #http://www.trimble.com/OEM_ReceiverHelp/V4.44/en/NMEA-0183messages_MessageOverview.html

    def __init__(self, vid, pid, uart=""):
        super(GPS, self).__init__(vid, pid, uart)

    def _get_last_nmea_sentence(self, nmea_sentence):
        for elem in reversed(self.data):
            decoded_elem = decode(elem)
            if nmea_sentence in decoded_elem:
                return decoded_elem
        else:
            return ""

    def get_last_GGA(self):
        return self._get_last_nmea_sentence(self.GGA)

    def get_last_VTG(self):
        return self._get_last_nmea_sentence(self.VTG)


class Inverter(Device):
    """Inverter Serial constants. These allow finding the best uart device
    and assign it to the proper queue and the database"""
    def __init__(self, vid, pid, uart=""):
        super(Inverter, self).__init__(vid, pid, uart)