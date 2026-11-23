# -*- coding: utf-8 -*-
"""

"""

__author__ = "Stefan Hendricks <stefan.hendricks@awi.de>"

from typing import List, Type, Dict, Any, Optional, Union

import xarray as xr
from scipy.sparse import coo

from bucket_grid.buckets import BucketGrid


class GridAnalysisData(object):

    def __init__(self, buckets: BucketGrid) -> None:
        self.buckets = buckets
        self.grid_data = buckets.grid_definition.get_data()
        self.nc_coords = self.grid_data.get_nc_coords()
        self.ds = self._get_analysis_dataset()

    def _get_analysis_dataset(self) -> xr.Dataset:
        """
        Initialize the xarray.Dataset for analysis results.

        :return: Initialized xarray.Dataset.
        """
        self.grid_data.get_lonlat_nc_vars()
        return xr.Dataset(
            attrs=self._get_default_attrs(),
            coords=self.get_data_array_coords()["coords"],
            data_vars=self.grid_data.get_lonlat_nc_vars()
        )

    def _get_default_attrs(self) -> Dict[str, Any]:
        """
        Get default attributes for the xarray.Dataset.

        :return: Dictionary of default attributes.
        """
        return {
            "title": "Gridded Data Analysis",
            "institution": "Alfred Wegener Institute, Helmholtz Centre for Polar and Marine Research",
            "source": "Gridded data analysis using BucketGrid",
            "history": "",
            "references": "",
            "comment": "",
        }

    def update(self, new_data_arrays: Dict[str, xr.DataArray]) -> None:
        """
        Update the analysis dataset with new data arrays.

        :param new_data_arrays: Dictionary of new data arrays to be added to the dataset.
        :return: None, updates self.ds in place.
        """
        for name, data_array in new_data_arrays.items():
            # new_coords = list(set(data_array.coords.variables) - set(self.ds.coords.variables))
            # # Manually set coords to ensure coords attributes are copied over
            # if new_coords:
            #     for coord_name in new_coords:
            #         self.ds = self.ds.assign_coords(**{coord_name: data_array.coords[coord_name]})
            self.ds[name] = data_array


    def get_indices(self, target: str) -> List[tuple]:
        if target == "all":
            return self.buckets.get_all_indices()
        elif target == "non_empty":
            return self.buckets.get_non_empty_indices()
        else:
            raise ValueError(f"Unknown target: {target}")

    def get_data_array_coords(
            self,
            additional_coords: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Dict[str, Any]]:
        coords = dict(coords=self.nc_coords.copy())
        if additional_coords:
            coords["coords"].update(additional_coords)
        return coords