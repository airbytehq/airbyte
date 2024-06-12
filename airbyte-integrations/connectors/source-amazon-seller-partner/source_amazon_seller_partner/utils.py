#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from airbyte_cdk.utils import AirbyteTracedException
from airbyte_protocol.models import FailureType


class AmazonConfigException(AirbyteTracedException):
    def __init__(self, **kwargs):
        failure_type: FailureType = FailureType.config_error
        super(AmazonConfigException, self).__init__(failure_type=failure_type, **kwargs)
