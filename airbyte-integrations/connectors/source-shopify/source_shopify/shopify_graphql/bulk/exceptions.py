#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from airbyte_cdk.models import FailureType
from airbyte_cdk.utils import AirbyteTracedException


class ShopifyBulkExceptions:
    class BaseBulkException(AirbyteTracedException):
        """Base BULK Job Exception"""

        failure_type: FailureType = FailureType.config_error

        def __init__(self, message: str, **kwargs) -> None:
            super().__init__(internal_message=message, failure_type=self.failure_type, **kwargs)

    class BulkJobError(BaseBulkException):
        """Raised when there are BULK Job Errors in response"""

    class BulkJobNonHandableError(BaseBulkException):
        """Raised when there are non-actionable BULK Job Errors in response"""

        failure_type: FailureType = FailureType.system_error

    class BulkJobBadResponse(BaseBulkException):
        """Raised when the requests.Response object could not be parsed"""

    class BulkJobResultUrlError(BaseBulkException):
        """Raised when BULK Job has ACCESS_DENIED status"""

    class BulkRecordProduceError(BaseBulkException):
        """Raised when there are error producing records from BULK Job result"""

    class BulkJobFailed(BaseBulkException):
        """Raised when BULK Job has FAILED status"""

    class BulkJobCanceled(BaseBulkException):
        """Raised when BULK Job has CANCELED status"""

        failure_type: FailureType = FailureType.system_error

    class BulkJobTimout(BaseBulkException):
        """Raised when BULK Job has TIMEOUT status"""

    class BulkJobAccessDenied(BaseBulkException):
        """Raised when BULK Job has ACCESS_DENIED status"""

    class BulkJobCreationFailedConcurrentError(BaseBulkException):
        """Raised when an attempt to create a job as failed because of concurrency limits."""

        failure_type: FailureType = FailureType.transient_error

    class BulkJobRedirectToOtherShopError(BaseBulkException):
        """Raised when the response contains another shop name"""

        failure_type: FailureType = FailureType.transient_error

    class BulkJobConcurrentError(BaseBulkException):
        """Raised when failing the job after hitting too many BulkJobCreationFailedConcurrentError."""

        failure_type: FailureType = FailureType.transient_error
