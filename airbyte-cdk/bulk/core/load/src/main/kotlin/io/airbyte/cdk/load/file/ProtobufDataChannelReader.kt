/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.file

import com.google.protobuf.CodedInputStream
import io.airbyte.cdk.load.message.DestinationMessage
import io.airbyte.cdk.load.message.DestinationMessageFactory
import io.airbyte.protocol.protobuf.AirbyteMessage.AirbyteMessageProtobuf
import java.io.InputStream
import kotlin.NoSuchElementException

/** Performs non-cooperative blocking IO. */
class ProtobufDataChannelReader(
    private val factory: DestinationMessageFactory,
    private val bufferSize: Int = 16 * 1024,
) : DataChannelReader {

    private val parser = AirbyteMessageProtobuf.parser()

    override fun read(inputStream: InputStream): Sequence<DestinationMessage> =
        object : Sequence<DestinationMessage> {
            override fun iterator(): Iterator<DestinationMessage> =
                object : Iterator<DestinationMessage> {

                    private val cis: CodedInputStream =
                        CodedInputStream.newInstance(inputStream, bufferSize).apply {
                            enableAliasing(false)
                            setSizeLimit(Int.MAX_VALUE)
                        }

                    private var nextMsg: DestinationMessage? = fetch()

                    override fun hasNext(): Boolean = nextMsg != null

                    override fun next(): DestinationMessage {
                        val out = nextMsg ?: throw NoSuchElementException()
                        nextMsg = fetch()
                        return out
                    }

                    private fun fetch(): DestinationMessage? {
                        if (cis.isAtEnd) return null

                        val msgSize = cis.readRawVarint32()
                        require(msgSize >= 0) { "Negative length prefix ($msgSize)" }

                        val oldLimit = cis.pushLimit(msgSize)
                        val proto = parser.parseFrom(cis)
                        cis.checkLastTagWas(0)
                        cis.popLimit(oldLimit)
                        val wireSize = cis.totalBytesRead
                        cis.resetSizeCounter()

                        return factory.fromAirbyteProtobufMessage(proto, wireSize.toLong())
                    }
                }
        }
}
