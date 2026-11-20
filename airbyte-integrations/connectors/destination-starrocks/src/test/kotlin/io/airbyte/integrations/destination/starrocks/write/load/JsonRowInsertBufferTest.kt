/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.starrocks.write.load

import com.fasterxml.jackson.databind.ObjectMapper
import com.github.luben.zstd.ZstdInputStream
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.NumberValue
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.table.CDC_DELETED_AT_COLUMN
import io.airbyte.integrations.destination.starrocks.http.StreamLoadClient
import java.math.BigDecimal
import java.math.BigInteger
import java.util.zip.GZIPInputStream
import kotlinx.coroutines.runBlocking
import okhttp3.mockwebserver.MockResponse
import okhttp3.mockwebserver.MockWebServer
import org.junit.jupiter.api.Assertions.assertArrayEquals
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.ValueSource

class JsonRowInsertBufferTest {

    private val unusedClient = StreamLoadClient("localhost", 8030, "u", "p")
    private val table = TableName("db", "orders")
    private val columns = listOf("_airbyte_raw_id", "id", "name", "amount", CDC_DELETED_AT_COLUMN)
    private val mapper = ObjectMapper()

    private fun buf(cdc: Boolean, soft: Boolean = false) =
        JsonRowInsertBuffer(
            table,
            columns,
            cdcDeleteEnabled = cdc,
            streamLoadClient = unusedClient,
            softDelete = soft
        )

    @Test
    fun `numbers are JSON strings, literal backslash-N survives, null is JSON null`() {
        val b = buf(cdc = false)
        b.accumulate(
            mapOf<String, AirbyteValue>(
                "_airbyte_raw_id" to StringValue("rid"),
                "id" to IntegerValue(BigInteger("9223372036854775807")), // BIGINT max
                "name" to
                    StringValue("\\N"), // literal backslash-N — NULL in CSV, must survive in JSON
                "amount" to NumberValue(BigDecimal("12345.678901234567890")),
                CDC_DELETED_AT_COLUMN to NullValue,
            ),
        )
        val node = mapper.readTree(b.bodySnapshot())[0]
        // integers/decimals as strings -> full precision (a JSON number would round to a double)
        assertTrue(node["id"].isTextual, "integers must be JSON strings")
        assertEquals("9223372036854775807", node["id"].asText())
        assertTrue(node["amount"].isTextual, "decimals must be JSON strings")
        assertEquals("12345.678901234567890", node["amount"].asText())
        // the literal `\N` string is preserved, not coerced to null
        assertEquals("\\N", node["name"].asText())
        assertTrue(node[CDC_DELETED_AT_COLUMN].isNull)
    }

    @Test
    fun `cdc delete adds __op 1 and soft delete keeps __op 0`() {
        val del = buf(cdc = true)
        del.accumulate(
            mapOf<String, AirbyteValue>(
                "_airbyte_raw_id" to StringValue("r"),
                CDC_DELETED_AT_COLUMN to StringValue("2026-01-01T00:00:00Z"),
            ),
        )
        assertEquals(
            1,
            mapper.readTree(del.bodySnapshot())[0][CsvRowInsertBuffer.OP_COLUMN].asInt()
        )

        val soft = buf(cdc = true, soft = true)
        soft.accumulate(
            mapOf<String, AirbyteValue>(
                "_airbyte_raw_id" to StringValue("r"),
                CDC_DELETED_AT_COLUMN to StringValue("2026-01-01T00:00:00Z"),
            ),
        )
        assertEquals(
            0,
            mapper.readTree(soft.bodySnapshot())[0][CsvRowInsertBuffer.OP_COLUMN].asInt()
        )
    }

    @Test
    fun `headers select JSON format and list columns including __op`() {
        assertEquals(
            mapOf(
                "format" to "JSON",
                "strip_outer_array" to "true",
                "columns" to "_airbyte_raw_id,id,name,amount,_ab_cdc_deleted_at,__op",
            ),
            buf(cdc = true).streamLoadHeaders(),
        )
    }

    @ParameterizedTest
    @ValueSource(strings = ["gzip", "zstd"])
    fun `compress round-trips and shrinks repetitive input`(algo: String) {
        val data = "x".repeat(2000).toByteArray()
        val c = buf(cdc = false).compress(algo, data)
        assertTrue(c.size < data.size)
        assertArrayEquals(data, decompress(algo, c))
    }

    @ParameterizedTest
    @ValueSource(strings = ["gzip", "zstd"])
    fun `compression sends a compressed body with the compression header`(algo: String) {
        val be = MockWebServer().apply { start() }
        be.enqueue(
            MockResponse()
                .setResponseCode(200)
                .setBody("""{"Status":"Success","NumberLoadedRows":1}""")
        )
        val fe = MockWebServer().apply { start() }
        fe.enqueue(
            MockResponse()
                .setResponseCode(307)
                .setHeader("Location", be.url("/api/db/orders/_stream_load").toString()),
        )
        val client =
            StreamLoadClient(
                host = fe.hostName,
                httpPort = fe.port,
                username = "root",
                password = "pw",
                expectContinue = false
            )
        val b =
            JsonRowInsertBuffer(
                table,
                columns,
                cdcDeleteEnabled = false,
                streamLoadClient = client,
                compression = algo
            )
        b.accumulate(
            mapOf<String, AirbyteValue>(
                "_airbyte_raw_id" to StringValue("rid"),
                "id" to IntegerValue(BigInteger.ONE),
                "name" to StringValue("hello"),
                "amount" to NumberValue(BigDecimal.ONE),
                CDC_DELETED_AT_COLUMN to NullValue,
            ),
        )
        runBlocking { b.flush() }

        fe.takeRequest()
        val beReq = be.takeRequest()
        assertEquals(algo, beReq.getHeader("compression"))
        val sent = beReq.body.readByteArray()
        // the body really is compressed and decompresses back to the JSON the buffer built
        val json = mapper.readTree(decompress(algo, sent))
        assertEquals("rid", json[0]["_airbyte_raw_id"].asText())
        assertEquals("1", json[0]["id"].asText())

        fe.shutdown()
        be.shutdown()
    }

    private fun decompress(algo: String, data: ByteArray): ByteArray =
        when (algo) {
            "gzip" -> GZIPInputStream(data.inputStream()).readBytes()
            "zstd" -> ZstdInputStream(data.inputStream()).readBytes()
            else -> error(algo)
        }
}
