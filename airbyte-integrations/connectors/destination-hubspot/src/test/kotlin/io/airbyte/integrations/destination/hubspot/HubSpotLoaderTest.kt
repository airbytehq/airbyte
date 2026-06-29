/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.hubspot

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.http.HttpClient
import io.airbyte.cdk.load.http.Request
import io.airbyte.cdk.load.http.Response
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.util.Jsons
import io.airbyte.integrations.destination.hubspot.io.airbyte.integrations.destination.hubspot.http.HubSpotObjectTypeIdMapper
import io.mockk.every
import io.mockk.mockk
import kotlin.test.assertEquals
import kotlin.test.assertNull
import kotlin.test.assertTrue
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

class HubSpotLoaderTest {
    private lateinit var httpClient: HttpClient
    private lateinit var objectDao: HubSpotObjectTypeIdMapper
    private lateinit var stream: DestinationStream
    private lateinit var state: HubSpotState

    @BeforeEach
    fun setUp() {
        httpClient = mockk()
        objectDao = mockk()
        stream = mockk(relaxed = true)

        every { stream.destinationObjectName } returns "CONTACT"
        every { stream.matchingKey } returns listOf("email")
        every { stream.schema } returns ObjectType(linkedMapOf())
        every { objectDao.fetchObjectTypeId("CONTACT") } returns "CONTACT"

        state = HubSpotState(httpClient, objectDao, stream)
    }

    private fun aResponse(statusCode: Int, body: String = "{}"): Response {
        val response = mockk<Response>()
        every { response.statusCode } returns statusCode
        every { response.body } returns body.byteInputStream()
        every { response.close() } returns Unit
        return response
    }

    private fun aRecord(): DestinationRecordRaw {
        return mockk(relaxed = true)
    }

    private fun anInput(email: String): JsonNode {
        return Jsons.objectNode().apply {
            put("idProperty", "email")
            put("id", email)
            val props = putObject("properties")
            props.put("email", email)
        }
    }

    @Test
    fun `test sendWithSplitRetry returns empty on 200`() {
        every { httpClient.send(any<Request>()) } returns aResponse(200)

        val records = listOf(aRecord())
        val inputs = listOf(anInput("test@example.com"))

        val rejected = state.sendWithSplitRetry(inputs, records)

        assertTrue(rejected.isEmpty())
    }

    @Test
    fun `test sendWithSplitRetry returns empty on 207`() {
        every { httpClient.send(any<Request>()) } returns aResponse(207)

        val records = listOf(aRecord())
        val inputs = listOf(anInput("test@example.com"))

        val rejected = state.sendWithSplitRetry(inputs, records)

        assertTrue(rejected.isEmpty())
    }

    @Test
    fun `test sendWithSplitRetry rejects single record on 409`() {
        every { httpClient.send(any<Request>()) } returns
            aResponse(409, """{"message":"Conflict","status":"error"}""")

        val record = aRecord()
        val records = listOf(record)
        val inputs = listOf(anInput("conflict@example.com"))

        val rejected = state.sendWithSplitRetry(inputs, records)

        assertEquals(1, rejected.size)
        assertEquals(record, rejected[0])
    }

    @Test
    fun `test sendWithSplitRetry splits batch on 409 and isolates bad record`() {
        val goodRecord1 = aRecord()
        val badRecord = aRecord()
        val goodRecord2 = aRecord()
        val records = listOf(goodRecord1, badRecord, goodRecord2)
        val inputs =
            listOf(
                anInput("good1@example.com"),
                anInput("bad@example.com"),
                anInput("good2@example.com")
            )

        // First call: full batch of 3 -> 409
        // Second call: first half [good1] -> 200
        // Third call: second half [bad, good2] -> 409
        // Fourth call: [bad] -> 409 (single record, rejected)
        // Fifth call: [good2] -> 200
        every { httpClient.send(any<Request>()) } returnsMany
            listOf(
                aResponse(409, """{"message":"Conflict"}"""),
                aResponse(200),
                aResponse(409, """{"message":"Conflict"}"""),
                aResponse(409, """{"message":"Conflict"}"""),
                aResponse(200)
            )

        val rejected = state.sendWithSplitRetry(inputs, records)

        assertEquals(1, rejected.size)
        assertEquals(badRecord, rejected[0])
    }

    @Test
    fun `test sendWithSplitRetry handles multiple bad records`() {
        val badRecord1 = aRecord()
        val badRecord2 = aRecord()
        val records = listOf(badRecord1, badRecord2)
        val inputs = listOf(anInput("bad1@example.com"), anInput("bad2@example.com"))

        // Full batch of 2 -> 409
        // First half [bad1] -> 409 (single, rejected)
        // Second half [bad2] -> 409 (single, rejected)
        every { httpClient.send(any<Request>()) } returnsMany
            listOf(
                aResponse(409, """{"message":"Conflict"}"""),
                aResponse(409, """{"message":"Conflict"}"""),
                aResponse(409, """{"message":"Conflict"}""")
            )

        val rejected = state.sendWithSplitRetry(inputs, records)

        assertEquals(2, rejected.size)
        assertEquals(badRecord1, rejected[0])
        assertEquals(badRecord2, rejected[1])
    }

    @Test
    fun `test sendWithSplitRetry with large batch isolates single bad record`() {
        val records = (0 until 8).map { aRecord() }
        val inputs = (0 until 8).map { anInput("user$it@example.com") }
        val badIndex = 5 // The bad record is at index 5

        // Simulate: only batches containing the bad record get 409
        // Batch [0..7] -> 409
        // Batch [0..3] -> 200 (no bad record)
        // Batch [4..7] -> 409 (contains bad record at index 5)
        // Batch [4..5] -> 409 (contains bad record)
        // Batch [4] -> 200
        // Batch [5] -> 409 (single bad record, rejected)
        // Batch [6..7] -> 200
        every { httpClient.send(any<Request>()) } returnsMany
            listOf(
                aResponse(409, """{"message":"Conflict"}"""),
                aResponse(200),
                aResponse(409, """{"message":"Conflict"}"""),
                aResponse(409, """{"message":"Conflict"}"""),
                aResponse(200),
                aResponse(409, """{"message":"Conflict"}"""),
                aResponse(200)
            )

        val rejected = state.sendWithSplitRetry(inputs, records)

        assertEquals(1, rejected.size)
        assertEquals(records[badIndex], rejected[0])
    }

    @Test
    fun `test flush returns null on empty batch`() {
        val result = state.flush()
        assertNull(result)
    }

    @Test
    fun `test throws on non-409 error`() {
        every { httpClient.send(any<Request>()) } returns
            aResponse(500, """{"message":"Internal Server Error"}""")

        val records = listOf(aRecord())
        val inputs = listOf(anInput("test@example.com"))

        org.junit.jupiter.api.assertThrows<IllegalStateException> {
            state.sendWithSplitRetry(inputs, records)
        }
    }
}
