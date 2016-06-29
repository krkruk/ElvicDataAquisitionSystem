import geotiler
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import matplotlib.animation as animation
import numpy as np

#lon, lat
london_aquatics_centre = (-.0105, 51.5404)
london_aquatics_centre_corners = (
                                  -0.0184,        #lower left corner longitude
                                  51.5378,        #lower left corner latitude
                                  -0.0074,        #upper right corner longitude
                                  51.5437,        #upper right corner latitude
                                  )
zoom = 16
figure = plt.figure(figsize=(16, 9))
ax = plt.subplot(111)
m = geotiler.Map(extent=london_aquatics_centre_corners, zoom=zoom)
img = geotiler.render_map(m)


bmap = Basemap(
    llcrnrlon=london_aquatics_centre_corners[0], llcrnrlat=london_aquatics_centre_corners[1],
    urcrnrlon=london_aquatics_centre_corners[2], urcrnrlat=london_aquatics_centre_corners[3],
    projection="merc", ax=ax
)

bmap.imshow(img, interpolation='lanczos', origin='upper')
# x, y = bmap(london_aquatics_centre[0], london_aquatics_centre[1])

aa = np.array( [[-0.0097, 51.5407],
               [-0.0120, 51.5417],
               [-0.0158, 51.5407],
               [-0.01112, 51.5366]])
# x, y = bmap( (
#                 -0.0097,
#                 -0.0120,
#                 -0.0158
#               ),
#              (
#                 51.5407,
#                 51.5417,
#                 51.5407
#              )
# )
x, y = bmap(aa[:,0],aa[:,1])
scat = plt.scatter(x=x,
            y=y,
            c="magenta",
            edgecolors="k",
            marker='*',
            s=1500,
            alpha=0.9)

plt.show()
