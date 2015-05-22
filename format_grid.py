import numpy as np
from netCDF4 import Dataset as NC

grid = np.loadtxt("SH.xy")

N_lat = 256
N_lon = 512

longitude = grid[:, 0].reshape(N_lat, N_lon)
latitude = grid[:, 1].reshape(N_lat, N_lon)
lat = latitude[:,0]
lon = longitude[0,:]

delta_lat = lat[1] - lat[0]
delta_lon = lon[1] - lon[0]

output = NC("grid.nc", "w")

output.createDimension("lat", N_lat)
output.createDimension("lon", N_lon)
output.createDimension("nv", 4)
nc_lat = output.createVariable("lat", "f8", ("lat",))
nc_lat.units = "degree_north"
nc_lon = output.createVariable("lon", "f8", ("lon",))
nc_lon.units = "degree_east"

nc_latitude  = output.createVariable("latitude", "f8", ("lat", "lon"))
nc_latitude.units = "degree_north"
nc_latitude.bounds = "latitude_bnds"
nc_longitude = output.createVariable("longitude", "f8", ("lat", "lon"))
nc_longitude.units = "degree_east"
nc_longitude.bounds = "longitude_bnds"


def bogus_data():
    "Create bogus data to test interpolation."
    data = np.zeros((N_lat, N_lon))

    W = 8
    for Lat in xrange(N_lat):
        if np.mod(Lat, 2*W) < W:
            data[Lat,:] = 1

    for Lon in xrange(N_lon):
        if np.mod(Lon, 2*W) < W:
            data[:,Lon] += 1

    return data

nc_data = output.createVariable("data", "f8", ("lat", "lon"))
nc_data.coordinates = "latitude longitude"
nc_data[:] = bogus_data()

nc_lat_bounds = output.createVariable("latitude_bnds", "f8", ("lat", "lon", "nv"))
nc_lon_bounds = output.createVariable("longitude_bnds", "f8", ("lat", "lon", "nv"))

nc_lat[:] = lat
nc_lon[:] = lon

nc_latitude[:] = latitude
nc_longitude[:] = longitude

lat_bounds = np.zeros((N_lat, N_lon, 4))
lon_bounds = np.zeros((N_lat, N_lon, 4))

lat_bounds[:,:,0] = latitude - 0.5 * delta_lat
lat_bounds[:,:,1] = latitude + 0.5 * delta_lat
lat_bounds[:,:,2] = latitude + 0.5 * delta_lat
lat_bounds[:,:,3] = latitude - 0.5 * delta_lat

lon_bounds[:,:,0] = longitude - 0.5 * delta_lon
lon_bounds[:,:,1] = longitude - 0.5 * delta_lon
lon_bounds[:,:,2] = longitude + 0.5 * delta_lon
lon_bounds[:,:,3] = longitude + 0.5 * delta_lon

for i in xrange(lon_bounds.size):
    if lon_bounds.flat[i] < 0:
        lon_bounds.flat[i] += 360.0

lat_min = np.min(lat)
lat_max = np.max(lat)
for i in xrange(lat_bounds.size):
    if lat_bounds.flat[i] < lat_min:
        lat_bounds.flat[i] = -90.0
    if lat_bounds.flat[i] > lat_max:
        lat_bounds.flat[i] = 90.0

nc_lat_bounds[:] = lat_bounds
nc_lon_bounds[:] = lon_bounds

output.close()

