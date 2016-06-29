import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np


class Anim:
    def __init__(self):
        self.x = np.random.random((1, 1))
        self.y = np.random.random((1, 1))

        self.fig = plt.figure()
        self.ax = plt.subplot(111)

        self.animation = animation.FuncAnimation(self.fig, self._update_plot,
                                                 init_func=self._init_plot)

    def _init_plot(self):
        self.plot_plot = plt.plot(self.x, self.y)
        self.plot_scatter = plt.scatter(self.x, self.y)

    def _update_plot(self, i):
        plt.clf()
        x = np.random.random((1, 1))
        y = np.random.random((1, 1))
        self.x = np.vstack((x, self.x))
        self.y = np.vstack((y, self.y))
        self.plot_plot = plt.plot(self.x, self.y)
        self.plot_scatter = plt.scatter(self.x, self.y)
        return self.plot_plot,

    def anim(self):
        plt.scatter(self.x, self.y)
        plt.plot(self.x, self.y)
        plt.show()

if __name__ == "__main__":
    anim = Anim()
    anim.anim()