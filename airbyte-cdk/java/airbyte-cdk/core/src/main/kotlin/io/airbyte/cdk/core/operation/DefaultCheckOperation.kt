/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.core.operation

import io.airbyte.cdk.core.context.env.ConnectorConfigurationPropertySource
import io.airbyte.cdk.core.operation.executor.OperationExecutor
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.micronaut.context.annotation.Requires
import jakarta.inject.Named
import jakarta.inject.Singleton

@Singleton
@Named("checkOperation")
@Requires(
    property = ConnectorConfigurationPropertySource.CONNECTOR_OPERATION,
    value = "check",
)
class DefaultCheckOperation(
    @Named("checkOperationExecutor") private val operationExecutor: OperationExecutor,
) : Operation {
    override fun type(): OperationType {
        return OperationType.CHECK
    }

    override fun execute(): Result<AirbyteMessage?> {
        val result = operationExecutor.execute()
        result.onFailure {
            return Result.success(
                AirbyteMessage()
                    .withType(AirbyteMessage.Type.CONNECTION_STATUS)
                    .withConnectionStatus(
                        AirbyteConnectionStatus()
                            .withStatus(AirbyteConnectionStatus.Status.FAILED)
                            .withMessage(it.message),
                    ),
            )
        }
        return result
    }
}
