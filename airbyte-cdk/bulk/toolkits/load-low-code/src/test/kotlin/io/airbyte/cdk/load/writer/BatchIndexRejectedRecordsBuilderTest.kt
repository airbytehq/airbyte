package io.airbyte.cdk.load.writer

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.load.http.InterpolableResponse
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.dlq.toDlqRecord
import io.airbyte.cdk.load.writer.rejected.BatchIndexRejectedRecordsBuilder
import io.airbyte.cdk.util.Jsons
import io.mockk.every
import io.mockk.mockk
import io.mockk.mockkStatic
import io.mockk.unmockkStatic
import kotlin.test.assertEquals
import kotlin.test.assertFailsWith
import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test


class BatchIndexRejectedRecordsBuilderTest {

    companion object {
        val REJECTED_FIELD: String = "rejected"
        val INDEX_FIELD: String = "index"
        val A_FIELD_TO_REPORT: String = "field_to_report1"
        val ANOTHER_FIELD_TO_REPORT: String = "field_to_report2"
        val TRUE_CONDITION: String = "true"
        val FALSE_CONDITION: String = "false"
        val ANY_FIELD = listOf("any_field")
        val ANY_RESPONSE = Jsons.objectNode()
    }

    @BeforeEach
    internal fun setUp() {
        mockkStatic(DestinationRecordRaw::toDlqRecord)
    }

    @AfterEach
    internal fun tearDown() {
        unmockkStatic(DestinationRecordRaw::toDlqRecord)
    }

    @Test
    internal fun `test rejected records when isFull then return list`() {
        val rejectedRecordsBuilder = BatchIndexRejectedRecordsBuilder(
            TRUE_CONDITION,
            listOf(REJECTED_FIELD),
            listOf(INDEX_FIELD),
            listOf(listOf(A_FIELD_TO_REPORT), listOf(ANOTHER_FIELD_TO_REPORT))
        )
        rejectedRecordsBuilder.accumulate(aRecord())
        rejectedRecordsBuilder.accumulate(aRecord())

        val rejectedRecords = rejectedRecordsBuilder.getRejectedRecords(
            anInterpolableResponse(
                Jsons.readTree("""{"$REJECTED_FIELD": [{"$INDEX_FIELD": 1, "$A_FIELD_TO_REPORT": "toto", "$ANOTHER_FIELD_TO_REPORT": "tata"}]}""")
            )
        )

        assertEquals(1, rejectedRecords.size)
    }

    @Test
    internal fun `test condition not met when isFull then return empty list`() {
        val rejectedRecordsBuilder = BatchIndexRejectedRecordsBuilder(
            FALSE_CONDITION,
            ANY_FIELD,
            ANY_FIELD,
            listOf(ANY_FIELD)
        )
        rejectedRecordsBuilder.accumulate(aRecord())

        val rejectedRecords = rejectedRecordsBuilder.getRejectedRecords(anInterpolableResponse(ANY_RESPONSE))

        assertTrue(rejectedRecords.isEmpty())
    }

    @Test
    internal fun `test rejection field not found when isFull then throw`() {
        val rejectedRecordsBuilder = BatchIndexRejectedRecordsBuilder(
            TRUE_CONDITION,
            listOf(REJECTED_FIELD),
            listOf(INDEX_FIELD),
            listOf(listOf(A_FIELD_TO_REPORT), listOf(ANOTHER_FIELD_TO_REPORT))
        )
        rejectedRecordsBuilder.accumulate(aRecord())
        rejectedRecordsBuilder.accumulate(aRecord())

        assertFailsWith<IllegalArgumentException> {
            rejectedRecordsBuilder.getRejectedRecords(
                anInterpolableResponse(
                    Jsons.readTree("""{"not_rejected_field": []}""")
                )
            )
        }
    }

    @Test
    internal fun `test index field not found when isFull then return throw`() {
        val rejectedRecordsBuilder = BatchIndexRejectedRecordsBuilder(
            TRUE_CONDITION,
            listOf(REJECTED_FIELD),
            listOf(INDEX_FIELD),
            listOf(listOf(A_FIELD_TO_REPORT), listOf(ANOTHER_FIELD_TO_REPORT))
        )
        rejectedRecordsBuilder.accumulate(aRecord())

        assertFailsWith<IllegalArgumentException> {
            rejectedRecordsBuilder.getRejectedRecords(
                anInterpolableResponse(
                    Jsons.readTree("""{"$REJECTED_FIELD": [{"not_index_field": 0, "$A_FIELD_TO_REPORT": "toto", "$ANOTHER_FIELD_TO_REPORT": "tata"}]}""")
                )
            )
        }
    }

    @Test
    internal fun `test given index is higher than number of accumulated records when isFull then throw`() {
        val rejectedRecordsBuilder = BatchIndexRejectedRecordsBuilder(
            TRUE_CONDITION,
            listOf(REJECTED_FIELD),
            listOf(INDEX_FIELD),
            listOf(listOf(A_FIELD_TO_REPORT), listOf(ANOTHER_FIELD_TO_REPORT))
        )
        rejectedRecordsBuilder.accumulate(aRecord())
        rejectedRecordsBuilder.accumulate(aRecord())

        assertFailsWith<IndexOutOfBoundsException> {
            rejectedRecordsBuilder.getRejectedRecords(
                anInterpolableResponse(
                    Jsons.readTree("""{"$REJECTED_FIELD": [{"$INDEX_FIELD": 100, "$A_FIELD_TO_REPORT": "toto", "$ANOTHER_FIELD_TO_REPORT": "tata"}]}""")
                )
            )
        }
    }

    fun aRecord(): DestinationRecordRaw {
        every { any<DestinationRecordRaw>().toDlqRecord(any(), any()) } returns mockk<DestinationRecordRaw>(relaxed = true)
        return mockk<DestinationRecordRaw>()
    }

    fun anInterpolableResponse(body: JsonNode): InterpolableResponse {
        return InterpolableResponse(200, emptyMap(), body)
    }
}
