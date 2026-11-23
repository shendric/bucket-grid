# -*- coding: utf-8 -*-
"""

"""

__author__ = "Stefan Hendricks <stefan.hendricks@awi.de>"

import cftime
import numpy as np
import pandas as pd
import xarray as xr

from pathlib import Path
from typing import List, Tuple, Type, Dict

from bucket_grid import BucketGrid, bucket_data_factory
from bucket_grid.analysis import GridAnalysis, GridAnalysisMethod, GridAnalysisMethodQueue, IndicesTarget

from easi_grid import Grid

UNLABELLED_FILE = r"C:\Users\Stefan-AWI\Downloads\test_data_three_days_untill_20230113_unlabeled_with_results.csv"
LABELLED_FILE = r"C:\Users\Stefan-AWI\Downloads\test_data_20230113_with_results.csv"

GRID_DEFINITION = Grid(
    "6931",
    (-5_400_000, 5_400_000, -5_400_000, 5_400_000),
    200_000,
    "cci_ease2_nh_100km"
)

def main() -> None:

    queue = [
        "num_points",
        SurfaceTypeStatistics(),
        CorrectPrediction(),
        MedianTrueLabel(),
    ]
    create_gridded_file(Path(LABELLED_FILE), queue)
    create_gridded_file(Path(UNLABELLED_FILE), queue[:-2])

def create_gridded_file(csv_file: Path, queue) -> None:
    bucket_data_def, points = get_point_list(csv_file)
    grid = BucketGrid(GRID_DEFINITION, bucket_data_def)
    grid.add(points)
    analysis_queue = GridAnalysisMethodQueue(queue)
    analysis = GridAnalysis(grid, analysis_queue)
    analysis.to_netcdf(csv_file.with_suffix(".nc"))


def get_point_list(csv_file: Path) -> Tuple[Type, List[Type]]:
    bucket_data_def = bucket_data_factory(
        [
            ("time", cftime.DatetimeJulian),
            ("latitude", np.float32),
            ("longitude", np.float32),
            ("true_label", np.int8),
            ("predicted_label", np.int8),
        ]
    )
    csv_data = pd.read_csv(csv_file)
    print("Loaded CSV data with shape:", csv_data.shape)

    # Create a list of bucket data instances from the CSV data
    points = [
        bucket_data_def(
            time=cftime.num2date((row["timestamp"]), units="seconds since 1970-01-01", calendar="julian"),
            latitude=row["latitude"],
            longitude=row["longitude"],
            true_label=row["true_labels"],
            predicted_label=row["predicted_labels"],
        ) for _, row in csv_data.iterrows()
    ]
    print("Created", len(points), "bucket data points")
    return bucket_data_def, points


class SurfaceTypeStatistics(GridAnalysisMethod):

    grid_indices_target = IndicesTarget.NON_EMPTY

    def __init__(self) -> None:
        ...

    def init_return_data(self, shape,callback) -> Dict[str, xr.DataArray]:
        """
        Initialize the xarray.Dataset for analysis results.

        :return: Initialized xarray.Dataset.
        """
        # Define the dataset structure here

        # Additional coordinate (surface_type) for the data array
        surface_type_var = xr.DataArray(
            np.array([0, 1, 2], dtype=np.uint8),
            dims=["surface_type"],
            attrs={
                "long_name": "Surface Type",
                "valid_min": np.uint8(0),
                "valid_max": np.uint8(2),
                "flag_values": np.array([0, 1, 2], dtype=np.uint8),
                "flag_meanings": "new_ice first_year_ice multi_year_ice",
            }
        )
        data_array_default = callback.get_data_array_coords( )

        new_shape = (*shape, 3)  # Extend shape to include surface_type dimension
        return {
            "surface_type_fraction": xr.DataArray(
                np.full(new_shape, np.nan, dtype=np.float32),
                name="surface_type_fraction",
                dims=["yc", "xc", "surface_type"],
                attrs={
                    "long_name": "Surface Type Fractions",
                    "valid_min": np.float32(0.0),
                    "valid_max": np.float32(1.0),
                    "comments": "Fraction of each surface type in the grid cell"
                },
                coords={
                    "yc": data_array_default["coords"]["yc"],
                    "xc": data_array_default["coords"]["xc"],
                    "surface_type": surface_type_var
                }

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
        Compute the fraction of each surface type in the grid cell and store it in the data array.

        :param points:
        :param yj:
        :param ix:
        :param da_dict:
        :param callback:

        :return: None, updates da_dict in place.
        """
        num_points = float(len(points))
        for sx in range(3):
            num_surface_type = float(sum(1. for p in points if p.predicted_label == sx))
            value = float(num_surface_type)  / num_points if num_points > 0 else np.nan
            da_dict["surface_type_fraction"].values[yj, ix, sx] = value


class CorrectPrediction(GridAnalysisMethod):

    grid_indices_target = IndicesTarget.NON_EMPTY

    def __init__(self) -> None:
        ...

    def init_return_data(self, shape,callback) -> Dict[str, xr.DataArray]:
        """
        Initialize the xarray.Dataset for analysis results.

        :return: Initialized xarray.Dataset.
        """
        # Define the dataset structure here

        # Additional coordinate (surface_type) for the data array
        data_array_default = callback.get_data_array_coords()

        return {
            "correct_prediction_fraction": xr.DataArray(
                np.full(shape, np.nan, dtype=np.float32),
                name="correct_prediction_fraction",
                dims=["yc", "xc"],
                attrs={
                    "long_name": "Correct Prediction Fraction",
                    "valid_min": np.float32(0.0),
                    "valid_max": np.float32(1.0),
                    "comments": "Fraction of correct (predicted=True) label in the grid cell"
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
        Compute the fraction of correct (predicted=True) labels in the grid cell and store it in the data array.

        :param points:
        :param yj:
        :param ix:
        :param da_dict:
        :param callback:

        :return: None, updates da_dict in place.
        """
        correct_labels = float(sum(1. for p in points if (p.predicted_label == p.true_label)))
        value = float(correct_labels)  / float(len(points)) if len(points) > 0 else np.nan
        da_dict["correct_prediction_fraction"].values[yj, ix] = value


class MedianTrueLabel(GridAnalysisMethod):

    grid_indices_target = IndicesTarget.NON_EMPTY

    def __init__(self) -> None:
        ...

    def init_return_data(self, shape,callback) -> Dict[str, xr.DataArray]:
        """
        Initialize the xarray.Dataset for analysis results.

        :return: Initialized xarray.Dataset.
        """
        # Define the dataset structure here

        # Additional coordinate (surface_type) for the data array
        data_array_default = callback.get_data_array_coords()

        return {
            "median_true_label": xr.DataArray(
                np.full(shape, -1, dtype=np.int8),
                dims=["yc", "xc"],
                name="median_true_label",
                attrs={
                    "long_name": "Median True Label",
                    "valid_min": np.int8(-1),
                    "valid_max": np.int8(2),
                    "flag_values": np.array([-1, 0, 1, 2], dtype=np.int8),
                    "flag_meanings": "no_data new_ice first_year_ice multi_year_ice",
                    "comments": "Median of true labels in the grid cell"
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
        Compute the fraction of correct (predicted=True) labels in the grid cell and store it in the data array.

        :param points:
        :param yj:
        :param ix:
        :param da_dict:
        :param callback:

        :return: None, updates da_dict in place.
        """
        true_labels = [p.true_label for p in points]
        da_dict["median_true_label"].values[yj, ix] = np.median(true_labels) if true_labels else np.int8(-1)


if __name__ == "__main__":
    main()
