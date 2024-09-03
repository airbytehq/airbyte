/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.message

import io.airbyte.cdk.command.DestinationStream
import io.micronaut.context.annotation.Prototype
import java.util.concurrent.ConcurrentHashMap
import kotlinx.coroutines.channels.Channel

class MockQueueChannel : QueueChannel<DestinationRecordWrapped> {
    var closed = false
    var mockChannel = Channel<DestinationRecordWrapped>(Channel.UNLIMITED)

    suspend fun getMessages(): List<DestinationRecordWrapped> {
        val messages = mutableListOf<DestinationRecordWrapped>()
        while (true) {
            val message = mockChannel.tryReceive()
            if (message.isFailure) {
                break
            }
            messages.add(message.getOrNull()!!)
        }
        return messages
    }

    override suspend fun close() {
        closed = true
    }

    override suspend fun isClosed(): Boolean {
        return closed
    }

    override suspend fun send(message: DestinationRecordWrapped) {
        mockChannel.send(message)
    }

    override suspend fun receive(): DestinationRecordWrapped {
        return mockChannel.receive()
    }
}

@Prototype
class MockMessageQueue : MessageQueue<DestinationStream, DestinationRecordWrapped> {
    private val channels =
        ConcurrentHashMap<DestinationStream, QueueChannel<DestinationRecordWrapped>>()

    override suspend fun getChannel(
        key: DestinationStream
    ): QueueChannel<DestinationRecordWrapped> {
        return channels.getOrPut(key) { MockQueueChannel() }
    }

    override suspend fun acquireQueueBytesBlocking(bytes: Long) {
        TODO("Not yet implemented")
    }

    override suspend fun releaseQueueBytes(bytes: Long) {
        TODO("Not yet implemented")
    }
}
