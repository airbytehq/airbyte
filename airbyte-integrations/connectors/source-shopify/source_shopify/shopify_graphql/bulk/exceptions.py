#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


class ShopifyBulkExceptions:
    class BaseBulkException(Exception):
        def __init__(self, message: str):
            super().__init__(message)

    class BulkJobError(BaseBulkException):
        """Raised when there are BULK Job Errors in response"""

    class BulkJobUnknownError(BaseBulkException):
        """Raised when BULK Job has FAILED with Unknown status"""

    class BulkJobBadResponse(BaseBulkException):
        """Raised when the requests.Response object could not be parsed"""

    class BulkJobResultUrlError(BaseBulkException):
        """Raised when BULK Job has ACCESS_DENIED status"""

    class BulkRecordProduceError(BaseBulkException):
        """Raised when there are error producing records from BULK Job result"""

    class BulkJobFailed(BaseBulkException):
        """Raised when BULK Job has FAILED status"""

    class BulkJobTimout(BaseBulkException):
        """Raised when BULK Job has TIMEOUT status"""

    class BulkJobAccessDenied(BaseBulkException):
        """Raised when BULK Job has ACCESS_DENIED status"""

    class BulkJobConcurrentError(BaseBulkException):
        """Raised when BULK Job could not be created, since the 1 Bulk job / shop quota is exceeded."""
