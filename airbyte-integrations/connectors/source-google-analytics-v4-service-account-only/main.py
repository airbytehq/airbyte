#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from airbyte_cdk.exception_handler import init_uncaught_exception_handler
from airbyte_cdk.logger import init_logger
from airbyte_cdk.models import FailureType
from airbyte_cdk.utils import AirbyteTracedException

if __name__ == "__main__":
    logger = init_logger("airbyte")
    init_uncaught_exception_handler(logger)

    error_message = "Google Analytics Universal Analytics Source Connector will be deprecated due to the deprecation of the Google Analytics Universal Analytics API by Google. This deprecation is scheduled by Google on July 1, 2024 (see Google’s Documentation for more details). Transition to the Google Analytics 4 (GA4) Source Connector by July 1, 2024, to continue accessing your analytics data."
    raise AirbyteTracedException(
        message=error_message,
        internal_message=error_message,
        failure_type=FailureType.config_error,
    )
