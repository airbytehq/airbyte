/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.file

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.message.DestinationMessage
import io.airbyte.cdk.load.message.DestinationMessageFactory
import io.airbyte.cdk.load.util.Jsons
import io.airbyte.protocol.models.v0.AirbyteMessage
import java.io.InputStream

class JSONLDataChannelReader(catalog: DestinationCatalog) : DataChannelReader {
    // NOTE: Presumes that legacy file transfer is not compatible with sockets.
    private val destinationMessageFactory: DestinationMessageFactory =
        DestinationMessageFactory(catalog, fileTransferEnabled = false)
    private var bytesRead: Long = 0

    override fun read(inputStream: InputStream): Sequence<DestinationMessage> {
        val parser = Jsons.factory.createParser(inputStream)
        return Jsons.readerFor(AirbyteMessage::class.java)
            .readValues<AirbyteMessage>(parser)
            .asSequence()
            .map {
                val serializedSize = parser.currentLocation().byteOffset - bytesRead
                bytesRead += serializedSize
                destinationMessageFactory.fromAirbyteMessage(it, serializedSize)
            }
    }
}
