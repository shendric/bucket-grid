# -*- coding: utf-8 -*-
"""

"""

__all__ = ["IndicesTarget", "GridAnalysisMethod"]

from enum import StrEnum
from abc import ABC, abstractmethod
from typing import Tuple, List, Type, Dict, ClassVar

import xarray as xr

from bucket_grid import BucketGrid

from bucket_grid.analysis._data import GridAnalysisData


class IndicesTarget(StrEnum):
    ALL = "all"
    NON_EMPTY = "non_empty"


class GridAnalysisMethod(ABC):
    """
    Abstract base class for analysis classes.
    """
    grid_indices_target: ClassVar[IndicesTarget]

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if not hasattr(cls, "grid_indices_target"):
            raise TypeError(f"{cls.__name__} must define 'grid_indices_target'")

    @abstractmethod
    def init_return_data(
        self,
        shape: Tuple[int, int],
        callback: GridAnalysisData
    ) -> Dict[str, xr.DataArray]:
        """
        Abstract method to initialize the xarray.Dataset for analysis results.

        :return: Initialized xarray.Dataset.
        """
        ...

    def apply(
            self,
            buckets: BucketGrid,
            indices: List[Tuple[int, int]],
            callback: GridAnalysisData
    ) -> Dict[str, xr.DataArray]:
        """
        Apply the methods for all selected grid indices and store the results in the xarray.Dataset.

        :param buckets: The BucketGrid instance containing the gridded data.
        :param indices: The indices to be processed, e.g., all grid cells or only non-empty ones.
            (defined by the analysis method)
        :param callback: Optional callback that can be used to get additional information.

        :return: A list of data ararys containing the analysis results.
        """
        # The data arrays can only be initialized once the data shape is known
        da_dict = self.init_return_data(buckets.shape, callback)
        for index in indices:
            points = buckets.get(*index)
            self.apply_method(points, *index, da_dict, callback)
        return da_dict

    @abstractmethod
    def apply_method(
            self,
            points: List[Type],
            yj: int,
            ix: int,
            da_dict: Dict[str, xr.DataArray],
            callback: "GridAnalysisData"
    ) -> None:
        """
        Abstract method to apply the analysis method to a single grid cell.

        :param points: List of data points in the grid cell.
        :param yj: Y index of the grid cell.
        :param ix: X index of the grid cell.
        :param da_dict: Dictionary of xarray.DataArray to store the analysis results.
        :param callback: Optional callback that can be used to get additional information.

        :return: xarray.Dataset containing the analysis results.
        """
        ...
