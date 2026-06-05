/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.toolkits.iceberg.parquet.io

import io.mockk.every
import io.mockk.mockk
import io.mockk.verify
import org.apache.iceberg.FileFormat
import org.apache.iceberg.PartitionSpec
import org.apache.iceberg.Schema
import org.apache.iceberg.Table
import org.apache.iceberg.TableProperties.WRITE_TARGET_FILE_SIZE_BYTES_DEFAULT
import org.apache.iceberg.data.GenericRecord
import org.apache.iceberg.data.Record
import org.apache.iceberg.io.FileAppenderFactory
import org.apache.iceberg.io.FileIO
import org.apache.iceberg.io.OutputFileFactory
import org.apache.iceberg.types.TypeUtil
import org.apache.iceberg.types.Types
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.EnumSource

internal class BaseDeltaTaskWriterTest {

    @ParameterizedTest
    @EnumSource(Operation::class)
    fun testDeltaWrite(operation: Operation) {
        val spec: PartitionSpec = mockk()
        val format = FileFormat.PARQUET
        val outputFileFactory: OutputFileFactory = mockk()
        val appenderFactory: FileAppenderFactory<Record> = mockk {
            every { newDataWriter(any(), any(), any()) } returns mockk()
        }
        val io: FileIO = mockk { every { newOutputFile(any()) } returns mockk() }
        val targetFileSize = WRITE_TARGET_FILE_SIZE_BYTES_DEFAULT
        val columns =
            mutableListOf(
                Types.NestedField.required(1, "id", Types.IntegerType.get()),
                Types.NestedField.required(2, "name", Types.StringType.get()),
                Types.NestedField.required(3, "timestamp", Types.TimestampType.withZone()),
            )
        val primaryKeyIds = setOf(1)
        val schema = Schema(columns, primaryKeyIds)
        val deltaWriter: BaseDeltaTaskWriter.RowDataDeltaWriter = mockk {
            every { deleteKey(any()) } returns Unit
            every { write(any()) } returns Unit
        }
        val record = RecordWrapper(delegate = mockk(), operation = operation)
        every { record.delegate.getField(any()) } returns mockk()
        val writer: BaseDeltaTaskWriter =
            TestDeltaWriter(
                spec = spec,
                format = format,
                appenderFactory = appenderFactory,
                outputFileFactory = outputFileFactory,
                io = io,
                targetFileSize = targetFileSize,
                schema = schema,
                primaryKeyIds = primaryKeyIds,
                deltaWriter = deltaWriter,
            )
        writer.write(record)
        when (operation) {
            Operation.DELETE -> {
                verify(exactly = 1) { deltaWriter.deleteKey(any()) }
            }
            Operation.INSERT -> {
                verify(exactly = 1) { deltaWriter.write(record) }
            }
            Operation.UPDATE -> {
                verify(exactly = 1) { deltaWriter.deleteKey(any()) }
                verify(exactly = 1) { deltaWriter.write(record) }
            }
        }
    }

    @Test
    fun testAppendWrite() {
        val spec: PartitionSpec = mockk()
        val format = FileFormat.PARQUET
        val outputFileFactory: OutputFileFactory = mockk()
        val appenderFactory: FileAppenderFactory<Record> = mockk {
            every { newDataWriter(any(), any(), any()) } returns mockk()
        }
        val io: FileIO = mockk { every { newOutputFile(any()) } returns mockk() }
        val targetFileSize = WRITE_TARGET_FILE_SIZE_BYTES_DEFAULT
        val columns =
            mutableListOf(
                Types.NestedField.required(1, "id", Types.IntegerType.get()),
                Types.NestedField.required(2, "name", Types.StringType.get()),
                Types.NestedField.required(3, "timestamp", Types.TimestampType.withZone()),
            )
        val schema = Schema(columns)
        val deltaWriter: BaseDeltaTaskWriter.RowDataDeltaWriter = mockk {
            every { deleteKey(any()) } returns Unit
            every { write(any()) } returns Unit
        }
        val record: Record = mockk()
        val writer: BaseDeltaTaskWriter =
            TestDeltaWriter(
                spec = spec,
                format = format,
                appenderFactory = appenderFactory,
                outputFileFactory = outputFileFactory,
                io = io,
                targetFileSize = targetFileSize,
                schema = schema,
                primaryKeyIds = emptySet(),
                deltaWriter = deltaWriter,
            )
        writer.write(record)
        verify(exactly = 1) { deltaWriter.write(record) }
        verify(exactly = 0) { deltaWriter.deleteKey(record) }
    }

    @Test
    fun `bloom filter skips first update delete and emits repeated update delete`() {
        val columns =
            mutableListOf(
                Types.NestedField.required(1, "id", Types.IntegerType.get()),
                Types.NestedField.required(2, "name", Types.StringType.get()),
            )
        val primaryKeyIds = setOf(1)
        val schema = Schema(columns, primaryKeyIds)
        val deltaWriter = mockDeltaWriter()
        val writer =
            testWriter(
                schema = schema,
                primaryKeyIds = primaryKeyIds,
                deltaWriter = deltaWriter,
                equalityDeleteKeyTracker = testBloomFilter(schema, primaryKeyIds),
            )

        writer.write(RecordWrapper(record(schema, 1, "first"), Operation.UPDATE))
        writer.write(RecordWrapper(record(schema, 1, "second"), Operation.UPDATE))

        verify(exactly = 1) { deltaWriter.deleteKey(any()) }
        verify(exactly = 2) { deltaWriter.write(any()) }
    }

    @Test
    fun `bloom filter skips first delete and emits repeated delete`() {
        val columns =
            mutableListOf(
                Types.NestedField.required(1, "id", Types.IntegerType.get()),
                Types.NestedField.required(2, "name", Types.StringType.get()),
            )
        val primaryKeyIds = setOf(1)
        val schema = Schema(columns, primaryKeyIds)
        val deltaWriter = mockDeltaWriter()
        val writer =
            testWriter(
                schema = schema,
                primaryKeyIds = primaryKeyIds,
                deltaWriter = deltaWriter,
                equalityDeleteKeyTracker = testBloomFilter(schema, primaryKeyIds),
            )

        writer.write(RecordWrapper(record(schema, 1, "first"), Operation.DELETE))
        writer.write(RecordWrapper(record(schema, 1, "second"), Operation.DELETE))

        verify(exactly = 1) { deltaWriter.deleteKey(any()) }
        verify(exactly = 0) { deltaWriter.write(any()) }
    }

    @Test
    fun `bloom filter distinguishes composite primary key values`() {
        val columns =
            mutableListOf(
                Types.NestedField.required(1, "first", Types.StringType.get()),
                Types.NestedField.required(2, "second", Types.StringType.get()),
            )
        val primaryKeyIds = setOf(1, 2)
        val schema = Schema(columns, primaryKeyIds)
        val deleteSchema = TypeUtil.select(schema, primaryKeyIds)
        val bloomFilter = testBloomFilter(schema, primaryKeyIds)

        assertFalse(bloomFilter.shouldDelete(record(deleteSchema, "ab", "c")))
        assertFalse(bloomFilter.shouldDelete(record(deleteSchema, "a", "bc")))
        assertTrue(bloomFilter.shouldDelete(record(deleteSchema, "ab", "c")))
    }

    private fun mockDeltaWriter(): BaseDeltaTaskWriter.RowDataDeltaWriter =
        mockk {
            every { deleteKey(any()) } returns Unit
            every { write(any()) } returns Unit
        }

    private fun testBloomFilter(
        schema: Schema,
        primaryKeyIds: Set<Int>
    ): EqualityDeleteBloomFilter =
        EqualityDeleteBloomFilter(
            streamName = "test",
            deleteSchema = TypeUtil.select(schema, primaryKeyIds),
            expectedItems = 100,
            numberOfBits = 1024,
            numberOfHashFunctions = 3,
            logIntervalRecords = 0,
        )

    private fun record(schema: Schema, id: Int, name: String): GenericRecord {
        val record = GenericRecord.create(schema)
        record.setField("id", id)
        record.setField("name", name)
        return record
    }

    private fun record(schema: Schema, first: String, second: String): GenericRecord {
        val record = GenericRecord.create(schema)
        record.setField("first", first)
        record.setField("second", second)
        return record
    }

    private fun testWriter(
        schema: Schema,
        primaryKeyIds: Set<Int>,
        deltaWriter: BaseDeltaTaskWriter.RowDataDeltaWriter,
        equalityDeleteKeyTracker: EqualityDeleteKeyTracker?,
    ): BaseDeltaTaskWriter {
        val spec: PartitionSpec = mockk()
        val outputFileFactory: OutputFileFactory = mockk()
        val appenderFactory: FileAppenderFactory<Record> = mockk {
            every { newDataWriter(any(), any(), any()) } returns mockk()
        }
        val io: FileIO = mockk { every { newOutputFile(any()) } returns mockk() }
        return TestDeltaWriter(
            spec = spec,
            format = FileFormat.PARQUET,
            appenderFactory = appenderFactory,
            outputFileFactory = outputFileFactory,
            io = io,
            targetFileSize = WRITE_TARGET_FILE_SIZE_BYTES_DEFAULT,
            schema = schema,
            primaryKeyIds = primaryKeyIds,
            deltaWriter = deltaWriter,
            equalityDeleteKeyTracker = equalityDeleteKeyTracker,
        )
    }

    private class TestDeltaWriter(
        spec: PartitionSpec,
        format: FileFormat,
        appenderFactory: FileAppenderFactory<Record>,
        outputFileFactory: OutputFileFactory,
        io: FileIO,
        targetFileSize: Long,
        schema: Schema,
        primaryKeyIds: Set<Int>,
        val deltaWriter: RowDataDeltaWriter,
        equalityDeleteKeyTracker: EqualityDeleteKeyTracker? = null,
    ) :
        BaseDeltaTaskWriter(
            mockk<Table>(),
            spec,
            format,
            appenderFactory,
            outputFileFactory,
            io,
            targetFileSize,
            schema,
            primaryKeyIds,
            equalityDeleteKeyTracker,
        ) {
        override fun close() {}

        override fun route(row: Record): RowDataDeltaWriter {
            return deltaWriter
        }
    }
}
