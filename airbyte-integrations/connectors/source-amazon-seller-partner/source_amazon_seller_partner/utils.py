#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import logging
import time

from airbyte_cdk.models import FailureType
from airbyte_cdk.utils import AirbyteTracedException


LOG_LEVEL = logging.getLevelName("INFO")
LOGGER = logging.getLogger("airbyte")


class AmazonConfigException(AirbyteTracedException):
    def __init__(self, **kwargs):
        failure_type: FailureType = FailureType.config_error
        super(AmazonConfigException, self).__init__(failure_type=failure_type, **kwargs)
