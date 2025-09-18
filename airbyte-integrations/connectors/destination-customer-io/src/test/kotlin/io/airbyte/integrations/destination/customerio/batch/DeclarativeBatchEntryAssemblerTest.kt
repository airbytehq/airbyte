package io.airbyte.integrations.destination.customerio.batch

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.DestinationRecordSource
import io.airbyte.cdk.util.Jsons
import io.airbyte.integrations.destination.customerio.io.airbyte.integrations.destination.customerio.batch.DeclarativeBatchEntryAssembler
import io.mockk.every
import io.mockk.mockk
import java.util.UUID
import kotlin.test.assertEquals
import org.junit.jupiter.api.Test

class DeclarativeBatchEntryAssemblerTest {
    val PERSON_EVENT_TEMPLATE = """
{
  "type": "person",
  "identifiers": {
    "id": "{{ record["person_email"] }}"
  },
  "action": "identify",
  "attributes": {{ additional_properties }}
}
    """.trimIndent()

    @Test
    internal fun `test given bracket accessor on record when extract record keys then return key`() {
        val assembler = DeclarativeBatchEntryAssembler(PERSON_EVENT_TEMPLATE)
        val batchEntry = assembler.assemble(
            aRecord(
                Jsons.readTree("""
            {
              "person_email": "maxime@airbyte.io",
              "attribute1": "x",
              "attribute2": 1
            }
        """.trimIndent()
                )
            )
        )
        assertEquals(batchEntry, Jsons.readTree("""
{
  "type": "person",
  "identifiers": {
    "id": "maxime@airbyte.io"
  },
  "action": "identify",
  "attributes": {
    "attribute1": "x",
    "attribute2": 1
  }
}
    """.trimIndent()))
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
