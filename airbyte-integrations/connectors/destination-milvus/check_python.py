# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import sys


print(f"Python {sys.version_info.major}.{sys.version_info.minor}")

try:
    from distutils import version

    print("distutils available in stdlib")
except ImportError:
    print("distutils NOT available in stdlib")

try:
    import pkg_resources

    print("pkg_resources available")
except ImportError:
    print("pkg_resources NOT available")
