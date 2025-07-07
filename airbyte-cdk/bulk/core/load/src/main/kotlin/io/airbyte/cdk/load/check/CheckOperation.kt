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
    val destinationChecker: DestinationChecker<C>,
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
            handleException(t)
        } finally {
            destinationChecker.cleanup(config)
        }
    }

    private fun handleException(t: Throwable) {
        val (traceMessage, statusMessage) = exceptionHandler.handleCheckFailure(t)
        outputConsumer.accept(traceMessage)
        outputConsumer.accept(statusMessage)
    }
}
