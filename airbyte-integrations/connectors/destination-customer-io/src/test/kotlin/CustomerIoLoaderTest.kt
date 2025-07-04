/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.load.http.HttpClient
import io.airbyte.cdk.load.http.Response
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.DestinationRecordSource
import io.airbyte.cdk.util.Jsons
import io.airbyte.integrations.destination.customerio.CustomerIoState
import io.mockk.every
import io.mockk.mockk
import io.mockk.verify
import java.io.InputStream
import java.util.UUID
import kotlin.test.assertEquals
import kotlin.test.assertFailsWith
import kotlin.test.assertTrue
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

class CustomerIoStateTest {
    private lateinit var httpClient: HttpClient
    private lateinit var state: CustomerIoState

    @BeforeEach
    fun setUp() {
        httpClient = mockk()
        state = CustomerIoState(httpClient)
    }

    @Test
    internal fun `test given no records when flush then don't perform HTTP request`() {
        state.flush()
        verify(exactly = 0) { httpClient.send(any()) }
    }

    @Test
    internal fun `test given invalid input record when flush then raise error`() {
        assertFailsWith<IllegalArgumentException> {
            state.accumulate(
                aRecord(
                    Jsons.objectNode().put("event_name", "an_event_name") // missing person_email
                )
            )
        }
    }

    @Test
    internal fun `test given no errors when flush then no rejected records`() {
        every { httpClient.send(any()) } returns aResponse(200)
        state.accumulate(anyValidRecord())

        val rejectedRecords = state.flush() ?: throw IllegalStateException("Expected empty list")

        assertTrue { rejectedRecords.isEmpty() }
    }

    @Test
    internal fun `test given errors when flush then return rejected records`() {
        val rejectedRecord =
            aRecord(
                Jsons.objectNode()
                    .put("person_email", "rejected_person_email")
                    .put("event_name", "rejected_event_name")
            )
        every { httpClient.send(any()) } returns
            aResponse(207, """{"errors": [{"batch_index": 1}]}""".toByteArray().inputStream())
        state.accumulate(anyValidRecord())
        state.accumulate(rejectedRecord)

        val rejectedRecords = state.flush() ?: throw IllegalStateException("Expected empty list")

        assertEquals(listOf<DestinationRecordRaw>(rejectedRecord), rejectedRecords)
    }

    @Test
    internal fun `test given unsupported return status when flush then raise`() {
        every { httpClient.send(any()) } returns aResponse(500)
        state.accumulate(anyValidRecord())

        assertFailsWith<IllegalStateException> { state.flush() }
    }

    fun aResponse(statusCode: Int, body: InputStream = InputStream.nullInputStream()): Response {
        val response = mockk<Response>()
        every { response.statusCode } returns statusCode
        every { response.body } returns body
        every { response.close() } returns Unit
        return response
    }

    fun aRecord(data: JsonNode): DestinationRecordRaw {
        val rawData = mockk<DestinationRecordSource>(relaxed = true)
        every { rawData.asJsonRecord(any()) } returns data
        return DestinationRecordRaw(
            stream = mockk(relaxed = true),
            rawData = rawData,
            serializedSizeBytes = "serialized".length.toLong(),
            airbyteRawId = UUID.randomUUID()
        )
    }

    private fun anyValidRecord(): DestinationRecordRaw =
        aRecord(
            Jsons.objectNode()
                .put("person_email", "a_person_email")
                .put("event_name", "an_event_name"),
        )
}
