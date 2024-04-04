/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.operation.executor

import io.airbyte.cdk.core.context.env.ConnectorConfigurationPropertySource
import io.airbyte.cdk.core.operation.executor.OperationExecutor
import io.airbyte.integrations.destination.s3.config.properties.S3ConnectorConfiguration
import io.airbyte.integrations.destination.s3.service.S3BaseChecks
import io.airbyte.integrations.destination.s3.service.S3CheckService
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus
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
@Requires(env = ["cloud"])
class CloudCheckOperationExecutor(
    private val s3BaseChecks: S3BaseChecks,
    private val checkService: S3CheckService,
    private val configuration: S3ConnectorConfiguration,
) : OperationExecutor {
    companion object {
        const val UNSECURED_ENDPOINT_FAILURE_MESSAGE = "Custom endpoint does not use HTTPS"
    }

    override fun execute(): Result<AirbyteMessage?> {
        // Fails early to avoid extraneous validations checks if custom endpoint is not secure
        if (!s3BaseChecks.testCustomEndpointSecured(configuration.s3Endpoint)) {
            return Result.success(
                AirbyteMessage()
                    .withType(AirbyteMessage.Type.CONNECTION_STATUS)
                    .withConnectionStatus(
                        AirbyteConnectionStatus()
                            .withStatus(AirbyteConnectionStatus.Status.FAILED)
                            .withMessage(UNSECURED_ENDPOINT_FAILURE_MESSAGE),
                    ),
            )
        }

        return checkService.check()
    }
}
