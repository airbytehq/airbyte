/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.core.event

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.core.command.option.ConnectorConfiguration
import io.airbyte.cdk.core.context.env.ConnectorConfigurationPropertySource
import io.airbyte.cdk.core.operation.Operation
import io.airbyte.commons.json.Jsons
import io.airbyte.commons.resources.MoreResources
import io.airbyte.validation.json.JsonSchemaValidator
import io.micronaut.context.annotation.Requires
import io.micronaut.context.annotation.Value
import io.micronaut.context.event.ApplicationEventListener
import io.micronaut.context.event.StartupEvent
import jakarta.inject.Singleton
import java.io.IOException

/**
 * Event listener that validates the Airbyte connector configuration, if present. This listener is
 * executed on application start.
 */
@Singleton
@Requires(bean = ConnectorConfiguration::class)
@Requires(property = ConnectorConfigurationPropertySource.CONNECTOR_OPERATION)
class ConfigurationValidator(
    @Value("\${micronaut.application.name}") private val connectorName: String,
    @Value("\${airbyte.connector.operation}") private val operationType: String,
    private val configuration: ConnectorConfiguration,
    private val validator: JsonSchemaValidator,
    private val operation: Operation,
) : ApplicationEventListener<StartupEvent> {
    override fun onApplicationEvent(event: StartupEvent) {
        if (requiresConfiguration()) {
            val validationResult = validator.validate(getSpecification(), configuration.toJson())
            if (validationResult.isNotEmpty()) {
                throw Exception(
                    String.format("Verification error(s) occurred. Errors: %s ", validationResult)
                )
            }
        }
    }

    @Throws(IOException::class)
    private fun getSpecification(): JsonNode {
        return Jsons.deserialize(MoreResources.readResource("spec.json"))
    }

    private fun requiresConfiguration(): Boolean {
        return operation.type().requiresConfiguration
    }
}
