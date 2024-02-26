/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.core.operation.executor

import io.airbyte.cdk.core.context.env.ConnectorConfigurationPropertySource
import io.airbyte.cdk.core.operation.OperationExecutionException
import io.airbyte.cdk.core.util.ShutdownUtils
import io.airbyte.commons.util.AutoCloseableIterator
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Requires
import jakarta.inject.Named
import jakarta.inject.Singleton
import java.util.Optional
import java.util.concurrent.TimeUnit
import java.util.function.Consumer

private val logger = KotlinLogging.logger {}

@Singleton
@Named("readOperationExecutor")
@Requires(
    property = ConnectorConfigurationPropertySource.CONNECTOR_OPERATION,
    value = "read",
)
@Requires(env = ["source"])
class DefaultReadOperationExecutor(
    private val messageIterator: Optional<AutoCloseableIterator<AirbyteMessage>>,
    @Named("outputRecordCollector") private val outputRecordCollector: Consumer<AirbyteMessage>,
    private val shutdownUtils: ShutdownUtils,
) :
    OperationExecutor {
    override fun execute(): Result<AirbyteMessage?> {
        try {
            if (messageIterator.isPresent) {
                val iterator = messageIterator.get()
                try {
                    iterator.use {
                        iterator.airbyteStream
                            .ifPresent { s: AirbyteStreamNameNamespacePair? ->
                                logger.debug { "Producing messages for stream $s..." }
                            }
                        iterator.forEachRemaining(outputRecordCollector)
                        iterator.airbyteStream
                            .ifPresent { s: AirbyteStreamNameNamespacePair? ->
                                logger.debug { "Finished producing messages for stream $s..." }
                            }
                    }
                } catch (e: Exception) {
                    return Result.failure(OperationExecutionException("Failed to read from connector.", e))
                }
            } else {
                return Result.failure(
                    OperationExecutionException(
                        "Failed to read from connector.",
                        IllegalArgumentException("Read operation supported, but message iterator does not exist."),
                    ),
                )
            }
            return Result.success(null)
        } finally {
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
