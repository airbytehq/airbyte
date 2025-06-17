/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse_v2.write.direct

import com.clickhouse.client.api.Client
import com.clickhouse.client.api.data_formats.RowBinaryFormatWriter
import com.clickhouse.client.api.insert.InsertResponse
import com.clickhouse.client.api.metadata.TableSchema
import com.clickhouse.data.ClickHouseFormat
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.ArrayValue
import io.airbyte.cdk.load.data.BooleanValue
import io.airbyte.cdk.load.data.DateValue
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.NumberValue
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.TimeWithTimezoneValue
import io.airbyte.cdk.load.data.TimeWithoutTimezoneValue
import io.airbyte.cdk.load.data.TimestampWithTimezoneValue
import io.airbyte.cdk.load.data.TimestampWithoutTimezoneValue
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.cdk.load.util.serializeToString
import io.mockk.every
import io.mockk.impl.annotations.MockK
import io.mockk.junit5.MockKExtension
import io.mockk.mockk
import io.mockk.verify
import java.io.ByteArrayInputStream
import java.io.InputStream
import java.math.BigDecimal
import java.util.concurrent.CompletableFuture
import kotlin.test.assertEquals
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.extension.ExtendWith
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.Arguments
import org.junit.jupiter.params.provider.MethodSource

@ExtendWith(MockKExtension::class)
class BinaryRowInsertBufferTest {
    @MockK(relaxed = true) lateinit var schema: TableSchema

    @MockK lateinit var clickhouseClient: Client

    private val tableName =
        TableName(
            namespace = Fixtures.TEST_NAMESPACE,
            name = Fixtures.TEST_NAME,
        )

    private lateinit var buffer: BinaryRowInsertBuffer

    @BeforeEach
    fun setup() {
        every {
            clickhouseClient.getTableSchema(Fixtures.TEST_NAME, Fixtures.TEST_NAMESPACE)
        } returns schema
        buffer = BinaryRowInsertBuffer(tableName, clickhouseClient)
    }

    @Test
    fun `initializes the ch row binary writer`() {
        verify { clickhouseClient.getTableSchema(Fixtures.TEST_NAME, Fixtures.TEST_NAMESPACE) }

        assertEquals(ClickHouseFormat.RowBinary, buffer.writer.format)
    }

    @ParameterizedTest
    @MethodSource("singleValueMatrix")
    fun `#accumulate writes and commits single value fields`(record: Map<String, AirbyteValue>) {
        val writer = mockk<RowBinaryFormatWriter>(relaxed = true)
        buffer.writer = writer

        buffer.accumulate(record)

        record.forEach {
            when (it.value) {
                is NullValue -> verify { writer.setValue(it.key, null) }
                is BooleanValue ->
                    verify { writer.setValue(it.key, (it.value as BooleanValue).value) }
                is IntegerValue ->
                    verify { writer.setValue(it.key, (it.value as IntegerValue).value) }
                is NumberValue ->
                    verify { writer.setValue(it.key, (it.value as NumberValue).value) }
                is StringValue ->
                    verify { writer.setValue(it.key, (it.value as StringValue).value) }
                is DateValue -> verify { writer.setValue(it.key, (it.value as DateValue).value) }
                is TimeWithTimezoneValue ->
                    verify { writer.setValue(it.key, (it.value as TimeWithTimezoneValue).value) }
                is TimeWithoutTimezoneValue ->
                    verify { writer.setValue(it.key, (it.value as TimeWithoutTimezoneValue).value) }
                is TimestampWithTimezoneValue ->
                    verify {
                        writer.setValue(it.key, (it.value as TimestampWithTimezoneValue).value)
                    }
                is TimestampWithoutTimezoneValue ->
                    verify {
                        writer.setValue(it.key, (it.value as TimestampWithoutTimezoneValue).value)
                    }
                else -> {}
            }
        }

        verify { writer.commitRow() }
    }

    @ParameterizedTest
    @MethodSource("multiValueMatrix")
    fun `#accumulate serializes, writes and commits multi value fields`(
        record: Map<String, AirbyteValue>
    ) {
        val writer = mockk<RowBinaryFormatWriter>(relaxed = true)
        buffer.writer = writer

        buffer.accumulate(record)

        record.forEach {
            when (it.value) {
                is ObjectValue ->
                    verify {
                        writer.setValue(
                            it.key,
                            (it.value as ObjectValue).values.serializeToString()
                        )
                    }
                is ArrayValue ->
                    verify {
                        writer.setValue(it.key, (it.value as ArrayValue).values.serializeToString())
                    }
                else -> {}
            }
        }

        verify { writer.commitRow() }
    }

    @Test
    fun `flush inserts the internal buffer clickhouse`() = runTest {
        every {
            clickhouseClient.insert(any<String>(), any<InputStream>(), ClickHouseFormat.RowBinary)
        } returns CompletableFuture.completedFuture(mockk<InsertResponse>())

        val bufferedPayload = mockk<ByteArrayInputStream>()
        buffer.inner = mockk { every { toInputStream() } returns bufferedPayload }

        buffer.flush()

        verify {
            clickhouseClient.insert(
                "`${tableName.namespace}`.`${tableName.name}`",
                bufferedPayload,
                ClickHouseFormat.RowBinary
            )
        }
    }

    companion object {
        // these values wrap a `value` field
        @JvmStatic
        fun singleValueMatrix() =
            listOf(
                Arguments.of(
                    mapOf(
                        "field1" to Fixtures.booleanValue,
                        "field2" to Fixtures.integerValue,
                        "field3" to Fixtures.numberValue,
                        "field4" to Fixtures.stringValue,
                        "field5" to Fixtures.dateValue,
                        "field6" to Fixtures.timeWithTimezoneValue,
                        "field7" to Fixtures.timeWithoutTimezoneValue,
                        "field8" to Fixtures.timestampWithTimezoneValue,
                        "field9" to Fixtures.timestampWithoutTimezoneValue,
                        "field10" to Fixtures.nullValue
                    )
                ),
                Arguments.of(
                    mapOf(
                        "field1" to Fixtures.booleanValue,
                        "field2" to Fixtures.stringValue,
                        "field3" to Fixtures.timeWithTimezoneValue,
                        "field4" to Fixtures.timestampWithTimezoneValue,
                        "field5" to Fixtures.timestampWithoutTimezoneValue,
                    )
                ),
                Arguments.of(
                    mapOf(
                        "field1" to Fixtures.booleanValue,
                        "field2" to Fixtures.integerValue,
                        "field3" to Fixtures.numberValue,
                        "field4" to Fixtures.stringValue,
                        "field5" to Fixtures.stringValue,
                        "field6" to Fixtures.stringValue,
                        "field7" to Fixtures.dateValue,
                        "field8" to Fixtures.nullValue,
                    )
                ),
                Arguments.of(
                    mapOf(
                        "field1" to Fixtures.stringValue,
                        "field2" to Fixtures.stringValue,
                        "field3" to Fixtures.stringValue,
                        "field4" to Fixtures.stringValue,
                        "field5" to Fixtures.dateValue,
                    )
                ),
            )

        // these values wrap a `values` field (note: differs from above)
        @JvmStatic
        fun multiValueMatrix() =
            listOf(
                Arguments.of(
                    mapOf(
                        "field1" to Fixtures.objectValue,
                        "field2" to Fixtures.arrayValue,
                    )
                ),
                Arguments.of(
                    mapOf(
                        "field1" to Fixtures.arrayValue,
                        "field2" to Fixtures.objectValue,
                    )
                ),
                Arguments.of(
                    mapOf(
                        "field1" to Fixtures.arrayValue,
                    )
                ),
                Arguments.of(
                    mapOf(
                        "field1" to Fixtures.objectValue,
                    )
                ),
            )
    }

    object Fixtures {
        const val TEST_NAMESPACE = "test_namespace_77"
        const val TEST_NAME = "test_name66"

        val booleanValue = BooleanValue(true)
        val integerValue = IntegerValue(99)
        val numberValue = NumberValue(BigDecimal.valueOf(1000))
        val stringValue = StringValue("test")
        val dateValue = DateValue("2025-06-16")
        val timeWithTimezoneValue = TimeWithTimezoneValue("15:41:36-07:00")
        val timeWithoutTimezoneValue = TimeWithoutTimezoneValue("15:41:36")
        val timestampWithTimezoneValue = TimestampWithTimezoneValue("2025-06-16T15:41:36-07:00")
        val timestampWithoutTimezoneValue = TimestampWithoutTimezoneValue("2025-06-16T15:41:36")
        val nullValue = NullValue
        val objectValue = ObjectValue(linkedMapOf("bool" to booleanValue, "str" to stringValue))
        val arrayValue = ArrayValue(listOf(integerValue, dateValue))
    }
}
