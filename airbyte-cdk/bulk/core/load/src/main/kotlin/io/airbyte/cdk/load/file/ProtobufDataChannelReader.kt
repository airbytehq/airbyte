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

class ProtobufDataChannelReader(
    private val factory: DestinationMessageFactory,
    private val bufferSize: Int = 16 * 1024,
    private val sizeLimit: Int = 256 * 1024 * 1024,
) : DataChannelReader {

    private val parser = AirbyteMessageProtobuf.parser()

    override fun read(inputStream: InputStream): Sequence<DestinationMessage> =
        object : Sequence<DestinationMessage> {
            override fun iterator(): Iterator<DestinationMessage> =
                object : Iterator<DestinationMessage> {

                    /** One buffered reader for the whole stream. */
                    private val cis: CodedInputStream =
                        CodedInputStream.newInstance(inputStream, bufferSize).apply {
                            enableAliasing(true)
//                            setSizeLimit(sizeLimit)
                        }

                    /** Stash for look-ahead. */
                    private var nextMsg: DestinationMessage? = fetch()

                    override fun hasNext(): Boolean = nextMsg != null

                    override fun next(): DestinationMessage {
                        val out = nextMsg ?: throw NoSuchElementException()
                        nextMsg = fetch()
                        return out
                    }

                    /** Reads one message or returns null if stream is exhausted. */
                    private fun fetch(): DestinationMessage? {
                        if (cis.isAtEnd) return null

                        val bytesBefore = cis.totalBytesRead
                        val msgSize = cis.readRawVarint32()

                        require(msgSize >= 0) { // catch bad prefixes early
                            "Negative length prefix ($msgSize) at byte $bytesBefore"
                        }

                        val oldLimit = cis.pushLimit(msgSize)

                        val proto = parser.parseFrom(cis)
                        cis.checkLastTagWas(0) // message done
                        cis.popLimit(oldLimit)

                        val wireSize = cis.totalBytesRead - bytesBefore
                        return factory.fromAirbyteProtobufMessage(proto, wireSize.toLong())
                    }
                }
        }
}
