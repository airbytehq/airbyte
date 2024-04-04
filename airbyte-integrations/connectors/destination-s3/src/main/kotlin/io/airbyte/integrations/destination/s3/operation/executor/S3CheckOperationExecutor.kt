/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.operation.executor

import io.airbyte.cdk.core.context.env.ConnectorConfigurationPropertySource
import io.airbyte.cdk.core.operation.executor.OperationExecutor
import io.airbyte.integrations.destination.s3.service.S3CheckService
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.micronaut.context.annotation.Primary
import io.micronaut.context.annotation.Requires
import jakarta.inject.Named
import jakarta.inject.Singleton

@Singleton
@Primary
@Named("checkOperationExecutor")
@Requires(
    property = ConnectorConfigurationPropertySource.CONNECTOR_OPERATION,
    value = "check",
)
@Requires(notEnv = ["cloud"])
class S3CheckOperationExecutor(private val checkService: S3CheckService) : OperationExecutor {
    override fun execute(): Result<AirbyteMessage?> {
        return checkService.check()
    }
}
