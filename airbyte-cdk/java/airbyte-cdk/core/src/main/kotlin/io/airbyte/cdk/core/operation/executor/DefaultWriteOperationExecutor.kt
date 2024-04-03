/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.core.operation.executor

import io.airbyte.cdk.core.context.env.ConnectorConfigurationPropertySource
import io.airbyte.cdk.core.operation.OperationExecutionException
import io.airbyte.cdk.core.util.ShutdownUtils
import io.airbyte.cdk.core.util.WriteStreamConsumer
import io.airbyte.cdk.integrations.base.SerializedAirbyteMessageConsumer
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Requires
import jakarta.inject.Named
import jakarta.inject.Singleton
import java.util.concurrent.TimeUnit

private val logger = KotlinLogging.logger {}

@Singleton
@Named("writeOperationExecutor")
@Requires(
    property = ConnectorConfigurationPropertySource.CONNECTOR_OPERATION,
    value = "write",
)
@Requires(env = ["destination"])
class DefaultWriteOperationExecutor(
    private val messageConsumer: SerializedAirbyteMessageConsumer,
    private val shutdownUtils: ShutdownUtils,
    private val writeStreamConsumer: WriteStreamConsumer,
) : OperationExecutor {
    override fun execute(): Result<AirbyteMessage?> {
        logger.info { "Using default write operation executor." }
        try {
            writeStreamConsumer.consumeWriteStream()
            return Result.success(null)
        } catch (e: Exception) {
            return Result.failure(
                OperationExecutionException("Failed to write output from connector.", e)
            )
        } finally {
            try {
                messageConsumer.close()
            } catch (e: Exception) {
                logger.warn(e) { "Failed to close consumer." }
            }
            shutdownUtils.stopOrphanedThreads(
                ShutdownUtils.EXIT_HOOK,
                ShutdownUtils.INTERRUPT_THREAD_DELAY_MINUTES,
                TimeUnit.MINUTES,
                ShutdownUtils.EXIT_THREAD_DELAY_MINUTES,
                TimeUnit.MINUTES,
            )
        }
    }
}
