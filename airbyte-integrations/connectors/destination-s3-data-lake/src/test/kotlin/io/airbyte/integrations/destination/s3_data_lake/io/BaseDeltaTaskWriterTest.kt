/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_data_lake.io

import io.airbyte.integrations.destination.s3_data_lake.io.BaseDeltaTaskWriter.RowDataDeltaWriter
import io.mockk.every
import io.mockk.mockk
import io.mockk.verify
import org.apache.iceberg.FileFormat
import org.apache.iceberg.PartitionSpec
import org.apache.iceberg.Schema
import org.apache.iceberg.TableProperties.WRITE_TARGET_FILE_SIZE_BYTES_DEFAULT
import org.apache.iceberg.data.Record
import org.apache.iceberg.io.FileAppenderFactory
import org.apache.iceberg.io.FileIO
import org.apache.iceberg.io.OutputFileFactory
import org.apache.iceberg.types.Types
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
        val deltaWriter: RowDataDeltaWriter = mockk {
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
        val deltaWriter: RowDataDeltaWriter = mockk {
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
    ) :
        BaseDeltaTaskWriter(
            spec,
            format,
            appenderFactory,
            outputFileFactory,
            io,
            targetFileSize,
            schema,
            primaryKeyIds
        ) {
        override fun close() {}

        override fun route(row: Record): RowDataDeltaWriter {
            return deltaWriter
        }
    }
}
