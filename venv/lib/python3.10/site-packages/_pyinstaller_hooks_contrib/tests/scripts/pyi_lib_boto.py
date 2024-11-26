# -----------------------------------------------------------------------------
# Copyright (c) 2015-2020, PyInstaller Development Team.
#
# Distributed under the terms of the GNU General Public License (version 2
# or later) with exception for distributing the bootloader.
#
# The full license is in the file COPYING.txt, distributed with this software.
#
# SPDX-License-Identifier: (GPL-2.0-or-later WITH Bootloader-exception)
# -----------------------------------------------------------------------------

from inspect import getmembers, isfunction
from functools import partial
import boto
import boto.exception

credentials = dict(
    aws_access_key_id='ASIAIH3F2FU3T63KIXKA',
    aws_secret_access_key='lnN4qk1a0SuQAFVsGA+Y+ujo2/5rLq2j+a1O4Vuy')
# connect_cloudsearchdomain is broken in boto; the rest require custom params
skip = {
    'connect_cloudsearchdomain',
    'connect_ec2_endpoint',
    'connect_gs',
    'connect_euca',
    'connect_ia',
    'connect_walrus',
}
connect_funcs = [
    func for name, func in getmembers(boto)
    if isfunction(func) and name.startswith('connect_') and name not in skip
]
connect_funcs += [
    partial(boto.connect_ec2_endpoint, 'https://ec2.amazonaws.com',
            **credentials),
    partial(boto.connect_gs, gs_access_key_id='', gs_secret_access_key=''),
    partial(boto.connect_euca, host=None, **credentials),
    partial(boto.connect_ia, ia_access_key_id='', ia_secret_access_key=''),
    partial(boto.connect_walrus, host='s3.amazonaws.com', **credentials),
]
for connect_func in connect_funcs:
    if isfunction(connect_func):
        connect_func(**credentials)
    else:
        connect_func()
