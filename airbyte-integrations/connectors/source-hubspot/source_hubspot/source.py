#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from airbyte_cdk.sources.deprecated.base_source import BaseSource

from .client import Client


class SourceHubspot(BaseSource):
    client_class = Client
