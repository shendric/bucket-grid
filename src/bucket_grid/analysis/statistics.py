# -*- coding: utf-8 -*-
"""

"""

__author__ = "Stefan Hendricks <stefan.hendricks@awi.de>"

from typing import Dict, List, Tuple, Type

import numpy as np
import xarray as xr

from bucket_grid.analysis import GridAnalysisMethod, IndicesTarget, GridAnalysisData


class NumPoints(GridAnalysisMethod):
    """
    A simple gridding method that counts the number of points in each grid cell.
    """

    grid_indices_target = IndicesTarget.NON_EMPTY

    def __init__(self) -> None:
        ...

    def init_return_data(self, shape: Tuple[int, int], callback: GridAnalysisData) -> Dict[str, xr.DataArray]:
        """
        Initialize the xarray.Dataarrays for analysis results.

        :return: Initialized xarray.Dataarrays.
        """
        # Define the dataset structure here
        data_array_default = callback.get_data_array_coords()
        return {
            "num_points": xr.DataArray(
                np.full(shape, 0, dtype=np.uint32),
                dims=["yc", "xc"],
                name="num_points",
                attrs={
                    "long_name": "Number of Points",
                    "valid_min": np.uint32(0.0),
                    "comments": "Number of data points in the grid cell"
                },
                **data_array_default
            )
        }

    def apply_method(
            self,
            points: List[Type],
            yj: int,
            ix: int,
            da_dict: Dict[str, xr.DataArray],
            callback: "GridAnalysisData"
    ) -> None:
        """
        Count the number of points in the grid cell

        :param points:
        :param yj:
        :param ix:
        :param da_dict:
        :param callback:

        :return: None, updates dataarray dictionary in place.
        """
        da_dict["num_points"].values[yj, ix] = float(len(points))
