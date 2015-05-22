#!/usr/bin/env python

from argparse import ArgumentParser
import numpy as np
from netCDF4 import Dataset as NC

def bogus_data(n_lon, n_lat):
    "Create bogus data to test interpolation."
    data = np.zeros((n_lat, n_lon))

    W = 32
    for Lat in xrange(n_lat):
        if np.mod(Lat, 2*W) < W:
            data[Lat,:] = 1

    for Lon in xrange(n_lon):
        if np.mod(Lon, 2*W) < W:
            data[:,Lon] += 1

    return data

def lat_1d(latitude):
    "Extract 1D latitudes from a 2D array."
    return latitude[:,0]

def lon_1d(longitude):
    "Extract 1D longitude from a 2D array."
    return longitude[0,:]

def read_data(filename, n_lon, n_lat):
    "Read coordinates and topography from an ASCII file."
    data = np.loadtxt(filename)
    longitude = data[:, 0].reshape(n_lat, n_lon)
    latitude = data[:, 1].reshape(n_lat, n_lon)
    try:
        topography = data[:, 2].reshape(n_lat, n_lon)
    except:
        # for testing with SH.xy
        topography = bogus_data(n_lon, n_lat)

    return longitude, latitude, topography

def write_data(filename,
               n_lon, longitude, longitude_bounds,
               n_lat, latitude, latitude_bounds,
               topography):
    "Write grid intormation and topography to a file."
    output = NC(filename, "w")

    # dimensions
    output.createDimension("lat", n_lat)
    output.createDimension("lon", n_lon)
    output.createDimension("nv", 4)

    # variables
    nc_lon = output.createVariable("lon", "f8", ("lon",))
    nc_lon.units = "degree_east"
    nc_longitude = output.createVariable("longitude", "f8", ("lat", "lon"))
    nc_longitude.units = "degree_east"
    nc_longitude.bounds = "longitude_bnds"
    nc_lon_bounds = output.createVariable("longitude_bnds", "f8", ("lat", "lon", "nv"))

    nc_lat = output.createVariable("lat", "f8", ("lat",))
    nc_lat.units = "degree_north"
    nc_latitude  = output.createVariable("latitude", "f8", ("lat", "lon"))
    nc_latitude.units = "degree_north"
    nc_latitude.bounds = "latitude_bnds"
    nc_lat_bounds = output.createVariable("latitude_bnds", "f8", ("lat", "lon", "nv"))

    nc_data = output.createVariable("topg", "f8", ("lat", "lon"))
    nc_data.units = "meters"
    nc_data.standard_name = "bedrock_altitude"
    nc_data.coordinates = "latitude longitude"

    nc_lon[:] = lon_1d(longitude)
    nc_lat[:] = lat_1d(latitude)
    nc_longitude[:] = longitude
    nc_latitude[:] = latitude
    nc_lon_bounds[:] = longitude_bounds
    nc_lat_bounds[:] = latitude_bounds
    nc_data[:] = topography

    output.close()

def compute_bounds(longitude, latitude, n_lon, n_lat):
    "Compute longitude and latitude bounds."
    lat = lat_1d(latitude)
    lon = lon_1d(longitude)
    delta_lat = lat[1] - lat[0]
    delta_lon = lon[1] - lon[0]
    lat_min = np.min(lat)
    lat_max = np.max(lat)

    lat_bounds = np.zeros((n_lat, n_lon, 4))
    lon_bounds = np.zeros((n_lat, n_lon, 4))

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

    return lon_bounds, lat_bounds

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.description = "Converts an ASCII file produced by a GIA model to a NetCDF file that can be used with CDO"
    parser.add_argument("INPUT", nargs=1)
    parser.add_argument("OUTPUT", nargs=1)
    parser.add_argument("--n_lat", default=256, dest="n_lat")
    parser.add_argument("--n_lon", default=512, dest="n_lon")

    options = parser.parse_args()

    lon, lat, data = read_data(options.INPUT[0], options.n_lon, options.n_lat)

    lon_bounds, lat_bounds = compute_bounds(lon, lat, options.n_lon, options.n_lat)

    write_data(options.OUTPUT[0],
               options.n_lon, lon, lon_bounds,
               options.n_lat, lat, lat_bounds,
               data)
