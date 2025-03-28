/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.check

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
@Requires(property = Operation.PROPERTY, value = "check")
@Requires(env = ["destination"])
class CheckOperation<T : ConfigurationSpecification, C : DestinationConfiguration>(
    val configJsonObjectSupplier: ConfigurationSpecificationSupplier<T>,
    val configFactory: DestinationConfigurationFactory<T, C>,
    private val destinationChecker: DestinationChecker<C>,
    private val exceptionHandler: ExceptionHandler,
    private val outputConsumer: OutputConsumer,
) : Operation {
    override fun execute() {
        try {
            val pojo = configJsonObjectSupplier.get()
            val config = configFactory.make(pojo)
            destinationChecker.check(config)
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
            val (traceMessage, statusMessage) = exceptionHandler.handleCheckFailure(t)
            outputConsumer.accept(traceMessage)
            outputConsumer.accept(statusMessage)
        } finally {
            destinationChecker.cleanup()
        }
    }
}
