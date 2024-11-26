# ------------------------------------------------------------------
# Copyright (c) 2022 PyInstaller Development Team.
#
# This file is distributed under the terms of the GNU General Public
# License (version 2.0 or later).
#
# The full license is available in LICENSE.GPL.txt, distributed with
# this software.
#
# SPDX-License-Identifier: GPL-2.0-or-later
# ------------------------------------------------------------------
#
# A modern, feature-rich and highly-tunable Python client library for Apache Cassandra (2.1+) and
# DataStax Enterprise (4.7+) using exclusively Cassandra's binary protocol and Cassandra Query Language v3.
#
# http://datastax.github.io/python-driver/api/index.html
#
# Tested with cassandra-driver 3.25.0

from PyInstaller.utils.hooks import collect_submodules

hiddenimports = collect_submodules('cassandra')
