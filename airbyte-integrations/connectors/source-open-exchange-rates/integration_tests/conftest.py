#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import os
import time

import pytest

from airbyte_cdk import Connector



@pytest.fixture(scope="session", autouse=True)
def oxr_app_id():
    """
    Get OpenExchangeRates App id from config file located in "secrets" directory
    """
    secrets_dirpath = os.path.sep.join([os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "secrets"])
    secrets_config_filename = "config.json"
    secrets_config_filepath = os.path.sep.join([secrets_dirpath, secrets_config_filename])

    config = Connector.read_config(secrets_config_filepath)

    app_id = config.get("app_id")
    if app_id is None:
        raise ValueError("app_id must be set in config file {secrets_config_filepath}")

    pytest.oxr_app_id = app_id

    yield

    
