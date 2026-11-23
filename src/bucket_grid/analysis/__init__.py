# -*- coding: utf-8 -*-
"""

"""

__author__ = "Stefan Hendricks <stefan.hendricks@awi.de>"
__all__ = ["GridAnalysis", "GridAnalysisMethod", "GridAnalysisData", "IndicesTarget"]

from typing import List, Type, Union

from bucket_grid.buckets import BucketGrid
from bucket_grid.analysis._data import GridAnalysisData
from bucket_grid.analysis._abc import GridAnalysisMethod, IndicesTarget
from bucket_grid.analysis.statistics import NumPoints


DEFAULT_METHOD_DICT = {
    "num_points": NumPoints,
}


class GridAnalysisMethodQueue(object):

    def __init__(
        self,
        analysis_methods: List[Union[str, Type]]
    ) -> None:

        # Initialize the queue of analysis methods. Each method can be specified either by its
        # class or by a string name that maps to a default method.
        self.queue = [
            method if not isinstance(method, str)
            else self._get_method_by_name(method)
            for method in analysis_methods
        ]

    def _get_method_by_name(self, name: str) -> Type:
        if name in DEFAULT_METHOD_DICT:
            return DEFAULT_METHOD_DICT[name]()
        raise NotImplementedError(f"Method retrieval by name not implemented: {name}")



class GridAnalysis(object):
    """
    Class for analyzing gridded data.
    """

    def __init__(
            self,
            buckets: BucketGrid,
            analysis_methods: GridAnalysisMethodQueue
    ) -> None:
        self.data = GridAnalysisData(buckets)
        self.analysis_methods = analysis_methods
        self.apply_all()

    def apply_all(self) -> None:
        """
        Apply the analysis methods to the gridded data.

        :return: None, results are stored in self.data.ds.
        """

        # Methods may select different grid indices to analyze, e.g., all grid cells or only non-empty ones.
        grid_indices_selection = {
            "all": self.data.get_indices("all"),
            "non_empty": self.data.get_indices("non_empty"),
        }
        # Loop over all analysis methods in the queue and update the analysis dataset
        # after each turn (so that the next method can use the results of the previous one).
        for method in self.analysis_methods.queue:
            grid_indices = grid_indices_selection.get(method.grid_indices_target, grid_indices_selection["all"])
            ds = method.apply(self.data.buckets, grid_indices, callback=self.data)
            self.data.update(ds)

    def to_netcdf(self, *args, **kwargs):
        return self.data.ds.to_netcdf(*args, **kwargs)