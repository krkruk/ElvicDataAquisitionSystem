import geotiler
from mpl_toolkits.basemap import Basemap
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np
import pynmea2


class CoordinateAnimation:
    def __init__(self, corners, zoom, data_pipe, figsize=(16, 9), scatter_params={}):
        self.corners = corners
        self.zoom = zoom
        self.scatter_params = scatter_params
        self.data_pipe = data_pipe
        self.plot_data = np.zeros(shape=(1, 2))
        self.fig, self.ax = plt.figure(figsize=figsize), plt.subplot(111)
        self._init_basemap()
        self.anim_scatter = animation.FuncAnimation(self.fig, self._update_scatter,
                                                    init_func=self._scatter_init)
        self.plot_scat = None
        self.plot_plot = None

    def _init_basemap(self):
        self.m = geotiler.Map(extent=self.corners, zoom=self.zoom)
        self.img = geotiler.render_map(self.m)
        self.bmap = Basemap(
            llcrnrlon=self.corners[0], llcrnrlat=self.corners[1],
            urcrnrlon=self.corners[2], urcrnrlat=self.corners[3],
            projection="merc", ax=self.ax
        )

        self.bmap.imshow(self.img, interpolation='lanczos', origin='upper')

    def _scatter_init(self):
        self.plot_scat = plt.scatter(self.plot_data[:, 0], self.plot_data[:, 1],
                                     **self.scatter_params)

        self.plot_plot = plt.plot(self.plot_data[:, 0], self.plot_data[:, 1])

    def _update_scatter(self, i):
        try:
            if not self.data_pipe.poll(3):
                return self.plot_scat,
        except KeyboardInterrupt:
            return self.plot_scat,
        try:
            gps_json = self.data_pipe.recv()
        except KeyboardInterrupt:
            return self.plot_scat,

        gga = gps_json['gga']
        try:
            parsed = pynmea2.parse(gga)
        except pynmea2.nmea.ChecksumError:
            return self.plot_scat,

        array = np.array(self.bmap(parsed.longitude, parsed.latitude))
        self.plot_data = np.vstack( (self.plot_data, array) )
        self.plot_scat.set_offsets(array)
        plt.plot(self.plot_data[1:, 0], self.plot_data[1:, 1])
        return self.plot_scat,

    def plot(self):
        plt.show()


if __name__ == "__main__":
    import multiprocessing as mp
    zoom = 16
    scatter_params = {"c": "magenta", "edgecolors": "k", "marker": '*', "s": 1500, "alpha": 0.9}
    london_aquatics_centre_corners = (
        -0.0184,  # lower left corner longitude
        51.5378,  # lower left corner latitude
        -0.0074,  # upper right corner longitude
        51.5437,  # upper right corner latitude
    )
    a, b = mp.Pipe()
    anim = CoordinateAnimation(london_aquatics_centre_corners, zoom, a, scatter_params=scatter_params)
    anim.plot()