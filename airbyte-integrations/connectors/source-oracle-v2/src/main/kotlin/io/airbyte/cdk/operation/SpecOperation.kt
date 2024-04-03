/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.operation

import io.airbyte.cdk.command.ConnectorConfigurationJsonObjectSupplier
import io.airbyte.cdk.consumers.OutputConsumer
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.ConnectorSpecification
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Requires
import io.micronaut.context.annotation.Value
import jakarta.inject.Singleton
import java.net.URI

private val logger = KotlinLogging.logger {}

@Singleton
@Requires(property = CONNECTOR_OPERATION, value = "spec")
class SpecOperation(
    @Value("\${airbyte.connector.documentationUrl}") val documentationUrl: String,
    val configJsonObjectSupplier: ConnectorConfigurationJsonObjectSupplier<*>,
    val outputConsumer: OutputConsumer
) : Operation {

    override val type = OperationType.SPEC

    override fun execute() {
        logger.info { "Performing SPEC operation." }
        val spec = ConnectorSpecification()
        try {
            spec.documentationUrl = URI.create(documentationUrl)
        } catch (e: Exception) {
            logger.error(e) { "Invalid documentation URL '$documentationUrl'." }
            throw OperationExecutionException(
                "Failed to generate connector specification " +
                    "using documentation URL '$documentationUrl'.",
                e,
            )
        }
        try {
            spec.connectionSpecification = configJsonObjectSupplier.jsonSchema
        } catch (e: Exception) {
            logger.error(e) {
                "Invalid configuration class '${configJsonObjectSupplier.valueClass}'."
            }
            throw OperationExecutionException(
                "Failed to generate connector specification " +
                    "using configuration class '${configJsonObjectSupplier.valueClass}'.",
                e,
            )
        }
        outputConsumer.accept(AirbyteMessage()
            .withType(AirbyteMessage.Type.SPEC)
            .withSpec(spec))
    }

}
