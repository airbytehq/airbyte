/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.input

import io.airbyte.cdk.load.message.DestinationMessage
import io.airbyte.cdk.load.message.ProtocolMessageDeserializer
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Named
import jakarta.inject.Singleton
import java.io.InputStream
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.FlowCollector

/** Takes bytes and emits DestinationMessages */
@Singleton
class DestinationMessageInputFlow(
    @Named("inputStream") private val inputStream: InputStream,
    private val deserializer: ProtocolMessageDeserializer,
) : Flow<DestinationMessage> {
    val log = KotlinLogging.logger {}

    override suspend fun collect(
        collector: FlowCollector<DestinationMessage>,
    ) {
        var msgCount = 0L
        var estBytes = 0L
        inputStream
            .bufferedReader()
            .lineSequence()
            .filter { it.isNotEmpty() }
            .forEach { line ->
                val message = deserializer.deserialize(line)

                collector.emit(message)

                estBytes += line.length
                if (++msgCount % 100_000 == 0L) {
                    log.info { "Processed $msgCount messages (${estBytes/1024/1024}Mb)" }
                }
            }

        log.info { "Finished processing input" }
    }
}
