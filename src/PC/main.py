from engine import CoordinateAnimation
from engine import DataReceiver
from engine import EchoMiscellaneous
import multiprocessing as mp
import matplotlib.pyplot as plt
import json


class DataSplitter(mp.Process):
    def __init__(self, input_pipe, power_inverter_pipe, gps_pipe):
        super(DataSplitter, self).__init__()
        self.input_pipe = input_pipe
        self.power_inverter_pipe = power_inverter_pipe
        self.gps_pipe = gps_pipe
        self.daemon = True

    def run(self):
        while True:
            try:
                self._main()
            except KeyboardInterrupt:
                break

    def _main(self):
        try:
            data = self.input_pipe.recv()
        except EOFError:
            return

        json_data = json.loads(data)
        inverter = json_data["inv"]
        gps = json_data["gps"]
        self.power_inverter_pipe.send(inverter)
        self.gps_pipe.send(gps)


class PlotGPS:
    def __init__(self):
        self.zoom = 17
        self.scatter_params = {"c": "magenta", "edgecolors": "k", "marker": '*', "s": 1500, "alpha": 0.9}
        self.london_aquatics_centre_corners = (
            -0.01377,  # lower left corner longitude
            51.53489,  # lower left corner latitude
            -0.00813,  # upper right corner longitude
            51.53727,  # upper right corner latitude
        )
        self.xmpp_to_splitter, self.xmpp_recv_msg = mp.Pipe()
        self.plot_to_splitter, self.plot_to_plot_class = mp.Pipe()
        self.telemetry_to_splitter, self.telemetry_to_process = mp.Pipe()

        self.data_splitter = DataSplitter(self.xmpp_to_splitter, self.telemetry_to_splitter, self.plot_to_splitter)

        self.anim = CoordinateAnimation.CoordinateAnimation(self.london_aquatics_centre_corners,
                                                            self.zoom,
                                                            self.plot_to_plot_class,
                                                            scatter_params=self.scatter_params)
        self.xmpp = DataReceiver.XmppDataReceiver("elvic02@jappix.com", "elvic", self.xmpp_recv_msg)
        self.echo = EchoMiscellaneous.EchoMiscellaneous(self.telemetry_to_process)

    def plot(self):
        self.data_splitter.start()
        self.echo.start()
        self.xmpp.start()
        self.anim.plot()
        plt.show()


if __name__ == "__main__":
    import time
    gps = PlotGPS()
    gps.plot()

