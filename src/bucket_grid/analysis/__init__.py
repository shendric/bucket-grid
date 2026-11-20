# -*- coding: utf-8 -*-
"""

"""

__author__ = "Stefan Hendricks <stefan.hendricks@awi.de>"
__all__ = ["GridAnalysis"]

import xarray as xr

from bucket_grid.buckets import BucketGrid


class GridAnalysis(object):
    """
    Class for analyzing gridded data.
    """

    def __init__(self, buckets: BucketGrid, analysis_definition) -> None:
        self.buckets = buckets
        self.analysis_definition = analysis_definition
        self.ds = self._get_analysis_dataset()

    def _get_analysis_dataset(self) -> xr.Dataset:
        pass

    def to_netcdf(self, *args, **kwargs):
        return self.ds.to_netcdf(*args, **kwargs)