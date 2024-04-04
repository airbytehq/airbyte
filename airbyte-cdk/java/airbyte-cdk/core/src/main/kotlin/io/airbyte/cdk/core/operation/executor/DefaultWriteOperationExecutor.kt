/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.core.operation.executor

import io.airbyte.cdk.core.context.env.ConnectorConfigurationPropertySource
import io.airbyte.cdk.core.operation.OperationExecutionException
import io.airbyte.cdk.core.util.ShutdownUtils
import io.airbyte.cdk.integrations.base.SerializedAirbyteMessageConsumer
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Requires
import jakarta.inject.Named
import jakarta.inject.Singleton
import java.io.BufferedInputStream
import java.io.ByteArrayOutputStream
import java.nio.charset.StandardCharsets
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
) : OperationExecutor {
    override fun execute(): Result<AirbyteMessage?> {
        try {
            getInputStream().use { bis ->
                ByteArrayOutputStream().use { baos ->
                    consumeWriteStream(messageConsumer, bis, baos)
                }
            }
            return Result.success(null)
        } catch (e: Exception) {
            return Result.failure(OperationExecutionException("Failed to write output from connector.", e))
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

    fun getInputStream(): BufferedInputStream {
        return BufferedInputStream(System.`in`)
    }

    @Throws(Exception::class)
    fun consumeWriteStream(
        consumer: SerializedAirbyteMessageConsumer,
        bis: BufferedInputStream,
        baos: ByteArrayOutputStream,
    ) {
        consumer.start()

        val buffer = ByteArray(8192) // 8K buffer
        var bytesRead: Int
        var lastWasNewLine = false

        while ((bis.read(buffer).also { bytesRead = it }) != -1) {
            for (i in 0 until bytesRead) {
                val b = buffer[i]
                if (b == '\n'.code.toByte() || b == '\r'.code.toByte()) {
                    if (!lastWasNewLine && baos.size() > 0) {
                        consumer.accept(baos.toString(StandardCharsets.UTF_8), baos.size())
                        baos.reset()
                    }
                    lastWasNewLine = true
                } else {
                    baos.write(b.toInt())
                    lastWasNewLine = false
                }
            }
        }

        // Handle last line if there's one
        if (baos.size() > 0) {
            consumer.accept(baos.toString(StandardCharsets.UTF_8), baos.size())
        }
    }
}
