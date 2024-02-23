/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.core.operation

import io.airbyte.protocol.models.v0.AirbyteMessage

/**
 * Interface that defines a CLI operation.  Each operation maps to one of the available {@link OperationType}s and
 * proxies to an {@link OperationExecutor} that performs the actual work.
 */
interface Operation {
    fun type(): OperationType

    fun execute(): Result<AirbyteMessage?>
}
