/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.discover

import io.airbyte.cdk.Operation
import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.command.ConfigurationSpecificationSupplier
import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationConfigurationFactory
import io.airbyte.cdk.load.command.DestinationDiscoverCatalog
import io.airbyte.cdk.load.command.DestinationOperation
import io.airbyte.cdk.load.command.ImportType
import io.airbyte.cdk.load.command.SoftDelete
import io.airbyte.cdk.load.command.Update
import io.airbyte.cdk.load.data.json.AirbyteTypeToJsonSchema
import io.airbyte.cdk.output.ExceptionHandler
import io.airbyte.cdk.output.OutputConsumer
import io.airbyte.protocol.models.v0.DestinationCatalog as ProtocolDestinationCatalog
import io.airbyte.protocol.models.v0.DestinationOperation as ProtocolDestinationOperation
import io.airbyte.protocol.models.v0.DestinationSyncMode as ProtocolDestinationSyncMode
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton

private val logger = KotlinLogging.logger {}

@Singleton
@Requires(property = Operation.PROPERTY, value = "discover")
@Requires(env = ["destination"])
class DiscoverOperation<T : ConfigurationSpecification, C : DestinationConfiguration>(
    val configJsonObjectSupplier: ConfigurationSpecificationSupplier<T>,
    val configFactory: DestinationConfigurationFactory<T, C>,
    val destinationDiscoverer: DestinationDiscoverer<C>,
    private val exceptionHandler: ExceptionHandler,
    private val outputConsumer: OutputConsumer,
) : Operation {

    override fun execute() {
        val pojo =
            try {
                configJsonObjectSupplier.get()
            } catch (e: Exception) {
                handleException(e)
                return
            }
        val config =
            try {
                configFactory.make(pojo)
            } catch (e: Exception) {
                handleException(e)
                return
            }
        try {
            val destinationCatalog = destinationDiscoverer.discover(config)
            outputConsumer.accept(destinationCatalog.toProtocol())
        } catch (t: Throwable) {
            logger.warn(t) { "Caught throwable during DISCOVER" }
            handleException(t)
        } finally {
            destinationDiscoverer.cleanup(config)
        }
    }

    private fun handleException(t: Throwable) {
        val (traceMessage, statusMessage) = exceptionHandler.handleCheckFailure(t)
        outputConsumer.accept(traceMessage)
        outputConsumer.accept(statusMessage)
    }

    private fun DestinationDiscoverCatalog.toProtocol(): ProtocolDestinationCatalog =
        ProtocolDestinationCatalog().withOperations(operations.map { it.toProtocol() })

    private fun DestinationOperation.toProtocol(): ProtocolDestinationOperation =
        ProtocolDestinationOperation()
            .withObjectName(objectName)
            .withSyncMode(syncMode.toProtocol())
            .withJsonSchema(AirbyteTypeToJsonSchema().convert(schema))
            .withMatchingKeys(matchingKeys)

    private fun ImportType.toProtocol(): ProtocolDestinationSyncMode =
        when (this) {
            Append -> ProtocolDestinationSyncMode.APPEND
            is Dedupe -> ProtocolDestinationSyncMode.APPEND_DEDUP
            Update -> ProtocolDestinationSyncMode.UPDATE
            SoftDelete -> ProtocolDestinationSyncMode.SOFT_DELETE
            else ->
                throw IllegalArgumentException("Invalid Sync Mode for Destination Discover $this")
        }
}
