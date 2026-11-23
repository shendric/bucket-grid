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


# Type variable for the fields argument in make_dataclass.
MAKE_DATACLASS_FIELDS = Union[
    str,
    Iterable[Tuple[str, type]],
    Iterable[Tuple[str, type, Any]],
    Iterable[Tuple[str, type, Field]]
]


class OutOfBoundsBehavior(StrEnum):
    IGNORE = "ignore"
    ERROR = "error"


def _post_init(self):
    """
    A post-initialization method for dataclasses that attempts
    to coerce the types of the fields to their specified types.
    This is mainly written to ensure that floats and ints are
    the correct numpy data types.

    :param self:

    :return: None
    """
    for field in self.__dataclass_fields__.values():
        try:
            setattr(self, field.name, field.type(getattr(self, field.name)))
        except Exception:
            pass  # keep original value if coercion fails


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
        namespace={
            "hash_value": lambda self: hash((self.__dataclass_fields__.keys())),
            "__post_init__": _post_init
        },
        slots=True,
    )


class BucketGrid(object):
    """
    Class for gridding data into buckets.
    """

    def __init__(
            self,
            grid_definition: easi_grid.Grid,
            data_definition: Type,
            out_of_bounds_behavior: OutOfBoundsBehavior = OutOfBoundsBehavior.IGNORE
    ) -> None:
        """

        :param grid_definition:
        :param out_of_bounds_behavior:

        :raises ValueError: If the out_of_bounds_behavior is not one of the defined OutOfBoundsBehavior values.
        :raises ValueError: If the grid_definition is not an instance of the Grid class.
        """

        # Grid definition is handled by easi-grid
        if not isinstance(grid_definition, easi_grid.Grid):
            raise ValueError(f"grid_definition must be an instance of easi_grid.Grid, got {type(grid_definition)}")
        self.grid_definition = grid_definition

        # Data definition is a dataclass created by bucket_data_factory
        if not hasattr(data_definition, "__dataclass_fields__"):
            raise ValueError(
                f"data_definition must be a dataclass created by bucket_data_factory, got {type(data_definition)}"
            )
        self.data_definition = data_definition

        # Create the buckets based on the grid definition
        self.buckets = self._create_buckets()
        self._n_points = 0

        # Store the out-of-bounds behavior and initialize an empty list for out-of-bounds buckets
        if not isinstance(out_of_bounds_behavior, OutOfBoundsBehavior):
            raise ValueError(
                f"Invalid out_of_bounds_behavior: {out_of_bounds_behavior}. "
                f"Must be one of {list(OutOfBoundsBehavior)}."
            )
        self.out_of_bounds_behavior = out_of_bounds_behavior
        self.out_of_bounds_bucket = []

    @classmethod
    def from_easi_grid_preset(cls, preset_name: str, *args, **kwargs) -> "BucketGrid":
        """
        Create a BucketGrid instance from a predefined EASI grid preset.
        """
        grid_definition = Grid.from_preset(preset_name)
        return cls(grid_definition, *args, **kwargs)

    def add(self, points: List[Type]) -> None:
        """
        Add a list of data points to the corresponding buckets based on their latitude and longitude.

        :param points: A list of data points, each of which should be a data class with the
            required fields (latitude, longitude, and any other fields).
            See function bucket_data_factory for creating a suitable data class for the points.

        :raises ValueError: If a point is out of bounds and the out_of_bounds_behavior is set to ERROR.

        :return: None, data is added to corresponding buckets in place.
        """
        grid_indices = [self.grid_definition.get_indices(point.longitude, point.latitude) for point in points]
        self._n_points += len(points)

        for point, (xi, yj) in zip(points, grid_indices):
            try:
                self.buckets[yj][xi].append(point)
            except IndexError:
                if self.out_of_bounds_behavior == OutOfBoundsBehavior.IGNORE:
                    self.out_of_bounds_bucket.append(point)
                    self._n_points -= 1
                elif self.out_of_bounds_behavior == OutOfBoundsBehavior.ERROR:
                    raise ValueError(f"Point {point} is out of bounds for the grid.")

    def _create_buckets(self) -> List[List[List]]:
        """
        Create buckets based on the grid definition. Here, a bucket is a simple
        python list, because list appending is faster than anything numpy might offer.

        """
        dimx, dimy = self.grid_definition.array_shape
        return [[[] for _ in range(dimx)] for _ in range(dimy)]

    def get(self, yj: int, xi: int) -> List[Type]:
        """
        Get the list of data points in the bucket at the specified grid indices.

        :param yj: The y-index of the grid cell.
        :param xi: The x-index of the grid cell.

        :return: A list of data points in the specified bucket.
        """
        try:
            return self.buckets[yj][xi]
        except IndexError as ie:
            raise IndexError(f"Grid indices (yj={yj}, xi={xi}) are out of bounds for the grid shape {self.shape}.") from ie

    def get_all_indices(self) -> List[Tuple[int, int]]:
        """
        Get all grid indices as a list of (yj, xi) tuples.

        :return: List of all grid indices.
        """
        dimx, dimy = self.grid_definition.array_shape
        return [(yj, xi) for yj in range(dimy) for xi in range(dimx)]

    def get_non_empty_indices(self) -> List[Tuple[int, int]]:
        """
        Get non-empty grid indices as a list of (yj, xi) tuples.

        :return: List of non-empty grid indices.
        """
        return [(yj, xi) for yj, row in enumerate(self.buckets) for xi, bucket in enumerate(row) if bucket]

    @property
    def shape(self) -> Tuple[int, int]:
        """
        Get the shape of the grid as a tuple (dimy, dimx).
        """
        return self.grid_definition.array_shape

    @property
    def num_points(self) -> int:
        """
        Get the total number of points added to the grid.

        :return: Point number
        """
        return int(self._n_points)

    @property
    def num_out_of_bounds_points(self) -> int:
        """
        Get the total number of points added to the grid.

        :return: Point number
        """
        return len(self.out_of_bounds_bucket)



