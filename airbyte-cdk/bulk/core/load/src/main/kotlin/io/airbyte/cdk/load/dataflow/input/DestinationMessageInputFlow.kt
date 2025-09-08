/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.input

import io.airbyte.cdk.load.message.DestinationMessage
import io.airbyte.cdk.load.message.ProtocolMessageDeserializer
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.InputStream
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.FlowCollector
import kotlinx.coroutines.withContext

/** Takes bytes and emits DestinationMessages */
class DestinationMessageInputFlow(
    private val inputStream: InputStream,
    private val deserializer: ProtocolMessageDeserializer,
) : Flow<DestinationMessage> {
    val log = KotlinLogging.logger {}

    override suspend fun collect(
        collector: FlowCollector<DestinationMessage>,
    ) {
        var msgCount = 0L
        var estBytes = 0L

        val reader = inputStream.bufferedReader()
        try {
            reader
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
        } finally {
            withContext(Dispatchers.IO) {
                reader.close()
                log.info { "Input stream reader closed." }
            }
        }

        log.info { "Finished reading input." }
    }
}
