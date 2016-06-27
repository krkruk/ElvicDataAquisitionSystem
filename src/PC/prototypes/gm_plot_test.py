import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap

import logging
logging.basicConfig(level=logging.DEBUG)

import geotiler

bbox = -0.0044, 51.5386, -0.0267, 51.5391

fig = plt.figure(figsize=(10, 10))
ax = plt.subplot(111)

#
# download background map using OpenStreetMap
#
mm = geotiler.Map(extent=bbox, zoom=18)

img = geotiler.render_map(mm)

#
# create basemap
#
map = Basemap(
    llcrnrlon=bbox[0], llcrnrlat=bbox[1],
    urcrnrlon=bbox[2], urcrnrlat=bbox[3],
    projection='merc', ax=ax
)

map.imshow(img, interpolation='lanczos', origin='upper')

#
# plot custom points
#
x0, y0 = -0.0044, 51.5386 # http://www.openstreetmap.org/search?query=46.48114%2C11.78816
x1, y1 = -0.0267, 51.5391 # http://www.openstreetmap.org/search?query=46.48165%2C11.78771
x, y = map((x0, x1), (y0, y1))
ax.scatter(x, y, c='red', edgecolor='none', s=10, alpha=0.9)

# plt.savefig('ex-basemap.pdf', bbox_inches='tight')
plt.show()
plt.close()