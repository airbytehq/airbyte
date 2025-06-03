package http

import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.util.Jsons
import io.airbyte.integrations.destination.shelby.http.job.Batch
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.mockk.mockk
import java.nio.charset.StandardCharsets
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

val ANY_FIELD_TYPE: FieldType = FieldType(StringType, false)

class ShelbyBatchTest {

    private lateinit var batch: Batch
    private lateinit var schema: ObjectType

    @BeforeEach
    fun setup() {
        val properties = linkedMapOf(
            "Id" to ANY_FIELD_TYPE,
            "a_field" to ANY_FIELD_TYPE,
            "another_field" to ANY_FIELD_TYPE,
        )
        schema = ObjectType(properties)
        batch = Batch(schema)
    }

    fun record(content: ObjectNode? = null) = DestinationRecordRaw(
        stream = mockk(),
        rawData = AirbyteMessage()
            .withType(AirbyteMessage.Type.RECORD)
            .withRecord(                AirbyteRecordMessage()
                .withStream("test_stream")
                .withEmittedAt(0L)
                .withData(content ?: Jsons.objectNode())),
        schema = schema,
        serializedSizeBytes = 1,
    )

    @Test
    internal fun `test given no records when is empty then return true`() {
        Assertions.assertTrue(batch.isEmpty())
    }

    @Test
    internal fun `test given at least one record when is empty then return false`() {
        batch.add(record())
        Assertions.assertFalse(batch.isEmpty())
    }

    @Test
    internal fun `test given less records than limit when is full then return false`() {
        val batch: Batch = Batch(schema, 1_000_000)
        batch.add(record())
        Assertions.assertFalse(batch.isFull())
    }

    @Test
    internal fun `test given more records than limit when is full then return true`() {
        val batch: Batch = Batch(schema, 1)
        batch.add(record())
        Assertions.assertTrue(batch.isFull())
    }

    @Test
    internal fun `test when to request body then return csv`() {
        val batch: Batch = Batch(schema)
        batch.add(record(Jsons.objectNode().put("Id", "an_id").put("a_field", "a_field_value").put("another_field", "another_field_value")))
        Assertions.assertEquals(
            "Id,a_field,another_field\n" +
                "an_id,a_field_value,another_field_value\n",
            String(batch.toRequestBody(), StandardCharsets.UTF_8),
        )
    }
}
