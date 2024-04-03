/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.async.model

import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.AirbyteStateMessage
import io.airbyte.protocol.models.AirbyteStreamState
import io.airbyte.protocol.models.StreamDescriptor
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import java.time.Instant
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

class PartialAirbyteMessageTest {
    @Test
    internal fun testDeserializeRecord() {
        val emittedAt = Instant.now().toEpochMilli()
        val serializedRec =
            Jsons.serialize(
                AirbyteMessage()
                    .withType(AirbyteMessage.Type.RECORD)
                    .withRecord(
                        AirbyteRecordMessage()
                            .withStream("users")
                            .withNamespace("public")
                            .withEmittedAt(emittedAt)
                            .withData(Jsons.jsonNode("data")),
                    ),
            )

        val rec =
            Jsons.tryDeserialize(
                    serializedRec,
                    PartialAirbyteMessage::class.java,
                )
                .get()
        assertEquals(AirbyteMessage.Type.RECORD, rec.type)
        assertEquals("users", rec.record?.stream)
        assertEquals("public", rec.record?.namespace)
        assertEquals("\"data\"", rec.record?.data.toString())
        assertEquals(emittedAt, rec.record?.emittedAt)
    }

    @Test
    internal fun testDeserializeState() {
        val serializedState =
            Jsons.serialize(
                io.airbyte.protocol.models
                    .AirbyteMessage()
                    .withType(io.airbyte.protocol.models.AirbyteMessage.Type.STATE)
                    .withState(
                        AirbyteStateMessage()
                            .withStream(
                                AirbyteStreamState()
                                    .withStreamDescriptor(
                                        StreamDescriptor().withName("user").withNamespace("public"),
                                    )
                                    .withStreamState(Jsons.jsonNode("data")),
                            )
                            .withType(AirbyteStateMessage.AirbyteStateType.STREAM),
                    ),
            )

        val rec =
            Jsons.tryDeserialize(
                    serializedState,
                    PartialAirbyteMessage::class.java,
                )
                .get()
        assertEquals(AirbyteMessage.Type.STATE, rec.type)

        val streamDesc = rec.state?.stream?.streamDescriptor
        assertEquals("user", streamDesc?.name)
        assertEquals("public", streamDesc?.namespace)
        assertEquals(
            io.airbyte.protocol.models.v0.AirbyteStateMessage.AirbyteStateType.STREAM,
            rec.state?.type,
        )
    }

    @Test
    internal fun testGarbage() {
        val badSerialization = "messed up data"

        val rec =
            Jsons.tryDeserialize(
                badSerialization,
                PartialAirbyteMessage::class.java,
            )
        assertTrue(rec.isEmpty)
    }
}
