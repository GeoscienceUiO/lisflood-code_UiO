"""

Copyright 2019 European Union

Licensed under the EUPL, Version 1.2 or as soon they will be approved by the European Commission  subsequent versions of the EUPL (the "Licence");

You may not use this work except in compliance with the Licence.
You may obtain a copy of the Licence at:

https://joinup.ec.europa.eu/sites/default/files/inline-files/EUPL%20v1_2%20EN(1).txt

Unless required by applicable law or agreed to in writing, software distributed under the Licence is distributed on an "AS IS" basis,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the Licence for the specific language governing permissions and limitations under the Licence.

"""
from __future__ import print_function, absolute_import

from ..global_modules.settings import LisSettings
from ..global_modules.add1 import readmapsparse
from ..global_modules.netcdf import xarray_reader


class readmeteo(object):

    """
     # ************************************************************
     # ***** READ METEOROLOGICAL DATA              ****************
     # ************************************************************
    """

    def __init__(self, readmeteo_variable):
        self.var = readmeteo_variable
        settings = LisSettings.instance()
        option = settings.options
        # initialise xarray readers
        if option['readNetcdfStack']:
            self.forcings = {}
            for data in ['PrecipitationMaps', 'TavgMaps', 'ET0Maps', 'E0Maps']:
                self.forcings[data] = xarray_reader(data)

# --------------------------------------------------------------------------
# --------------------------------------------------------------------------
    def dynamic(self):
        """ dynamic part of the readmeteo module
            read meteo input maps
        """
        settings = LisSettings.instance()
        option = settings.options
        binding = settings.binding

        # ************************************************************
        # ***** READ METEOROLOGICAL DATA *****************************
        # ************************************************************
        if option['readNetcdfStack']:

            step = self.var.currentTimeStep() - self.var.firstTimeStep()
            # date = date_from_step(binding, self.var.currentTimeStep())

            # Read from NetCDF stack files
            self.var.Precipitation = self.forcings['PrecipitationMaps'][step] * self.var.DtDay * self.var.PrScaling
            self.var.Tavg = self.forcings['TavgMaps'][step]
            self.var.ETRef = self.forcings['ET0Maps'][step] * self.var.DtDay * self.var.CalEvaporation
            self.var.EWRef =self.forcings['E0Maps'][step] * self.var.DtDay * self.var.CalEvaporation

        else:
            # Read from stack of maps in Pcraster format
            self.var.Precipitation = readmapsparse(binding['PrecipitationMaps'], self.var.currentTimeStep(), self.var.Precipitation) * self.var.DtDay * self.var.PrScaling
            # precipitation (conversion to [mm] per time step)
            self.var.Tavg = readmapsparse(binding['TavgMaps'], self.var.currentTimeStep(), self.var.Tavg)
            # average DAILY temperature (even if you are running the model on say an hourly time step) [degrees C]
            self.var.ETRef = readmapsparse(binding['ET0Maps'], self.var.currentTimeStep(), self.var.ETRef) * self.var.DtDay * self.var.CalEvaporation
            # daily reference evapotranspiration (conversion to [mm] per time step)
            # potential evaporation rate from a bare soil surface (conversion to [mm] per time step)
            self.var.EWRef = readmapsparse(binding['E0Maps'], self.var.currentTimeStep(), self.var.EWRef) * self.var.DtDay * self.var.CalEvaporation
            # potential evaporation rate from water surface (conversion to [mm] per time step)

        self.var.ESRef = (self.var.EWRef + self.var.ETRef)/2

        if option['TemperatureInKelvin']:
            self.var.Tavg -= 273.15
