/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.exceptions

/** Custom exception that represents a failure to execute an operation. */
class OperationExecutionException(
    message: String? = null,
    cause: Throwable? = null,
) : Exception(message, cause)
