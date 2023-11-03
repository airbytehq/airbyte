#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from airbyte_cdk.sources.declarative.requesters import LowCodeHttpRequester


class SampleCustomComponent(LowCodeHttpRequester):
    """
    A test class used to validate manifests that rely on custom defined Python components
    """

    pass
