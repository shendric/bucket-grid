# -*- coding: utf-8 -*-
"""

"""

__author__ = "Stefan Hendricks <stefan.hendricks@awi.de>"

from bucket_grid import BucketGrid, bucket_data_factory


def main() -> None:

    grid = BucketGrid.from_easi_grid_preset("cci_ease2_nh_25km")
    bucket_data_cls = bucket_data_factory((("latitude", float), ("longitude", float), ("value", float)))

    bucket_data = bucket_data_cls(latitude=88.0, longitude=20.0, value=42.0)

    breakpoint()


if __name__ == "__main__":
    main()
