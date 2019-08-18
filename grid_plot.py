from shapely.geometry.polygon import Polygon
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import cartopy.io.img_tiles as cimgt
from shapely.geometry.polygon import LinearRing

import maidenhead as mh

def GridToPoly(grid):
    lat,lon = mh.toLoc(grid)
    lats = [lat, lat+1, lat+1, lat, lat]
    lons = [lon, lon, lon+2, lon+2, lon]
    ring = LinearRing(list(zip(lons, lats)))
    return ring 

fig = plt.figure()
ax = fig.add_axes([0, 0, 1, 1])
ax = plt.axes(projection=ccrs.PlateCarree())

ax.add_feature(cfeature.LAND)
ax.add_feature(cfeature.OCEAN)
ax.add_feature(cfeature.COASTLINE)
ax.add_feature(cfeature.BORDERS)
ax.outline_patch.set_visible(False)

with open('seen_grids.txt') as f:
    lines = f.readlines()
    for line in lines:
        poly = GridToPoly(line)
        ax.add_geometries([poly], ccrs.PlateCarree(), facecolor='r', edgecolor='red', alpha=0.6)

plt.show()

