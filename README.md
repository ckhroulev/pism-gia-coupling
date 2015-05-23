### Coupling PISM to a GIA model

#### Data transfer: PISM to GIA

We can track changes in the load used by the GIA model using modeled
ice thickness reported by PISM at predefined intervals.

PISM reports ice thickness on an uniform cartesian grid, typically
using the polar stereographic projection, so we need to transfer this
thickness to the a longitude,latitude grid used by GIA.

We need to ensure that the total ice volume is conserved during when
ice thickness is transferred from the PISM grid to the GIA grid, so we
use conservative remapping (see CDO documentation for a reference).

##### Defining grids

To make sure that a PISM output file contains metadata defining the
grid in the form recognized by CDO, run

    nc2cdo.py pism_output.nc

Ths `nc2cdo.py` script is installed with PISM. (It requires Python
modules `numpy`, `pyproj`, and `netCDF`.)

To create a netCDF file defining an GIA grid, run

    ascii_to_nc.py gia_grid.xy gia_grid.nc

Both `nc2cdo.py` and `ascii_to_nc.py` compute latitude and longitude
bounds (see below).

##### Pre-computing interpolation weights

Computing weights is the most computationally expensive part of the
interpolation process, but luckily we only need to do it once for each
pair of grids and each interpolation direction.

CDO supports pre-computing weights using the `genbil` operator for
bilinear interpolation and `gencon` for first order conservative
interpolation.

To compute bilinear interpolation weights CDO needs a grid
description. Conservative remapping methods also require latitude and
longitude bounds.

We use bilinear interpolation to transfer data from the GIA grid to
the PISM grid. To compute corresponding weights, run

    cdo genbil,pism_output.nc gia_grid.nc gia_to_pism_weights.nc

Here `pism_output.nc` is a PISM output file processed using
`nc2cdo.py` and `gia_grid.nc` is a NetCDF file produced by
`ascii_to_nc.py`.

We use first-order conservative remapping to transfer data from the
PISM grid to the GIA grid. To compute corresponding weights, run

    cdo gencon,gia_grid.nc pism_output.nc pism_to_gia_weights.nc

##### Interpolating ice thickness

Assume that `pism_output.nc` contains the PISM model state, running
the following

```
 # extract ice thickness
 cdo selvar,thk pism_output.nc ice_thickness.nc
 # put it onto the GIA grid using pre-computed weights
 cdo remap,gia_grid.nc,pism_to_gia_weights.nc ice_thickness.nc ice_thickness_latlon.nc
 # replace missing values with zeros
 cdo setmisstoc,0 ice_thickness_latlon.nc ice_thickness_latlon_filled.nc
```

#### Data transfer: GIA to PISM

FIXME
