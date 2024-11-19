/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg.v2.io

import io.airbyte.integrations.destination.iceberg.v2.io.BaseDeltaTaskWriter.RowDataDeltaWriter
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
import org.apache.iceberg.types.Type
import org.apache.iceberg.types.Types
import org.apache.iceberg.types.Types.IntegerType
import org.apache.iceberg.types.Types.StructType
import org.junit.jupiter.api.Test
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.EnumSource

internal class BaseDeltaTaskWriterTest {

    @ParameterizedTest
    @EnumSource(Operation::class)
    fun testDeltaWrite(operation: Operation) {
        val spec: PartitionSpec = mockk()
        val format = FileFormat.PARQUET
        val appenderFactory: FileAppenderFactory<Record> = mockk()
        val outputFileFactory: OutputFileFactory = mockk()
        val io: FileIO = mockk()
        val targetFileSize = WRITE_TARGET_FILE_SIZE_BYTES_DEFAULT
        val columns =
            mutableListOf(
                Types.NestedField.required(1, "id", Types.IntegerType.get()),
                Types.NestedField.required(2, "name", Types.StringType.get()),
                Types.NestedField.required(3, "timestamp", Types.TimestampType.withZone()),
            )
        val primaryKeyIds = setOf(1)
        val struct: StructType = mockk {
            every { asPrimitiveType() } returns IntegerType()
            every { fields() } returns columns.subList(0, 1)
            every { typeId() } returns Type.TypeID.INTEGER
        }
        val schema: Schema = mockk {
            every { aliases } returns emptyMap()
            every { asStruct() } returns struct
            every { columns() } returns columns
            every { identifierFieldIds() } returns primaryKeyIds
            every { schemaId() } returns 1
        }
        val deltaWriter: RowDataDeltaWriter = mockk {
            every { deleteKey(any()) } returns Unit
            every { write(any()) } returns Unit
        }
        val record = RecordWrapper(delegate = mockk(), operation = operation)
        val writer: BaseDeltaTaskWriter =
            object :
                BaseDeltaTaskWriter(
                    spec,
                    format,
                    appenderFactory,
                    outputFileFactory,
                    io,
                    targetFileSize,
                    schema,
                    emptySet()
                ) {
                override fun close() {}

                override fun route(row: Record): RowDataDeltaWriter {
                    return deltaWriter
                }
            }
        writer.write(record)
        when (operation) {
            Operation.DELETE -> {
                verify(exactly = 1) { deltaWriter.deleteKey(record) }
            }
            Operation.INSERT -> {
                verify(exactly = 1) { deltaWriter.write(record) }
            }
            Operation.UPDATE -> {
                verify(exactly = 1) { deltaWriter.deleteKey(record) }
                verify(exactly = 1) { deltaWriter.write(record) }
            }
        }
    }

    @Test
    fun testAppendWrite() {
        val spec: PartitionSpec = mockk()
        val format = FileFormat.PARQUET
        val appenderFactory: FileAppenderFactory<Record> = mockk()
        val outputFileFactory: OutputFileFactory = mockk()
        val io: FileIO = mockk()
        val targetFileSize = WRITE_TARGET_FILE_SIZE_BYTES_DEFAULT
        val columns =
            mutableListOf(
                Types.NestedField.required(1, "id", Types.IntegerType.get()),
                Types.NestedField.required(2, "name", Types.StringType.get()),
                Types.NestedField.required(3, "timestamp", Types.TimestampType.withZone()),
            )
        val primaryKeyIds = setOf(1)
        val struct: StructType = mockk {
            every { asPrimitiveType() } returns IntegerType()
            every { fields() } returns columns.subList(0, 1)
            every { typeId() } returns Type.TypeID.INTEGER
        }
        val schema: Schema = mockk {
            every { aliases } returns emptyMap()
            every { asStruct() } returns struct
            every { columns() } returns columns
            every { identifierFieldIds() } returns primaryKeyIds
            every { schemaId() } returns 1
        }
        val deltaWriter: RowDataDeltaWriter = mockk {
            every { deleteKey(any()) } returns Unit
            every { write(any()) } returns Unit
        }
        val record: Record = mockk()
        val writer: BaseDeltaTaskWriter =
            object :
                BaseDeltaTaskWriter(
                    spec,
                    format,
                    appenderFactory,
                    outputFileFactory,
                    io,
                    targetFileSize,
                    schema,
                    emptySet()
                ) {
                override fun close() {}

                override fun route(row: Record): RowDataDeltaWriter {
                    return deltaWriter
                }
            }
        writer.write(record)
        verify(exactly = 1) { deltaWriter.write(record) }
        verify(exactly = 0) { deltaWriter.deleteKey(record) }
    }
}
