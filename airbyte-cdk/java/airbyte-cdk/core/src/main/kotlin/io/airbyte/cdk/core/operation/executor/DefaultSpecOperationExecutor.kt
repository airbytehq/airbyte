/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.core.operation.executor

import io.airbyte.cdk.core.context.env.ConnectorConfigurationPropertySource
import io.airbyte.cdk.core.operation.OperationExecutionException
import io.airbyte.commons.json.Jsons
import io.airbyte.commons.resources.MoreResources
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.ConnectorSpecification
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Requires
import io.micronaut.context.annotation.Value
import jakarta.inject.Named
import jakarta.inject.Singleton

private val logger = KotlinLogging.logger {}

@Singleton
@Named("specOperationExecutor")
@Requires(
    property = ConnectorConfigurationPropertySource.CONNECTOR_OPERATION,
    value = "spec",
)
class DefaultSpecOperationExecutor(
    @Value("\${airbyte.connector.specification.file:spec.json}") private val specFile: String,
) : OperationExecutor {
    override fun execute(): Result<AirbyteMessage> {
        logger.info { "Using default spec operation executor." }
        try {
            val resourceString = MoreResources.readResource(specFile)
            val connectorSpecification =
                Jsons.deserialize(
                    resourceString,
                    ConnectorSpecification::class.java,
                )
            return Result.success(
                AirbyteMessage().withType(AirbyteMessage.Type.SPEC).withSpec(connectorSpecification)
            )
        } catch (e: Exception) {
            return Result.failure(
                OperationExecutionException("Failed to retrieve specification from connector.", e)
            )
        }
    }
}
