# -*- coding: utf-8 -*-
"""

"""

__author__ = "Stefan Hendricks <stefan.hendricks@awi.de>"
__all__ = ["BucketGrid"]

from easi_grid import Grid


class BucketGrid(object):
    """
    Class for gridding data into buckets.
    """

    def __init__(self, grid_definition: Grid) -> None:
        self.grid_definition = grid_definition
        self.buckets = self._create_buckets()

    def _create_buckets(self):
        """
        Create buckets based on the grid definition.
        """
        # Implementation to create buckets based on the grid definition
        pass

    @classmethod
    def from_easi_grid_preset(cls, preset_name: str):
        """
        Create a BucketGrid instance from a predefined EASI grid preset.
        """
        grid_definition = Grid.from_preset(preset_name)
        return cls(grid_definition)