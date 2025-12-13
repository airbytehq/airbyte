/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.check

import io.airbyte.cdk.Operation
import io.airbyte.cdk.output.OutputConsumer
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.github.oshai.kotlinlogging.KotlinLogging

private val logger = KotlinLogging.logger {}

class CheckOperationV2(
    val destinationChecker: DestinationCheckerV2,
    private val outputConsumer: OutputConsumer,
) : Operation {
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
            throw t
        } finally {
            destinationChecker.cleanup()
        }
    }
}
