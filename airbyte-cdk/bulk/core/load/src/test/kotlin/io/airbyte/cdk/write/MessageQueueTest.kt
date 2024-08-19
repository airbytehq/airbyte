package io.airbyte.cdk.write

import com.fasterxml.jackson.databind.ObjectMapper
import kotlinx.coroutines.launch
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Test

class MessageQueueTest {
    @Test
    fun testQueue() = runTest {
        val queue = MessageQueue.instance

        launch {
            listOf(
                AirbyteMessage(Stream("test1"), AirbyteMessageType.RECORD),
                AirbyteMessage(Stream("test2"), AirbyteMessageType.RECORD),
                AirbyteMessage(Stream("test1"), AirbyteMessageType.RECORD),
                AirbyteMessage(Stream("test1"), AirbyteMessageType.STREAM_COMPLETE),
                AirbyteMessage(Stream("test2"), AirbyteMessageType.RECORD),
                AirbyteMessage(Stream("test2"), AirbyteMessageType.RECORD),
                AirbyteMessage(Stream("test2"), AirbyteMessageType.STREAM_COMPLETE)
            ).map { ObjectMapper().writeValueAsString(it) }
                .forEach { queue.publish(it) }
        }

        launch {
            queue.open(Stream("test1"), 0).collect { record ->
                when (record) {
                    is DestinationMessage.DestinationRecord -> {
                        println("test1: received record: $record")
                    }
                    is DestinationMessage.EndOfStream -> {
                        println("test1: received end of stream: $record")
                        return@collect
                    }
                    null -> {
                        println("test1: null")
                        return@collect
                    }
                }
            }
            println("test1: completed")
        }

        launch {
            queue.open(Stream("test2"), 0).collect { record ->
                when (record) {
                    is DestinationMessage.DestinationRecord -> {
                        println("test2: received record: $record")
                    }
                    is DestinationMessage.EndOfStream -> {
                        println("test2: received end of stream: $record")
                        return@collect
                    }
                    null -> {
                        println("test2: null")
                        return@collect
                    }
                }
            }
            println("test2: completed")
        }
    }
}
