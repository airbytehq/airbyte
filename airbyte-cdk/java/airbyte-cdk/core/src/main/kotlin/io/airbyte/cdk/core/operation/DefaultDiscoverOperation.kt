/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.core.operation

import io.airbyte.cdk.core.context.env.ConnectorConfigurationPropertySource
import io.airbyte.cdk.core.operation.executor.OperationExecutor
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Requires
import jakarta.inject.Named
import jakarta.inject.Singleton

private val logger = KotlinLogging.logger {}

@Singleton
@Named("discoverOperation")
@Requires(
    property = ConnectorConfigurationPropertySource.CONNECTOR_OPERATION,
    value = "discover",
)
@Requires(env = ["source"])
class DefaultDiscoverOperation(
    @Named("discoverOperationExecutor") private val operationExecutor: OperationExecutor,
) : Operation {
    override fun type(): OperationType {
        return OperationType.DISCOVER
    }

    override fun execute(): Result<AirbyteMessage?> {
        logger.info { "Using default check operation." }
        return operationExecutor.execute()
    }
}
