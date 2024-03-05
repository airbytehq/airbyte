/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.core.operation

/** Custom exception that represents a failure to execute an operation. */
class OperationExecutionException(message: String, cause: Throwable) : Exception(message, cause)
