# Copyright 2021 Monty Taylor
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""PEP-517 / PEP-660 support

Add::

    [build-system]
    requires = ["pbr>=6.0.0", "setuptools>=64.0.0"]
    build-backend = "pbr.build"

to ``pyproject.toml`` to use this.
"""

from setuptools import build_meta

__all__ = [
    'get_requires_for_build_sdist',
    'get_requires_for_build_wheel',
    'prepare_metadata_for_build_wheel',
    'build_wheel',
    'build_sdist',
    'build_editable',
    'get_requires_for_build_editable',
    'prepare_metadata_for_build_editable',
]


# PEP-517

def get_requires_for_build_wheel(config_settings=None):
    return build_meta.get_requires_for_build_wheel(
        config_settings=config_settings,
    )


def get_requires_for_build_sdist(config_settings=None):
    return build_meta.get_requires_for_build_sdist(
        config_settings=config_settings,
    )


def prepare_metadata_for_build_wheel(metadata_directory, config_settings=None):
    return build_meta.prepare_metadata_for_build_wheel(
        metadata_directory,
        config_settings=config_settings,
    )


def build_wheel(
    wheel_directory,
    config_settings=None,
    metadata_directory=None,
):
    return build_meta.build_wheel(
        wheel_directory,
        config_settings=config_settings,
        metadata_directory=metadata_directory,
    )


def build_sdist(sdist_directory, config_settings=None):
    return build_meta.build_sdist(
        sdist_directory,
        config_settings=config_settings,
    )


# PEP-660

def build_editable(
    wheel_directory,
    config_settings=None,
    metadata_directory=None,
):
    return build_meta.build_editable(
        wheel_directory,
        config_settings=config_settings,
        metadata_directory=metadata_directory,
    )


def get_requires_for_build_editable(config_settings=None):
    return build_meta.get_requires_for_build_editable(
        config_settings=config_settings,
    )


def prepare_metadata_for_build_editable(
    metadata_directory,
    config_settings=None,
):
    return build_meta.prepare_metadata_for_build_editable(
        metadata_directory,
        config_settings=config_settings,
    )
