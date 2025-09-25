package io.airbyte.cdk.load.writer

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.load.http.HttpRequester
import io.airbyte.cdk.load.http.Response
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.DestinationRecordSource
import io.airbyte.cdk.util.Jsons
import io.mockk.Runs
import io.mockk.every
import io.mockk.just
import io.mockk.mockk
import io.mockk.verify
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import java.util.UUID
import kotlin.test.assertEquals
import kotlin.test.assertFailsWith
import kotlin.test.assertFalse
import kotlin.test.assertNull
import kotlin.test.assertTrue


class DeclarativeLoaderStateTest {
    lateinit var destinationRecordRaw: DestinationRecordRaw
    lateinit var httpRequester: HttpRequester
    lateinit var responseBodyBuilder: ResponseBodyBuilder
    lateinit var loaderState: DeclarativeLoaderState

    companion object {
        val A_BODY = byteArrayOf(1, 2, 3)
    }

    @BeforeEach
    fun setUp() {
        destinationRecordRaw = mockk()

        httpRequester = mockk()
        responseBodyBuilder = mockk()
        loaderState = DeclarativeLoaderState(httpRequester, responseBodyBuilder)
    }

    @Test
    internal fun `test when accumulate then pass record to response body builder`() {
        every { responseBodyBuilder.accumulate(any()) } just Runs
        loaderState.accumulate(destinationRecordRaw)
        verify { responseBodyBuilder.accumulate(destinationRecordRaw) }
    }

    @Test
    internal fun `test given response body builder is full when isFull then return true`() {
        every { responseBodyBuilder.isFull() } returns true
        val result = loaderState.isFull()
        assertTrue { result }
    }

    @Test
    internal fun `test given response body builder is not full when isFull then return false`() {
        every { responseBodyBuilder.isFull() } returns false
        val result = loaderState.isFull()
        assertFalse { result }
    }

    @Test
    internal fun `test given response body builder is empty when flush then do not interact with requester and return null`() {
        every { responseBodyBuilder.isEmpty() } returns true

        val result = loaderState.flush()

        verify(exactly = 0) { httpRequester.send(any()) }
        assertNull(result)
    }

    @Test
    internal fun `test given status code is 200 when flush then return null`() {
        every { responseBodyBuilder.isEmpty() } returns false
        every { responseBodyBuilder.build() } returns A_BODY
        every { httpRequester.send(body=A_BODY) } returns aResponse(200)

        val result = loaderState.flush()

        verify(exactly = 1) { httpRequester.send(body=A_BODY) }
        assertNull(result)
    }

    @Test
    internal fun `test given status code is not 200 when flush then raise`() {
        every { responseBodyBuilder.isEmpty() } returns false
        every { responseBodyBuilder.build() } returns A_BODY
        every { httpRequester.send(body=A_BODY) } returns aResponse(500)

        assertFailsWith<IllegalStateException> { loaderState.flush() }
    }

    private fun aResponse(statusCode: Int): Response {
        val response = mockk<Response>()
        every { response.statusCode } returns statusCode
        every { response.body } returns null
        every { response.close() } just Runs
        return response
    }

}


class NoLimitBatchSizeStrategy: BatchSizeStrategy {
    override fun isFull(): Boolean {
        return false
    }
}

class NoLimitSizeStrategyFactory: BatchSizeStrategyFactory {
    override fun create(
        requestBody: JsonNode,
        batchField: List<String>
    ): BatchSizeStrategy {
        return NoLimitBatchSizeStrategy()
    }
}


class JsonResponseBodyBuilderTest {
    @Test
    internal fun `test given interpolation for string when build then return string`() {
        val responseBuilder = JsonResponseBodyBuilder(anySizeStrategyFactory(), DeclarativeBatchEntryAssembler("""{"entry_key": "{{ record["record_key"] }}" }"""), listOf("batch"))
        responseBuilder.accumulate(aRecord(Jsons.readTree("""{"record_key": "record_key_value"}""")))

        val response = responseBuilder.build()

        val jsonResponse = Jsons.readTree(response)
        assertEquals(Jsons.readTree("""{"batch": [{"entry_key":"record_key_value"}]}"""), jsonResponse)
    }

    @Test
    internal fun `test given interpolation for integer when build then return integer`() {
        val responseBuilder = JsonResponseBodyBuilder(anySizeStrategyFactory(), DeclarativeBatchEntryAssembler("""{"entry_key": {{ record["record_key"] }} }"""), listOf("batch"))
        responseBuilder.accumulate(aRecord(Jsons.readTree("""{"record_key": "2"}""")))

        val response = responseBuilder.build()

        val jsonResponse = Jsons.readTree(response)
        assertEquals(Jsons.readTree("""{"batch": [{"entry_key":2}]}"""), jsonResponse)
    }

    @Test
    internal fun `test given batch on root level when build then return array`() {
        val responseBuilder = JsonResponseBodyBuilder(anySizeStrategyFactory(), anyRecordEntryAssembler(), emptyList())
        responseBuilder.accumulate(aRecord())

        val response = responseBuilder.build()

        val jsonResponse = Jsons.readTree(response)
        assertTrue { jsonResponse.isArray }
        assertEquals(1, jsonResponse.size())
    }

    @Test
    internal fun `test given batch on nested level when build then return object with nested fields`() {
        val responseBuilder = JsonResponseBodyBuilder(anySizeStrategyFactory(), anyRecordEntryAssembler(), listOf("parent", "child"))
        responseBuilder.accumulate(aRecord())

        val response = responseBuilder.build()

        val jsonResponse = Jsons.readTree(response)
        assertTrue { jsonResponse.isObject }
        assertTrue { jsonResponse.get("parent").get("child").isArray }
        assertEquals(1, jsonResponse.get("parent").get("child").size())
    }

    fun anySizeStrategyFactory() = NoLimitSizeStrategyFactory()

    fun anyRecordEntryAssembler() = DeclarativeBatchEntryAssembler("""{"key": "value"}""")

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
