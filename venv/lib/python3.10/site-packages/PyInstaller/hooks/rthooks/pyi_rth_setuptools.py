#-----------------------------------------------------------------------------
# Copyright (c) 2022-2023, PyInstaller Development Team.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#
# SPDX-License-Identifier: Apache-2.0
#-----------------------------------------------------------------------------

# This runtime hook performs the equivalent of the distutils-precedence.pth from the setuptools package;
# it registers a special meta finder that diverts import of distutils to setuptools._distutils, if available.


def _pyi_rthook():
    def _install_setuptools_distutils_hack():
        import os
        import setuptools

        # We need to query setuptools version at runtime, because the default value for SETUPTOOLS_USE_DISTUTILS
        # has changed at version 60.0 from "stdlib" to "local", and we want to mimic that behavior.
        setuptools_major = int(setuptools.__version__.split('.')[0])
        default_value = "stdlib" if setuptools_major < 60 else "local"

        if os.environ.get("SETUPTOOLS_USE_DISTUTILS", default_value) == "local":
            import _distutils_hack
            _distutils_hack.add_shim()

    try:
        _install_setuptools_distutils_hack()
    except Exception:
        pass


_pyi_rthook()
del _pyi_rthook
