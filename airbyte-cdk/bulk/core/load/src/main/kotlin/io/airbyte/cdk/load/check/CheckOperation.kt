/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.check

import io.airbyte.cdk.Operation
import io.airbyte.cdk.output.ExceptionHandler
import io.airbyte.cdk.output.OutputConsumer
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.ApplicationContext
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton
import javax.inject.Inject

private val logger = KotlinLogging.logger {}

@Singleton
@Requires(property = Operation.PROPERTY, value = "check")
@Requires(env = ["destination"])
class CheckOperation(
    private val exceptionHandler: ExceptionHandler,
    private val outputConsumer: OutputConsumer,
) : Operation {
    @Inject
    lateinit var applicationContext: ApplicationContext

    override fun execute() {

        val destinationChecker = try {
            applicationContext.createBean(DestinationChecker::class.java) as DestinationChecker
        } catch (e: Exception) {
            handleException(e)
            return
        }

        try {
            destinationChecker.check()
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
            destinationChecker.cleanup()
        }
    }

    private fun handleException(t: Throwable) {
        val (traceMessage, statusMessage) = exceptionHandler.handleCheckFailure(t)
        outputConsumer.accept(traceMessage)
        outputConsumer.accept(statusMessage)
    }
}
