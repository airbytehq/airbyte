/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodb.read.cdc

import java.nio.ByteBuffer
import org.bson.BsonDocument
import org.bson.BsonTimestamp
import org.bson.BsonValue

/**
 * Reads the oplog time out of a change-stream resume token. `_data` is the server's KeyString
 * encoding of the token, whose first field is the cluster time: one type byte (`0x82`, timestamp)
 * followed by big-endian seconds and increment. Same decoding as Debezium's
 * `ResumeTokens.getTimestamp`.
 */
object MongoDbResumeTokens {
    private const val DATA = "_data"
    private const val KEYSTRING_TIMESTAMP: Byte = 0x82.toByte()

    fun timestamp(token: BsonDocument): BsonTimestamp {
        val data: BsonValue =
            token[DATA] ?: throw IllegalArgumentException("resume token without $DATA: $token")
        val bytes: ByteArray =
            when {
                data.isString -> hexToBytes(data.asString().value)
                data.isBinary -> data.asBinary().data
                else -> throw IllegalArgumentException("unexpected $DATA type ${data.bsonType}")
            }
        require(bytes.size >= 9 && bytes[0] == KEYSTRING_TIMESTAMP) {
            "resume token does not start with a KeyString timestamp: $token"
        }
        val buffer: ByteBuffer = ByteBuffer.wrap(bytes, 1, 8)
        return BsonTimestamp(buffer.int, buffer.int)
    }

    private fun hexToBytes(hex: String): ByteArray {
        require(hex.length % 2 == 0) { "odd-length hex: $hex" }
        return ByteArray(hex.length / 2) { i -> hex.substring(2 * i, 2 * i + 2).toInt(16).toByte() }
    }
}
