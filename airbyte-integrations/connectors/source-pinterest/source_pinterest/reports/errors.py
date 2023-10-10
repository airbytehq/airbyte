#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


class RetryableException(Exception):
    """Custom Exception Class for Retryable Exception"""

    pass


class ReportGenerationFailure(RetryableException):
    """Custom Exception Class for Report Generation Failure"""

    pass


class ReportGenerationInProgress(RetryableException):
    """Custom Exception Class for Report Generation In Progress"""

    pass


class ReportStatusError(RetryableException):
    """Custom Exception Class for Report Status Error"""

    pass
