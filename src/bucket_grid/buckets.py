# -*- coding: utf-8 -*-
"""

"""

__author__ = "Stefan Hendricks <stefan.hendricks@awi.de>"
__all__ = ["BucketGrid", "bucket_data_factory"]

from dataclasses import make_dataclass, Field
from enum import StrEnum
from typing import List, Union, Tuple, Any, Type, Iterable

import easi_grid
from easi_grid import Grid





class OutOfBoundsBehavior(StrEnum):
    IGNORE = "ignore"
    ERROR = "error"


def bucket_data_factory(item_definitions: MAKE_DATACLASS_FIELDS) -> Type:
    """
    Create a dataclass object for bucket data based on the provided item definitions
    using the dataclasses.make_dataclass factory function.

    The item definition can be quite flexible, but specifying the data type is recommended for better type
    checking and validation.

    :param item_definitions: A list of field definitions for the dataclass.
        see https://docs.python.org/3/library/dataclasses.html#dataclasses.make_dataclass for details.

    :raises AssertionError: `latitude` and `longitude` fields not present in the item definitions.

    :return: A dataclass type that can be used to create instances of bucket data.
    """

    assert item_definitions is not None, "item_definitions must not be None."
    assert any(field[0] == "latitude" or field == "latitude" for field in item_definitions), \
        "item_definitions must include a 'latitude' field."
    assert any(field[0] == "longitude" or field == "longitude" for field in item_definitions), \
        "item_definitions must include a 'longitude' field."
    return make_dataclass(
        "BucketData",
        item_definitions,
        slots=True,
    )


class BucketGrid(object):
    """
    Class for gridding data into buckets.
    """

    def __init__(
            self,
            grid_definition: easi_grid.Grid,
            out_of_bounds_behavior: OutOfBoundsBehavior = OutOfBoundsBehavior.IGNORE
    ) -> None:
        """

        :param grid_definition:
        :param out_of_bounds_behavior:

        :raises AssertionError: If the out_of_bounds_behavior is not one of the defined OutOfBoundsBehavior values.
        :raises AssertionError: If the grid_definition is not an instance of the Grid class.
        """

        self.grid_definition = grid_definition
        self.buckets = self._create_buckets()

        # Store the out-of-bounds behavior and initialize an empty list for out-of-bounds buckets
        assert out_of_bounds_behavior in OutOfBoundsBehavior, \
            f"Invalid out_of_bounds_behavior: {out_of_bounds_behavior}. Must be one of {list(OutOfBoundsBehavior)}."
        self.out_of_bounds_behavior = out_of_bounds_behavior
        self.out_of_bounds_bucket = []

    @classmethod
    def from_easi_grid_preset(cls, preset_name: str):
        """
        Create a BucketGrid instance from a predefined EASI grid preset.
        """
        grid_definition = Grid.from_preset(preset_name)
        return cls(grid_definition)

    def _create_buckets(self) -> List[List[List]]:
        """
        Create buckets based on the grid definition. Here, a bucket is a simple
        python list, because list appending is faster than anything numpy might offer.

        """
        dimx, dimy = self.grid_definition.array_shape
        return [[[] for _ in range(dimx)] for _ in range(dimy)]


# Type variable for the fields argument in make_dataclass.
MAKE_DATACLASS_FIELDS = Union[
    str,
    Iterable[Tuple[str, type]],
    Iterable[Tuple[str, type, Any]],
    Iterable[Tuple[str, type, Field]]
]

