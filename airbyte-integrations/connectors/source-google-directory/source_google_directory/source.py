#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from airbyte_cdk.sources.deprecated.base_source import BaseSource

from .client import Client


class SourceGoogleDirectory(BaseSource):
    client_class = Client
