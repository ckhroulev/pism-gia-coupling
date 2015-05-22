#!/bin/bash

# Turn an ASCII file into a NetCDF file with metadata and grid information.
./ascii_to_nc.py topo55.xyz topography.nc

# Make sure that all variables in the file defining the PISM grid have
# the same storage order.
ncpdq -O -a y,x pism_antarctica.nc pism_antarctica.nc

# Try bilinear interpolation.
cdo remapbil,pism_antarctica.nc topography.nc topography-bilinear.nc

# Try conservative interpolation.
cdo remapcon,pism_antarctica.nc topography.nc topography-conservative.nc

# Look at results.
ncview topography-bilinear.nc &
ncview topography-conservative.nc &
ncview pism_antarctica.nc
