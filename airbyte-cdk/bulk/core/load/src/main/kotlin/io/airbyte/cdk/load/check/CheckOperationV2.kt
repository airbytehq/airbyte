package io.airbyte.cdk.load.check

import io.airbyte.cdk.Operation
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
@Requires(property = "airbyte.destination.core.load.check.version", value = "v2")
@Requires(env = ["destination"])
class CheckOperationV2(
    val destinationChecker: DestinationCheckerV2,
    private val exceptionHandler: ExceptionHandler,
    private val outputConsumer: OutputConsumer,
)  : Operation {
    override fun execute() {
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
