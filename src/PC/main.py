from engine import CoordinateAnimation
from engine import DataReceiver
import multiprocessing as mp
import numpy as np


class PlotGPS:
    def __init__(self):
        self.zoom = 16
        self.scatter_params = {"c": "magenta", "edgecolors": "k", "marker": '*', "s": 1500, "alpha": 0.9}
        self.london_aquatics_centre_corners = (
            -0.0184,  # lower left corner longitude
            51.5378,  # lower left corner latitude
            -0.0074,  # upper right corner longitude
            51.5437,  # upper right corner latitude
        )
        # self.send, self.recv = mp.Pipe()
        # self.anim = CoordinateAnimation.CoordinateAnimation(self.london_aquatics_centre_corners,
        #                                                     self.zoom,
        #                                                     self.send,
        #                                                     scatter_params=self.scatter_params)
        # self.xmpp = DataReceiver.XmppDataReceiver("elvic02@jappix.com", "elvic", self.recv)

    def plot(self):
        self.xmpp.start()
        self.anim.plot()


if __name__ == "__main__":
    gps = PlotGPS()
    gps.plot()