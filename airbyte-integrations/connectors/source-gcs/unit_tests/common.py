# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from pathlib import Path


def catalog_path():
    return Path(__file__).resolve().parent.joinpath("resource/catalog/")


def config_path():
    return Path(__file__).resolve().parent.joinpath("resource/config/")
