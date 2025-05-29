/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.check

import io.airbyte.cdk.Operation
import io.airbyte.cdk.command.ConfigurationJsonObjectBase
import io.airbyte.cdk.command.ConfigurationJsonObjectSupplier
import io.airbyte.cdk.command.DestinationConfiguration
import io.airbyte.cdk.command.DestinationConfigurationFactory
import io.airbyte.cdk.output.ExceptionHandler
import io.airbyte.cdk.output.OutputConsumer
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton

@Singleton
@Requires(property = Operation.PROPERTY, value = "check")
@Requires(env = ["destination"])
class CheckOperation<T : ConfigurationJsonObjectBase, C : DestinationConfiguration>(
    val configJsonObjectSupplier: ConfigurationJsonObjectSupplier<T>,
    val configFactory: DestinationConfigurationFactory<T, C>,
    private val destinationCheckOperation: DestinationCheckOperation<C>,
    private val exceptionHandler: ExceptionHandler,
    private val outputConsumer: OutputConsumer,
) : Operation {
    override fun execute() {
        try {
            val pojo: T = configJsonObjectSupplier.get()
            val config: C = configFactory.make(pojo)
            destinationCheckOperation.check(config)
            val successMessage =
                AirbyteMessage()
                    .withType(AirbyteMessage.Type.CONNECTION_STATUS)
                    .withConnectionStatus(
                        AirbyteConnectionStatus()
                            .withStatus(AirbyteConnectionStatus.Status.SUCCEEDED)
                    )
            outputConsumer.accept(successMessage)
        } catch (t: Throwable) {
            val (traceMessage, statusMessage) = exceptionHandler.handleCheckFailure(t)
            outputConsumer.accept(traceMessage)
            outputConsumer.accept(statusMessage)
        } finally {
            destinationCheckOperation.cleanup()
        }
    }
}
