#-----------------------------------------------------------------------------
# Copyright (c) 2023, PyInstaller Development Team.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#
# SPDX-License-Identifier: Apache-2.0
#-----------------------------------------------------------------------------

def _pyi_rthook():
    import sys

    # `tensorflow` versions prior to 2.3.0 attempt to use `site.USER_SITE` in path/string manipulation functions.
    # As frozen application runs with disabled `site`, the value of this variable is `None`, and causes path/string
    # manipulation functions to raise an error. As a work-around, we set `site.USER_SITE` to an empty string, which is
    # also what the fake `site` module available in PyInstaller prior to v5.5 did.
    import site

    if site.USER_SITE is None:
        site.USER_SITE = ''

    # The issue described about with site.USER_SITE being None has largely been resolved in contemporary `tensorflow`
    # versions, which now check that `site.ENABLE_USER_SITE` is set and that `site.USER_SITE` is not None before
    # trying to use it.
    #
    # However, `tensorflow` will attempt to search and load its plugins only if it believes that it is running from
    # "a pip-based installation" - if the package's location is rooted in one of the "site-packages" directories. See
    # https://github.com/tensorflow/tensorflow/blob/6887368d6d46223f460358323c4b76d61d1558a8/tensorflow/api_template.__init__.py#L110C76-L156
    # Unfortunately, they "cleverly" infer the module's location via `inspect.getfile(inspect.currentframe())`, which
    # in the frozen application returns anonymized relative source file name (`tensorflow/__init__.py`) - so we need one
    # of the "site directories" to be just "tensorflow" (to fool the `_running_from_pip_package()` check), and we also
    # need `sys._MEIPASS` to be among them (to load the plugins from the actual `sys._MEIPASS/tensorflow-plugins`).
    # Therefore, we monkey-patch `site.getsitepackages` to add those two entries to the list of "site directories".

    _orig_getsitepackages = getattr(site, 'getsitepackages')

    def _pyi_getsitepackages():
        return [
            sys._MEIPASS,
            "tensorflow",
            *(_orig_getsitepackages() if _orig_getsitepackages is not None else []),
        ]

    site.getsitepackages = _pyi_getsitepackages

    # NOTE: instead of the above override, we could also set TF_PLUGGABLE_DEVICE_LIBRARY_PATH, but that works only
    # for tensorflow >= 2.12.


_pyi_rthook()
del _pyi_rthook
