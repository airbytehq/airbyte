#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging

import pytest
import requests
from airbyte_cdk.sources.declarative.auth.token import ApiKeyAuthenticator, BasicHttpAuthenticator, BearerAuthenticator
from airbyte_cdk.sources.declarative.auth.token_provider import InterpolatedStringTokenProvider
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOption, RequestOptionType
from requests import Response

# TODO add tests for the interpolated string token provider

# TODO add tests for the session token provider