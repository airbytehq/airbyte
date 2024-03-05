/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.core.event

import io.airbyte.cdk.core.command.option.AirbyteConfiguredCatalog
import io.airbyte.cdk.core.context.env.ConnectorConfigurationPropertySource
import io.airbyte.cdk.core.operation.Operation
import io.airbyte.cdk.core.operation.OperationType
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Requires
import io.micronaut.context.annotation.Value
import io.micronaut.context.event.ApplicationEventListener
import io.micronaut.context.event.StartupEvent
import jakarta.inject.Singleton

private val logger = KotlinLogging.logger {}

/**
 * Event listener that validates the Airbyte configured catalog, if present. This listener is
 * executed on application start.
 */
@Singleton
@Requires(bean = AirbyteConfiguredCatalog::class)
@Requires(property = ConnectorConfigurationPropertySource.CONNECTOR_OPERATION)
class CatalogValidator(
    @Value("\${micronaut.application.name}") private val connectorName: String,
    @Value("\${airbyte.connector.operation}") private val operationType: String,
    private val airbyteConfiguredCatalog: AirbyteConfiguredCatalog,
    private val operations: List<Operation>,
) : ApplicationEventListener<StartupEvent> {
    companion object {
        var emptyCatalog: ConfiguredAirbyteCatalog = ConfiguredAirbyteCatalog()
    }

    override fun onApplicationEvent(event: StartupEvent) {
        if (requiresCatalog()) {
            if (emptyCatalog != airbyteConfiguredCatalog.getConfiguredCatalog()) {
                logger.info { "$connectorName connector configured catalog is valid." }
            } else {
                throw IllegalArgumentException("Configured catalog is not valid.")
            }
        }
    }

    private fun requiresCatalog(): Boolean {
        return operations
            .find { it.type() == OperationType.valueOf(operationType.uppercase()) }
            ?.type()?.requiresCatalog
            ?: false
    }
}
