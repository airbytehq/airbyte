#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


class RetryableException(Exception):
    """Custom Exception Class for Retryable Exception."""



class ReportGenerationFailure(RetryableException):
    """Custom Exception Class for Report Generation Failure."""



class ReportGenerationInProgress(RetryableException):
    """Custom Exception Class for Report Generation In Progress."""



class ReportStatusError(RetryableException):
    """Custom Exception Class for Report Status Error."""

