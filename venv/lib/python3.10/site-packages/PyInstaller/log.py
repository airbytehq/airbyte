#-----------------------------------------------------------------------------
# Copyright (c) 2013-2023, PyInstaller Development Team.
#
# Distributed under the terms of the GNU General Public License (version 2
# or later) with exception for distributing the bootloader.
#
# The full license is in the file COPYING.txt, distributed with this software.
#
# SPDX-License-Identifier: (GPL-2.0-or-later WITH Bootloader-exception)
#-----------------------------------------------------------------------------
"""
Logging module for PyInstaller.
"""

__all__ = ['getLogger', 'INFO', 'WARN', 'DEBUG', 'TRACE', 'ERROR', 'FATAL', 'DEPRECATION']

import os
import logging
from logging import DEBUG, ERROR, FATAL, INFO, WARN, getLogger

TRACE = DEBUG - 5
logging.addLevelName(TRACE, 'TRACE')
DEPRECATION = WARN + 5
logging.addLevelName(DEPRECATION, 'DEPRECATION')
LEVELS = {
    'TRACE': TRACE,
    'DEBUG': DEBUG,
    'INFO': INFO,
    'WARN': WARN,
    'DEPRECATION': DEPRECATION,
    'ERROR': ERROR,
    'FATAL': FATAL,
}

FORMAT = '%(relativeCreated)d %(levelname)s: %(message)s'
_env_level = os.environ.get("PYI_LOG_LEVEL", "INFO")
try:
    level = LEVELS[_env_level.upper()]
except KeyError:
    raise SystemExit(f"Invalid PYI_LOG_LEVEL value '{_env_level}'. Should be one of {list(LEVELS)}.")
logging.basicConfig(format=FORMAT, level=level)
logger = getLogger('PyInstaller')


def __add_options(parser):
    parser.add_argument(
        '--log-level',
        choices=LEVELS,
        metavar="LEVEL",
        dest='loglevel',
        help='Amount of detail in build-time console messages. LEVEL may be one of %s (default: INFO). '
        'Also settable via and overrides the PYI_LOG_LEVEL environment variable.' % ', '.join(LEVELS),
    )


def __process_options(parser, opts):
    if opts.loglevel:
        try:
            level = opts.loglevel.upper()
            _level = LEVELS[level]
        except KeyError:
            parser.error('Unknown log level `%s`' % opts.loglevel)
        logger.setLevel(_level)
        os.environ["PYI_LOG_LEVEL"] = level
