/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodb.read.cdc

import org.bson.BsonBinary
import org.bson.BsonDocument
import org.bson.BsonString
import org.bson.BsonTimestamp
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class MongoDbResumeTokensTest {

    /** `82` + seconds `6703D580` + increment `00000001`, then the rest of the KeyString. */
    @Test
    fun testHexDataDecodesToItsTimestamp() {
        val token = BsonDocument("_data", BsonString("826703D5800000000129295A1004"))
        Assertions.assertEquals(
            BsonTimestamp(0x6703D580, 1),
            MongoDbResumeTokens.timestamp(token),
        )
    }

    @Test
    fun testBinaryDataDecodesToItsTimestamp() {
        val bytes =
            byteArrayOf(0x82.toByte(), 0x67, 0x03, 0xD5.toByte(), 0x80.toByte(), 0, 0, 0, 7, 0x29)
        val token = BsonDocument("_data", BsonBinary(bytes))
        Assertions.assertEquals(
            BsonTimestamp(0x6703D580, 7),
            MongoDbResumeTokens.timestamp(token),
        )
    }

    @Test
    fun testMalformedTokensAreRejected() {
        for (data in listOf("", "00", "8267")) {
            Assertions.assertThrows(IllegalArgumentException::class.java) {
                MongoDbResumeTokens.timestamp(BsonDocument("_data", BsonString(data)))
            }
        }
        Assertions.assertThrows(IllegalArgumentException::class.java) {
            MongoDbResumeTokens.timestamp(BsonDocument())
        }
    }
}
