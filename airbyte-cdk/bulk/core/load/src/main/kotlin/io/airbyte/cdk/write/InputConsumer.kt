/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.write

import io.airbyte.cdk.message.Deserializer
import io.airbyte.cdk.message.DestinationMessage
import io.airbyte.cdk.message.MessageQueueWriter
import io.github.oshai.kotlinlogging.KLogger
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton
import java.io.InputStream
import java.nio.charset.StandardCharsets
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

/** Runnable input consumer. */
interface InputConsumer<T> {
    suspend fun run()
}

/** Input consumer that deserializes and publishes to a queue. */
interface DeserializingInputStreamConsumer<T : Any> : InputConsumer<T> {
    val log: KLogger
    val inputStream: InputStream
    val deserializer: Deserializer<T>
    val messageQueue: MessageQueueWriter<T>

    override suspend fun run() =
        withContext(Dispatchers.IO) {
            val log = KotlinLogging.logger {}

            log.info { "Starting consuming messages from the input stream" }

            var index = 0L
            var bytes = 0L
            inputStream.bufferedReader(StandardCharsets.UTF_8).lineSequence().forEach { line ->
                val lineSize = line.length.toLong()
                if (lineSize > 0L) {
                    val deserialized = deserializer.deserialize(line)
                    messageQueue.publish(deserialized, lineSize)

                    bytes += lineSize
                    if (++index % 10_000L == 0L) {
                        log.info {
                            "Consumed $index messages (${bytes / 1024L}mb) from the input stream"
                        }
                    }
                }
            }

            log.info { "Finished consuming $index messages (${bytes}b) from the input stream" }
        }
}

@Singleton
class DefaultInputConsumer(
    override val inputStream: InputStream,
    override val deserializer: Deserializer<DestinationMessage>,
    override val messageQueue: MessageQueueWriter<DestinationMessage>
) : DeserializingInputStreamConsumer<DestinationMessage> {
    override val log = KotlinLogging.logger {}
}

/** Override to provide a custom input stream. */
@Factory
class InputStreamFactory {
    @Singleton
    fun make(): InputStream {
        return System.`in`
    }
}
