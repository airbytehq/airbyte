package io.airbyte.cdk.load.file

import io.airbyte.cdk.load.message.DestinationMessage
import java.io.InputStream

interface DataChannelReader {
    fun read(inputStream: InputStream): Sequence<DestinationMessage>
}
