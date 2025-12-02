/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.load.http.HttpClient
import io.airbyte.cdk.load.http.Response
import io.airbyte.cdk.load.message.DestinationRecordJsonSource
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.dlq.toDlqRecord
import io.airbyte.cdk.util.Jsons
import io.airbyte.integrations.destination.customerio.CustomerIoState
import io.airbyte.integrations.destination.customerio.io.airbyte.integrations.destination.customerio.batch.BatchEntryAssembler
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.mockk.every
import io.mockk.mockk
import io.mockk.verify
import java.io.InputStream
import java.util.UUID
import kotlin.test.assertEquals
import kotlin.test.assertFailsWith
import kotlin.test.assertNull
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

class CustomerIoStateTest {
    private lateinit var httpClient: HttpClient
    private lateinit var state: CustomerIoState

    @BeforeEach
    fun setUp() {
        httpClient = mockk()
        val entryAssembler = mockk<BatchEntryAssembler>()
        every { entryAssembler.assemble(any()) } returns Jsons.objectNode()
        state = CustomerIoState(httpClient, entryAssembler)
    }

    @Test
    internal fun `test given no records when flush then don't perform HTTP request`() {
        state.flush()
        verify(exactly = 0) { httpClient.send(any()) }
    }

    @Test
    internal fun `test given no errors when flush then no rejected records`() {
        every { httpClient.send(any()) } returns aResponse(200)
        state.accumulate(aRecord())

        val rejectedRecords = state.flush()

        assertNull(rejectedRecords)
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
            aResponse(
                207,
                """{"errors": [{"batch_index": 1, "reason": "a_reason", "field": "a_field", "message": "a_message"}]}"""
                    .toByteArray()
                    .inputStream()
            )
        state.accumulate(aRecord())
        state.accumulate(rejectedRecord)

        val rejectedRecords =
            state.flush() ?: throw IllegalStateException("Expected list with one element")

        assertEquals(
            listOf(
                rejectedRecord.toDlqRecord(
                    mapOf("reason" to "a_reason", "field" to "a_field", "message" to "a_message")
                )
            ),
            rejectedRecords
        )
    }

    @Test
    internal fun `test given unsupported return status when flush then raise`() {
        every { httpClient.send(any()) } returns aResponse(500)
        state.accumulate(aRecord())

        assertFailsWith<IllegalStateException> { state.flush() }
    }

    fun aResponse(statusCode: Int, body: InputStream = InputStream.nullInputStream()): Response {
        val response = mockk<Response>()
        every { response.statusCode } returns statusCode
        every { response.body } returns body
        every { response.close() } returns Unit
        return response
    }

    fun aRecord(data: JsonNode = Jsons.objectNode()): DestinationRecordRaw {
        val rawData =
            DestinationRecordJsonSource(
                AirbyteMessage()
                    .withType(AirbyteMessage.Type.RECORD)
                    .withRecord(
                        AirbyteRecordMessage()
                            .withStream("any_stream")
                            .withEmittedAt(0L)
                            .withData(data)
                    )
            )
        return DestinationRecordRaw(
            stream = mockk(relaxed = true),
            rawData = rawData,
            serializedSizeBytes = "serialized".length.toLong(),
            airbyteRawId = UUID.randomUUID()
        )
    }
}
