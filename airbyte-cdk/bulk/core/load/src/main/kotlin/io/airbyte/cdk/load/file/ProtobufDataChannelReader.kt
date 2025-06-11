/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.file

import com.google.common.io.CountingInputStream
import io.airbyte.cdk.load.message.DestinationMessage
import io.airbyte.cdk.load.message.DestinationMessageFactory
import io.airbyte.protocol.protobuf.AirbyteMessage.AirbyteMessageProtobuf
import java.io.InputStream

/**
 * Parses a stream of size-prefixed protobuf messages, yielding a sequence of sized
 * [DestinationMessage]'s.
 */
class ProtobufDataChannelReader(private val destinationMessageFactory: DestinationMessageFactory) :
    DataChannelReader {
    private val parser = AirbyteMessageProtobuf.parser()
    override fun read(inputStream: InputStream): Sequence<DestinationMessage> = sequence {
        val countingInputStream = CountingInputStream(inputStream)
        var count = countingInputStream.count
        while (true) {
            val protoMessage = parser.parseDelimitedFrom(countingInputStream) ?: break
            val newCount = countingInputStream.count
            val serializedSizeBytes = newCount - count
            count = newCount
            yield(
                destinationMessageFactory.fromAirbyteProtobufMessage(
                    protoMessage,
                    serializedSizeBytes
                )
            )
        }
    }
}
