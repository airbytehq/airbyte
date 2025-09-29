package io.airbyte.cdk.load.writer

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.load.http.HttpRequester
import io.airbyte.cdk.load.http.Response
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.DestinationRecordSource
import io.airbyte.cdk.load.writer.batch.JsonResponseBodyBuilder
import io.airbyte.cdk.load.writer.batch.ResponseBodyBuilder
import io.airbyte.cdk.load.writer.batch.size.BatchSizeStrategy
import io.airbyte.cdk.load.writer.batch.size.BatchSizeStrategyFactory
import io.airbyte.cdk.load.writer.rejected.RejectedRecordsBuilder
import io.airbyte.cdk.util.Jsons
import io.mockk.Runs
import io.mockk.every
import io.mockk.just
import io.mockk.mockk
import io.mockk.verify
import java.util.UUID
import kotlin.test.assertEquals
import kotlin.test.assertFalse
import kotlin.test.assertNull
import kotlin.test.assertTrue
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

class DeclarativeLoaderStateTest {
    lateinit var destinationRecordRaw: DestinationRecordRaw
    lateinit var httpRequester: HttpRequester
    lateinit var responseBodyBuilder: ResponseBodyBuilder
    lateinit var rejectedRecordsBuilder: RejectedRecordsBuilder
    lateinit var loaderState: DeclarativeLoaderState

    @BeforeEach
    fun setUp() {
        destinationRecordRaw = mockk()

        httpRequester = mockk()
        responseBodyBuilder = mockk()
        rejectedRecordsBuilder = mockk()
        loaderState =
            DeclarativeLoaderState(httpRequester, responseBodyBuilder, rejectedRecordsBuilder)
    }

    @Test
    internal fun `test when accumulate then pass record to response body and rejected records builder`() {
        every { responseBodyBuilder.accumulate(any()) } just Runs
        every { rejectedRecordsBuilder.accumulate(any()) } just Runs

        loaderState.accumulate(destinationRecordRaw)

        verify { responseBodyBuilder.accumulate(destinationRecordRaw) }
        verify { rejectedRecordsBuilder.accumulate(destinationRecordRaw) }
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
    internal fun `test when flush then return rejected records builder result`() {
        val rejectedRecords = listOf(mockk<DestinationRecordRaw>())
        val body = aBody()
        every { rejectedRecordsBuilder.getRejectedRecords(any()) } returns rejectedRecords
        every { httpRequester.send(body = aBody()) } returns aResponse()
        every { responseBodyBuilder.isEmpty() } returns false
        every { responseBodyBuilder.build() } returns body

        val result = loaderState.flush()

        verify(exactly = 1) { httpRequester.send(body = body) }
        assertEquals(rejectedRecords, result)
    }

    private fun aResponse(): Response {
        val response = mockk<Response>()
        every { response.statusCode } returns 1
        every { response.body } returns null
        every { response.headers } returns emptyMap()
        every { response.close() } just Runs
        return response
    }

    fun aBody(): ByteArray = byteArrayOf(1, 2, 3)
}

class NoLimitBatchSizeStrategy : BatchSizeStrategy {
    override fun isFull(): Boolean {
        return false
    }
}

class NoLimitSizeStrategyFactory : BatchSizeStrategyFactory {
    override fun create(requestBody: JsonNode, batchField: List<String>): BatchSizeStrategy {
        return NoLimitBatchSizeStrategy()
    }
}

class JsonResponseBodyBuilderTest {
    @Test
    internal fun `test given interpolation for string when build then return string`() {
        val responseBuilder =
            JsonResponseBodyBuilder(
                anySizeStrategyFactory(),
                DeclarativeBatchEntryAssembler("""{"entry_key": "{{ record["record_key"] }}" }"""),
                listOf("batch")
            )
        responseBuilder.accumulate(
            aRecord(Jsons.readTree("""{"record_key": "record_key_value"}"""))
        )

        val response = responseBuilder.build()

        val jsonResponse = Jsons.readTree(response)
        assertEquals(
            Jsons.readTree("""{"batch": [{"entry_key":"record_key_value"}]}"""),
            jsonResponse
        )
    }

    @Test
    internal fun `test given interpolation for integer when build then return integer`() {
        val responseBuilder =
            JsonResponseBodyBuilder(
                anySizeStrategyFactory(),
                DeclarativeBatchEntryAssembler("""{"entry_key": {{ record["record_key"] }} }"""),
                listOf("batch")
            )
        responseBuilder.accumulate(aRecord(Jsons.readTree("""{"record_key": "2"}""")))

        val response = responseBuilder.build()

        val jsonResponse = Jsons.readTree(response)
        assertEquals(Jsons.readTree("""{"batch": [{"entry_key":2}]}"""), jsonResponse)
    }

    @Test
    internal fun `test given batch on root level when build then return array`() {
        val responseBuilder =
            JsonResponseBodyBuilder(
                anySizeStrategyFactory(),
                anyRecordEntryAssembler(),
                emptyList()
            )
        responseBuilder.accumulate(aRecord())

        val response = responseBuilder.build()

        val jsonResponse = Jsons.readTree(response)
        assertTrue { jsonResponse.isArray }
        assertEquals(1, jsonResponse.size())
    }

    @Test
    internal fun `test given batch on nested level when build then return object with nested fields`() {
        val responseBuilder =
            JsonResponseBodyBuilder(
                anySizeStrategyFactory(),
                anyRecordEntryAssembler(),
                listOf("parent", "child")
            )
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
