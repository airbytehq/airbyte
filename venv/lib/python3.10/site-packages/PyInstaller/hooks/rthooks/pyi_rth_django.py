#-----------------------------------------------------------------------------
# Copyright (c) 2005-2023, PyInstaller Development Team.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#
# SPDX-License-Identifier: Apache-2.0
#-----------------------------------------------------------------------------

# This Django rthook was tested with Django 1.8.3.


def _pyi_rthook():
    import django.utils.autoreload

    _old_restart_with_reloader = django.utils.autoreload.restart_with_reloader

    def _restart_with_reloader(*args):
        import sys
        a0 = sys.argv.pop(0)
        try:
            return _old_restart_with_reloader(*args)
        finally:
            sys.argv.insert(0, a0)

    # Override restart_with_reloader() function, otherwise the app might complain that some commands do not exist;
    # e.g., runserver.
    django.utils.autoreload.restart_with_reloader = _restart_with_reloader


_pyi_rthook()
del _pyi_rthook
