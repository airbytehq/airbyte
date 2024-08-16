package io.airbyte.cdk.write

import java.util.concurrent.atomic.AtomicBoolean
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.flow.flow

class MessageQueue(
    private val consumerTimeoutMs: Long = 1000L,
    private val waitTimeMs: Long = 100L,
    private val nChannelsPerStream: Int = 1,
    private val consumerChunkSizeBytes: Long = 1_000_000L
) {
    companion object {
        val instance: MessageQueue by lazy { MessageQueue() }
    }

    // TODO: Limit the sizes of the channels
    // TODO: Initialize the channels from the catalog at start
    private val channels = mutableMapOf<Stream, Array<Channel<Pair<Long, AirbyteMessage>>>>()
    private val streamCounts = mutableMapOf<Stream, Long>()
    private val streamComplete = mutableMapOf<Stream, AtomicBoolean>()

    /**
     * Deserialize and route the message to the appropriate channel.
     *
     * NOTE: Not thread-safe! Only a single writer should publish to the queue.
     */
    suspend fun publish(serialized: String) {
        // TODO: Buffer the channel or explicitly block on size
        val message = AirbyteMessage.fromSerialized(serialized)

        when (message.type) {
            AirbyteMessageType.STREAM_COMPLETE,
            AirbyteMessageType.RECORD -> {
                val count = streamCounts[message.stream] ?: 0
                val channel = (count % nChannelsPerStream.toLong()).toInt()

                channels.getOrPut(message.stream) {
                    Array(nChannelsPerStream) { Channel(Channel.UNLIMITED) }
                }[channel].send(
                    count / nChannelsPerStream.toLong() to message
                )

                streamCounts[message.stream] = count + 1
            }
        }
    }

    /**
     * Open a flow for consuming. Consumption continues until
     *   * MAX_BYTE_SIZE_PER_STREAM is reached (from message.size)
     *   * There is no available data for timeout milliseconds
     *   * A flow can always be reopened and does not need to be closed
     */
    @OptIn(ExperimentalCoroutinesApi::class)
    suspend fun open(stream: Stream, channel: Int = 0): Flow<DestinationMessage> = flow {
        if (channel < 0 || channel >= nChannelsPerStream) {
            throw IllegalArgumentException("Invalid taskId: $channel")
        }

        if (streamComplete.getOrPut(stream) { AtomicBoolean(false) }.get()) {
            emit(DestinationMessage.EndOfStream(stream))
            return@flow
        }

        var totalBytesRead = 0L

        while (totalBytesRead < consumerChunkSizeBytes) {
            var totalWait = 0L

            while (channels[stream]?.get(channel)?.isEmpty != false) {
                if (totalWait >= consumerTimeoutMs) {
                    emit(DestinationMessage.TimeOut)
                    return@flow
                }
                delay(waitTimeMs)
                totalWait += waitTimeMs
            }
            val messageIndexed = channels[stream]?.get(channel)?.receive()
            if (messageIndexed != null) {
                val (index, message) = messageIndexed
                totalBytesRead += message.sizeBytes

                if (message.type == AirbyteMessageType.STREAM_COMPLETE) {
                    streamComplete[stream]?.set(true)
                    emit(DestinationMessage.EndOfStream(stream))
                    return@flow
                }

                emit(message.record(index))
            }
        }

        return@flow
    }

    fun isStreamComplete(stream: Stream): Boolean {
        return streamComplete[stream]?.get() ?: false
    }
}
