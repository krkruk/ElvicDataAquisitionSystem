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
        self.x, self.y = np.random.random((2, 2))  # params just for sake of init
        self.fig, self.ax = plt.figure(figsize=figsize), plt.subplot(111)
        self._init_basemap()
        self.anim = animation.FuncAnimation(self.fig, self._update_plot,
                                            init_func=self._plot_init)

        self.scat = None
        self.test_points = np.array([[-0.0097, 51.5407],
                       [-0.0120, 51.5417],
                       [-0.0158, 51.5407]])

    def _init_basemap(self):
        self.m = geotiler.Map(extent=self.corners, zoom=self.zoom)
        self.img = geotiler.render_map(self.m)
        self.bmap = Basemap(
            llcrnrlon=self.corners[0], llcrnrlat=self.corners[1],
            urcrnrlon=self.corners[2], urcrnrlat=self.corners[3],
            projection="merc", ax=self.ax
        )

        self.bmap.imshow(self.img, interpolation='lanczos', origin='upper')

    def _plot_init(self):
        self.scat = plt.scatter(self.x, self.y,
                                **self.scatter_params)

    def _update_plot(self, i):
        # x, y = self.bmap(self.test_points[:, 0], self.test_points[:, 1])
        # array = np.array([elem for elem in zip(x, y)])
        try:
            if not self.data_pipe.poll(3):
                return self.scat,
        except KeyboardInterrupt:
            return self.scat,
        try:
            gps_json = self.data_pipe.recv()
        except KeyboardInterrupt:
            return self.scat,

        gga = gps_json['gga']
        parsed = pynmea2.parse(gga)
        array = np.array(self.bmap(parsed.longitude, parsed.latitude))
        print(parsed.longitude, parsed.latitude)
        print(array)
        self.scat.set_offsets(array)
        return self.scat,

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