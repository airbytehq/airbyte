/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.core.util

import io.airbyte.cdk.core.context.env.ConnectorConfigurationPropertySource
import io.airbyte.cdk.integrations.base.SerializedAirbyteMessageConsumer
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Requires
import jakarta.inject.Named
import jakarta.inject.Singleton
import java.io.InputStream
import java.nio.charset.StandardCharsets

private val logger = KotlinLogging.logger {}

@Singleton
@Named("writeOperationExecutor")
@Requires(
    property = ConnectorConfigurationPropertySource.CONNECTOR_OPERATION,
    value = "write",
)
@Requires(env = ["destination"])
class WriteStreamConsumer(private val consumer: SerializedAirbyteMessageConsumer) {

    fun consumeWriteStream(inputStream: InputStream = System.`in`) {
        logger.info { "Starting buffered read of input stream" }
        consumer.start()
        inputStream.bufferedReader(StandardCharsets.UTF_8).use {
            var emptyLines = 0
            it.lines().forEach { line: String ->
                if (line.isNotEmpty()) {
                    consumer.accept(line, line.toByteArray(StandardCharsets.UTF_8).size)
                } else {
                    emptyLines++
                    // We've occasionally seen this loop not exit
                    // maybe it's because we keep getting streams of empty lines?
                    // TODO: Monitor the logs for occurrences of this log line and if this isn't
                    // an issue, remove it.
                    if (emptyLines % 1_000 == 0 && emptyLines < 10_000) {
                        logger.warn { "Encountered $emptyLines empty lines during execution" }
                    }
                }
            }
            if (emptyLines > 0) {
                logger.warn { "Encountered $emptyLines empty lines in the input stream." }
            }
        }
        logger.info { "Finished buffered read of input stream" }
    }
}
