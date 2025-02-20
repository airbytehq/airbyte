/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task.internal

import io.airbyte.cdk.load.message.DestinationMessage
import io.airbyte.cdk.load.message.ProtocolMessageDeserializer
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import java.io.InputStream

@Singleton
class DeserializingInputSequence(
    private val deserializer: ProtocolMessageDeserializer,
    private val inputStream: InputStream,
) : Sequence<DestinationMessage> {
    private val log = KotlinLogging.logger {}
    private var index: Long = 0L

    override fun iterator(): Iterator<DestinationMessage> {
        return inputStream
            .bufferedReader()
            .lineSequence()
            .filter { it.isNotEmpty() }
            .map { line ->
                // TODO: Do the equivalent w/o locking every record
                // val estimatedSize = lineSize * config.estimatedRecordMemoryOverheadRatio
                // val reserved = memoryManager.reserve(estimatedSize.toLong(), line)

                if (++index % 10_000L == 0L) {
                    log.info { "Processed $index lines" }
                }

                deserializer.deserialize(line)
            }
            .iterator()
    }
}
