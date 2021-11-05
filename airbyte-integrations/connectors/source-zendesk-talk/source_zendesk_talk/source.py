#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from base_python import BaseSource

from .client import Client


class SourceZendeskTalk(BaseSource):
    client_class = Client
