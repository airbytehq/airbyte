/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.core.operation.executor

import io.airbyte.protocol.models.v0.AirbyteMessage

/**
 * Interface that defines an operation executor.  An operation executor performs the actual work
 * represented by the operation type, returning a successful or failure result.
 */
interface OperationExecutor {
    fun execute(): Result<AirbyteMessage?>
}
