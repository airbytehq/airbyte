/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.core.operation.executor

import io.airbyte.cdk.core.context.env.ConnectorConfigurationPropertySource
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Requires
import jakarta.inject.Named
import jakarta.inject.Singleton

private val logger = KotlinLogging.logger {}

@Singleton
@Named("checkOperationExecutor")
@Requires(
    property = ConnectorConfigurationPropertySource.CONNECTOR_OPERATION,
    value = "check",
)
class DefaultCheckOperationExecutor : OperationExecutor {
    override fun execute(): Result<AirbyteMessage?> {
        logger.info { "Using default check operation executor." }
        return Result.success(
            AirbyteMessage()
                .withType(AirbyteMessage.Type.CONNECTION_STATUS)
                .withConnectionStatus(
                    AirbyteConnectionStatus().withStatus(AirbyteConnectionStatus.Status.SUCCEEDED),
                ),
        )
    }
}
