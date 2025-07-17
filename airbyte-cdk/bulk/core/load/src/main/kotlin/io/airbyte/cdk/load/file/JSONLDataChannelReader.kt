/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.file

import com.google.common.io.CountingInputStream
import io.airbyte.cdk.load.message.DestinationMessage
import io.airbyte.cdk.load.message.DestinationMessageFactory
import io.airbyte.cdk.load.util.Jsons
import io.airbyte.protocol.models.v0.AirbyteMessage
import java.io.InputStream

class JSONLDataChannelReader(private val destinationMessageFactory: DestinationMessageFactory) :
    DataChannelReader {

    override fun read(inputStream: InputStream): Sequence<DestinationMessage> {
        val countingStream = CountingInputStream(inputStream)
        val parser = Jsons.factory.createParser(countingStream)
        var lastCount = 0L

        return Jsons.readerFor(AirbyteMessage::class.java)
            .readValues<AirbyteMessage>(parser)
            .asSequence()
            .map {
                val currentCount = countingStream.count
                val serializedSize = currentCount - lastCount
                lastCount = currentCount
                // serializedSize is an approximation not actual for an individual record size
                destinationMessageFactory.fromAirbyteProtocolMessage(it, serializedSize)
            }
    }
}
