# --LICENSE--#
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
# --LICENSE--#


from airbyte_cdk.base_python.catalog_helpers import CatalogHelper
from airbyte_cdk.base_python.cdk.abstract_source import AbstractSource

# Separate the SDK imports so they can be moved somewhere else more easily
from airbyte_cdk.base_python.cdk.streams.auth.core import HttpAuthenticator
from airbyte_cdk.base_python.cdk.streams.auth.oauth import Oauth2Authenticator
from airbyte_cdk.base_python.cdk.streams.auth.token import TokenAuthenticator
from airbyte_cdk.base_python.cdk.streams.core import Stream
from airbyte_cdk.base_python.cdk.streams.exceptions import UserDefinedBackoffException
from airbyte_cdk.base_python.cdk.streams.http import HttpStream
from airbyte_cdk.base_python.client import BaseClient
from airbyte_cdk.base_python.integration import AirbyteSpec, Destination, Integration, Source
from airbyte_cdk.base_python.logger import AirbyteLogger
from airbyte_cdk.base_python.source import BaseSource

# Must be the last one because the way we load the connector module creates a circular
# dependency and models might not have been loaded yet
from airbyte_cdk.base_python.entrypoint import AirbyteEntrypoint  # noqa isort:skip

__all__ = [
    "AirbyteLogger",
    "AirbyteSpec",
    "AbstractSource",
    "BaseClient",
    "BaseSource",
    "CatalogHelper",
    "Destination",
    "HttpAuthenticator",
    "HttpStream",
    "Integration",
    "Oauth2Authenticator",
    "Source",
    "Stream",
    "TokenAuthenticator",
    "UserDefinedBackoffException",
]
