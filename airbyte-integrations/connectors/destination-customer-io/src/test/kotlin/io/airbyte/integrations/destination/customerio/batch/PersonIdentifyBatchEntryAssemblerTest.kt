/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.customerio.batch

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.DestinationRecordSource
import io.airbyte.cdk.util.Jsons
import io.airbyte.integrations.destination.customerio.io.airbyte.integrations.destination.customerio.batch.PersonIdentifyBatchEntryAssembler
import io.mockk.every
import io.mockk.mockk
import java.util.UUID
import kotlin.test.assertEquals
import kotlin.test.assertFailsWith
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

class PersonIdentifyBatchEntryAssemblerTest {
    private lateinit var assembler: PersonIdentifyBatchEntryAssembler

    @BeforeEach
    fun setUp() {
        assembler = PersonIdentifyBatchEntryAssembler()
    }

    @Test
    internal fun `test given valid record with attributes when assemble then create entry properly`() {
        val entry =
            assembler.assemble(
                aRecord(
                    Jsons.objectNode()
                        .put("person_email", "person@email.com")
                        .put("an_attribute", 123)
                )
            )

        assertEquals(
            Jsons.readTree(
                """
                {
                  "type": "person",
                  "identifiers": {
                    "email": "person@email.com"
                  },
                  "action": "identify",
                  "attributes": {
                    "an_attribute": 123
                  }
                }
            """.trimIndent()
            ),
            entry
        )
    }

    @Test
    internal fun `test given person_email not provided when assemble then throw`() {
        assertFailsWith<IllegalArgumentException> {
            assembler.assemble(aRecord(Jsons.objectNode().put("event_name", "an_event_name")))
        }
    }

    fun aRecord(data: JsonNode = Jsons.objectNode()): DestinationRecordRaw {
        val rawData = mockk<DestinationRecordSource>(relaxed = true)
        every { rawData.asJsonRecord(any()) } returns data
        return DestinationRecordRaw(
            stream = mockk(relaxed = true),
            rawData = rawData,
            serializedSizeBytes = "serialized".length.toLong(),
            airbyteRawId = UUID.randomUUID()
        )
    }
}
