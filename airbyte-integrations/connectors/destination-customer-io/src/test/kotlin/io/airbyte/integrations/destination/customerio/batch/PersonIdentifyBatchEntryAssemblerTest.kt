/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.customerio.batch

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.DestinationRecordSource
import io.airbyte.cdk.util.Jsons
import io.airbyte.integrations.destination.customerio.io.airbyte.integrations.destination.customerio.batch.IdentifierType
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

    @Test
    internal fun `test given id identifier type when assemble then use id identifier`() {
        val idAssembler = PersonIdentifyBatchEntryAssembler(IdentifierType.ID)
        val entry =
            idAssembler.assemble(
                aRecord(
                    Jsons.objectNode()
                        .put("person_id", "user-123")
                        .put("an_attribute", "value")
                )
            )

        assertEquals(
            Jsons.readTree(
                """
                {
                  "type": "person",
                  "identifiers": {
                    "id": "user-123"
                  },
                  "action": "identify",
                  "attributes": {
                    "an_attribute": "value"
                  }
                }
            """.trimIndent()
            ),
            entry
        )
    }

    @Test
    internal fun `test given cio_id identifier type when assemble then use cio_id identifier`() {
        val cioAssembler = PersonIdentifyBatchEntryAssembler(IdentifierType.CIO_ID)
        val entry =
            cioAssembler.assemble(
                aRecord(
                    Jsons.objectNode()
                        .put("person_cio_id", "cio-abc-123")
                        .put("an_attribute", 456)
                )
            )

        assertEquals(
            Jsons.readTree(
                """
                {
                  "type": "person",
                  "identifiers": {
                    "cio_id": "cio-abc-123"
                  },
                  "action": "identify",
                  "attributes": {
                    "an_attribute": 456
                  }
                }
            """.trimIndent()
            ),
            entry
        )
    }

    @Test
    internal fun `test given id identifier type but missing field when assemble then throw`() {
        val idAssembler = PersonIdentifyBatchEntryAssembler(IdentifierType.ID)
        assertFailsWith<IllegalArgumentException> {
            idAssembler.assemble(
                aRecord(Jsons.objectNode().put("person_email", "person@email.com"))
            )
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
