# -*- coding: utf-8 -*-
"""

"""

__author__ = "Stefan Hendricks <stefan.hendricks@awi.de>"

import pytest
from bucket_grid import BucketGrid


# Test data for happy path scenarios
happy_cases_data = [
    ("valid_epsg_6931", 6931, (0., 100., 0., 100.), 10.),
    ("valid_epsg_3857", 6931, (-5_000_000., 5_000_000., -5_000_000., 5_000_000.), 10_000.),
]