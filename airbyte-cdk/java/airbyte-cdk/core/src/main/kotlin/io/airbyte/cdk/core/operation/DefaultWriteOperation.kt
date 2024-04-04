/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.core.operation

import io.airbyte.cdk.core.context.env.ConnectorConfigurationPropertySource
import io.airbyte.cdk.core.operation.executor.OperationExecutor
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.micronaut.context.annotation.Requires
import jakarta.inject.Named
import jakarta.inject.Singleton

@Singleton
@Named("writeOperation")
@Requires(
    property = ConnectorConfigurationPropertySource.CONNECTOR_OPERATION,
    value = "write",
)
@Requires(env = ["destination"])
class DefaultWriteOperation(
    @Named("writeOperationExecutor") private val operationExecutor: OperationExecutor,
) : Operation {
    override fun type(): OperationType {
        return OperationType.WRITE
    }

    override fun execute(): Result<AirbyteMessage?> {
        return operationExecutor.execute()
    }
}
