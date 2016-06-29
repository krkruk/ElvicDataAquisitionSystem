import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np


class Anim:
    def __init__(self):
        self.rows = 2
        self.col = 2
        self.x, self.y = np.random.random( (self.col, self.rows) )
        self.fig = plt.figure(figsize=(16,9))

        self.anim = animation.FuncAnimation(self.fig, self._update_plot,
                                            init_func=self._plot_init)

        self.scat = None

    def _plot_init(self):
        self.scat = plt.scatter(self.x, self.y)

    def _update_plot(self, i):
        self.scat.set_offsets(np.random.random((2, 1)))
        return self.scat,

    def plot(self):
        # self._plot_init()
        plt.show()


if __name__ == "__main__":
    anim = Anim()
    anim.plot()