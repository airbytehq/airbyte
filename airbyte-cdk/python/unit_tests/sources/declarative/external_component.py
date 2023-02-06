#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from airbyte_cdk.sources.declarative.requesters import HttpRequester


class SampleCustomComponent(HttpRequester):
    """
    A test class used to validate manifests that rely on custom defined Python components
    """

    pass
