/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.input

import io.airbyte.cdk.load.file.ProtobufDataChannelReader
import io.airbyte.cdk.load.message.DestinationMessage
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.InputStream
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.FlowCollector
import kotlinx.coroutines.withContext

/**
 * Performs non-cooperative blocking IO. Does not respond directly to coroutine
 * CancellationExceptions.
 */
class ProtobufDestinationMessageInputFlow(
    private val inputStream: InputStream,
    private val reader: ProtobufDataChannelReader,
) : Flow<DestinationMessage> {
    val log = KotlinLogging.logger {}

    override suspend fun collect(
        collector: FlowCollector<DestinationMessage>,
    ) {
        var msgCount = 0L

        try {
            reader.read(inputStream).forEach { message ->
                collector.emit(message)

                if (++msgCount % 100_000 == 0L) {
                    log.info { "Processed $msgCount protobuf messages" }
                }
            }
        } finally {
            withContext(Dispatchers.IO) {
                inputStream.close()
                log.info { "Protobuf input stream closed." }
            }
        }

        log.info { "Finished reading protobuf input." }
    }
}
