package io.airbyte.cdk.load.discover

import io.airbyte.cdk.Operation
import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.command.ConfigurationSpecificationSupplier
import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationConfigurationFactory
import io.airbyte.cdk.output.ExceptionHandler
import io.airbyte.cdk.output.OutputConsumer
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus
import io.airbyte.protocol.models.v0.AirbyteMessage
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
            // TODO the output should come from discover
            destinationDiscoverer.discover(config)
            val successMessage =
                AirbyteMessage()
                    .withType(AirbyteMessage.Type.CONNECTION_STATUS)
                    .withConnectionStatus(
                        AirbyteConnectionStatus()
                            .withStatus(AirbyteConnectionStatus.Status.SUCCEEDED)
                    )
            outputConsumer.accept(successMessage)
        } catch (t: Throwable) {
            logger.warn(t) { "Caught throwable during CHECK" }
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
}
