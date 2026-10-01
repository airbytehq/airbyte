/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_data_lake.dataflow

import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.NamespaceMapper
import io.airbyte.cdk.load.config.NamespaceDefinitionType
import io.airbyte.cdk.load.data.BooleanType
import io.airbyte.cdk.load.data.DateType
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.NumberType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.TimestampTypeWithTimezone
import io.airbyte.cdk.load.data.TimestampTypeWithoutTimezone
import io.airbyte.cdk.load.data.iceberg.parquet.toIcebergSchema
import io.airbyte.cdk.load.data.withAirbyteMeta
import io.airbyte.cdk.load.message.ArrowBatchDTO
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.schema.model.ColumnSchema
import io.airbyte.cdk.load.schema.model.StreamTableSchema
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.schema.model.TableNames
import java.math.BigDecimal
import java.nio.charset.StandardCharsets
import java.nio.file.Path
import java.time.Instant
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.OffsetDateTime
import java.time.ZoneOffset
import java.util.UUID
import org.apache.arrow.memory.RootAllocator
import org.apache.arrow.vector.BigIntVector
import org.apache.arrow.vector.BitVector
import org.apache.arrow.vector.DateDayVector
import org.apache.arrow.vector.DecimalVector
import org.apache.arrow.vector.Float8Vector
import org.apache.arrow.vector.LargeVarCharVector
import org.apache.arrow.vector.TimeStampMicroTZVector
import org.apache.arrow.vector.TimeStampMicroVector
import org.apache.arrow.vector.VarCharVector
import org.apache.arrow.vector.VectorSchemaRoot
import org.apache.arrow.vector.types.FloatingPointPrecision
import org.apache.arrow.vector.types.TimeUnit
import org.apache.arrow.vector.types.pojo.ArrowType
import org.apache.arrow.vector.types.pojo.Field
import org.apache.arrow.vector.types.pojo.FieldType as ArrowFieldType
import org.apache.arrow.vector.types.pojo.Schema as ArrowSchema
import org.apache.hadoop.conf.Configuration
import org.apache.iceberg.FileFormat
import org.apache.iceberg.PartitionSpec
import org.apache.iceberg.SortOrder
import org.apache.iceberg.data.IcebergGenerics
import org.apache.iceberg.hadoop.HadoopTables
import org.apache.parquet.hadoop.ParquetFileReader
import org.apache.parquet.hadoop.util.HadoopInputFile
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNotNull
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.io.TempDir

internal class ArrowBatchParquetWriterTest {
    @TempDir lateinit var tempDir: Path

    @Test
    fun `writes all supported Arrow columns and metadata to Iceberg`() {
        val decimals =
            listOf(
                BigDecimal("0.000000000"),
                BigDecimal("-2.000000000"),
                BigDecimal("99999999999999999999999999999.999999999"),
                BigDecimal("9007199254740993.000000000"),
                BigDecimal("0.100000000"),
                BigDecimal("1.005000000"),
                null,
            )
        val emittedAtMs = 1_720_000_000_123L
        val inputSchema =
            ObjectType(
                linkedMapOf(
                    "source_bigint" to FieldType(IntegerType, nullable = true),
                    "varchar" to FieldType(StringType, nullable = true),
                    "large_varchar" to FieldType(StringType, nullable = true),
                    "float8" to FieldType(NumberType, nullable = true),
                    "decimal" to FieldType(NumberType, nullable = true),
                    "bit" to FieldType(BooleanType, nullable = true),
                    "date" to FieldType(DateType, nullable = true),
                    "timestamp" to FieldType(TimestampTypeWithoutTimezone, nullable = true),
                    "timestamp_tz" to FieldType(TimestampTypeWithTimezone, nullable = true),
                ),
            )
        val inputToFinalNames =
            inputSchema.properties.keys.associateWith {
                if (it == "source_bigint") "bigint" else it
            }
        val finalSchema =
            ObjectType(
                LinkedHashMap(inputSchema.properties).apply {
                    remove("source_bigint")
                    put("bigint", inputSchema.properties.getValue("source_bigint"))
                },
            )
        val stream =
            DestinationStream(
                unmappedNamespace = "test_namespace",
                unmappedName = "test_stream",
                generationId = 73,
                minimumGenerationId = 0,
                syncId = 92,
                namespaceMapper =
                    NamespaceMapper(namespaceDefinitionType = NamespaceDefinitionType.SOURCE),
                tableSchema =
                    StreamTableSchema(
                        tableNames =
                            TableNames(finalTableName = TableName("test_namespace", "test_stream")),
                        columnSchema =
                            ColumnSchema(
                                inputSchema = inputSchema.properties,
                                inputToFinalColumnNames = inputToFinalNames,
                                finalSchema = emptyMap(),
                            ),
                        importType = Append,
                    ),
            )
        val icebergSchema = finalSchema.withAirbyteMeta(flatten = true).toIcebergSchema(emptyList())
        val table =
            HadoopTables(Configuration())
                .create(
                    icebergSchema,
                    PartitionSpec.unpartitioned(),
                    SortOrder.unsorted(),
                    emptyMap(),
                    tempDir.resolve("table").toUri().toString(),
                )

        RootAllocator(Long.MAX_VALUE).use { allocator ->
            val root = VectorSchemaRoot.create(arrowSchema(), allocator)
            root.allocateNew()
            val rowCount = decimals.size
            (root.getVector("source_bigint") as BigIntVector).apply {
                for (row in 0 until rowCount - 1) setSafe(row, row.toLong() + 10)
                setNull(rowCount - 1)
            }
            (root.getVector("varchar") as VarCharVector).apply {
                for (row in 0 until rowCount - 1) {
                    setSafe(row, "value-$row".toByteArray(StandardCharsets.UTF_8))
                }
                setNull(rowCount - 1)
            }
            (root.getVector("large_varchar") as LargeVarCharVector).apply {
                for (row in 0 until rowCount - 1) {
                    setSafe(row, "large-value-$row".toByteArray(StandardCharsets.UTF_8))
                }
                setNull(rowCount - 1)
            }
            (root.getVector("float8") as Float8Vector).apply {
                for (row in 0 until rowCount - 1) setSafe(row, row + 0.25)
                setNull(rowCount - 1)
            }
            (root.getVector("decimal") as DecimalVector).apply {
                decimals.forEachIndexed { row, value ->
                    if (value == null) setNull(row) else setSafe(row, value)
                }
            }
            (root.getVector("bit") as BitVector).apply {
                for (row in 0 until rowCount - 1) setSafe(row, row % 2)
                setNull(rowCount - 1)
            }
            (root.getVector("date") as DateDayVector).apply {
                for (row in 0 until rowCount - 1) setSafe(row, 19_000 + row)
                setNull(rowCount - 1)
            }
            (root.getVector("timestamp") as TimeStampMicroVector).apply {
                for (row in 0 until rowCount - 1) setSafe(row, 1_720_000_000_000_000L + row)
                setNull(rowCount - 1)
            }
            (root.getVector("timestamp_tz") as TimeStampMicroTZVector).apply {
                for (row in 0 until rowCount - 1) setSafe(row, 1_720_000_000_000_000L + row)
                setNull(rowCount - 1)
            }
            root.rowCount = rowCount

            val generationIdSuffix = "ab-generation-id-${stream.generationId}-e"
            val writer = ArrowBatchFileWriter(table, stream, generationIdSuffix)
            writer.write(
                ArrowBatchDTO(
                    root = root,
                    partitionKey = io.airbyte.cdk.load.dataflow.state.PartitionKey("partition"),
                    rowCount = rowCount,
                    sizeBytes = 0,
                    emittedAtMs = emittedAtMs,
                ),
            )
            root.close()
            val dataFiles = writer.complete()
            assertEquals(1, dataFiles.size)
            assertEquals(FileFormat.PARQUET, dataFiles.single().format())
            assertTrue(dataFiles.all { it.location().contains(generationIdSuffix) })
            table.newAppend().appendFile(dataFiles.single()).commit()

            IcebergGenerics.read(table).build().use { records ->
                val readBack = records.toList()
                assertEquals(rowCount, readBack.size)
                readBack.take(rowCount - 1).forEachIndexed { row, record ->
                    assertEquals(row.toLong() + 10, record.getField("bigint"))
                    assertEquals("value-$row", record.getField("varchar"))
                    assertEquals("large-value-$row", record.getField("large_varchar"))
                    assertEquals(row + 0.25, record.getField("float8"))
                    assertEquals(row % 2 == 1, record.getField("bit"))
                    assertEquals(LocalDate.ofEpochDay(19_000L + row), record.getField("date"))

                    val timestampMicros = 1_720_000_000_000_000L + row
                    assertEquals(
                        LocalDateTime.ofInstant(
                            Instant.ofEpochSecond(
                                timestampMicros / 1_000_000,
                                (timestampMicros % 1_000_000) * 1_000,
                            ),
                            ZoneOffset.UTC,
                        ),
                        record.getField("timestamp"),
                    )
                    assertEquals(
                        OffsetDateTime.ofInstant(
                            Instant.ofEpochSecond(
                                timestampMicros / 1_000_000,
                                (timestampMicros % 1_000_000) * 1_000,
                            ),
                            ZoneOffset.UTC,
                        ),
                        record.getField("timestamp_tz"),
                    )
                    assertEquals(
                        java.lang.Double.doubleToLongBits(decimals[row]!!.toDouble()),
                        java.lang.Double.doubleToLongBits(record.getField("decimal") as Double),
                    )

                    assertTrue(
                        UUID.fromString(record.getField(Meta.COLUMN_NAME_AB_RAW_ID).toString())
                            .version() == 7
                    )
                    assertEquals(emittedAtMs, record.getField(Meta.COLUMN_NAME_AB_EXTRACTED_AT))
                    assertEquals(
                        stream.generationId,
                        record.getField(Meta.COLUMN_NAME_AB_GENERATION_ID)
                    )
                    val metadata =
                        record.getField(Meta.COLUMN_NAME_AB_META) as org.apache.iceberg.data.Record
                    assertEquals(stream.syncId, metadata.getField(Meta.AIRBYTE_META_SYNC_ID))
                    assertTrue((metadata.getField(Meta.AIRBYTE_META_CHANGES) as List<*>).isEmpty())
                }
                val nullRecord = readBack.last()
                listOf(
                        "bigint",
                        "varchar",
                        "large_varchar",
                        "float8",
                        "decimal",
                        "bit",
                        "date",
                        "timestamp",
                        "timestamp_tz",
                    )
                    .forEach { assertNull(nullRecord.getField(it)) }
                assertNotNull(nullRecord.getField(Meta.COLUMN_NAME_AB_RAW_ID))
            }
        }
    }

    @Test
    fun `caps row groups and reads all rows back`() {
        val rowCount = 20_000
        val payloads = List(rowCount) { row -> "row-$row-${"0123456789abcdef".repeat(16)}" }
        val inputSchema =
            ObjectType(linkedMapOf("payload" to FieldType(StringType, nullable = true)))
        val stream =
            DestinationStream(
                unmappedNamespace = "test_namespace",
                unmappedName = "row_group_stream",
                generationId = 73,
                minimumGenerationId = 0,
                syncId = 92,
                namespaceMapper =
                    NamespaceMapper(namespaceDefinitionType = NamespaceDefinitionType.SOURCE),
                tableSchema =
                    StreamTableSchema(
                        tableNames =
                            TableNames(
                                finalTableName = TableName("test_namespace", "row_group_stream")
                            ),
                        columnSchema =
                            ColumnSchema(
                                inputSchema = inputSchema.properties,
                                inputToFinalColumnNames = mapOf("payload" to "payload"),
                                finalSchema = emptyMap(),
                            ),
                        importType = Append,
                    ),
            )
        val icebergSchema = inputSchema.withAirbyteMeta(flatten = true).toIcebergSchema(emptyList())
        val table =
            HadoopTables(Configuration())
                .create(
                    icebergSchema,
                    PartitionSpec.unpartitioned(),
                    SortOrder.unsorted(),
                    emptyMap(),
                    tempDir.resolve("row-groups-table").toUri().toString(),
                )

        RootAllocator(Long.MAX_VALUE).use { allocator ->
            VectorSchemaRoot.create(
                    ArrowSchema(listOf(field("payload", ArrowType.Utf8()))),
                    allocator,
                )
                .use { root ->
                    root.allocateNew()
                    (root.getVector("payload") as VarCharVector).apply {
                        payloads.forEachIndexed { row, payload ->
                            setSafe(row, payload.toByteArray(StandardCharsets.UTF_8))
                        }
                    }
                    root.rowCount = rowCount

                    val generationIdSuffix = "ab-generation-id-${stream.generationId}-e"
                    val batch =
                        ArrowBatchDTO(
                            root = root,
                            partitionKey =
                                io.airbyte.cdk.load.dataflow.state.PartitionKey("partition"),
                            rowCount = rowCount,
                            sizeBytes = 0,
                            emittedAtMs = 1_720_000_000_123L,
                        )
                    val dataFiles =
                        ArrowBatchFileWriter(
                                table,
                                stream,
                                generationIdSuffix,
                                maxRowGroupSizeBytes = 64L * 1024,
                            )
                            .use { writer ->
                                writer.write(batch)
                                val completedFiles = writer.complete()
                                val repeatedFiles = writer.complete()
                                assertEquals(
                                    completedFiles.map { it.location() to it.recordCount() },
                                    repeatedFiles.map { it.location() to it.recordCount() },
                                )
                                assertThrows(IllegalStateException::class.java) {
                                    writer.write(batch)
                                }
                                completedFiles
                            }
                    val dataFile = dataFiles.single()
                    val rowGroupCount =
                        ParquetFileReader.open(
                                HadoopInputFile.fromPath(
                                    org.apache.hadoop.fs.Path(dataFile.location()),
                                    Configuration(),
                                ),
                            )
                            .use { it.footer.blocks.size }
                    assertTrue(
                        rowGroupCount > 1,
                        "Expected multiple row groups, got $rowGroupCount"
                    )

                    table.newAppend().appendFile(dataFile).commit()
                    IcebergGenerics.read(table).build().use { records ->
                        val readBack = records.toList()
                        assertEquals(rowCount, readBack.size)
                        assertEquals(
                            payloads.toSet(),
                            readBack.map { it.getField("payload") as String }.toSet(),
                        )
                    }
                }
        }
    }

    private fun arrowSchema() =
        ArrowSchema(
            listOf(
                field("source_bigint", ArrowType.Int(64, true)),
                field("varchar", ArrowType.Utf8()),
                field("large_varchar", ArrowType.LargeUtf8()),
                field("float8", ArrowType.FloatingPoint(FloatingPointPrecision.DOUBLE)),
                field("decimal", ArrowType.Decimal(38, 9, 128)),
                field("bit", ArrowType.Bool()),
                field("date", ArrowType.Date(org.apache.arrow.vector.types.DateUnit.DAY)),
                field("timestamp", ArrowType.Timestamp(TimeUnit.MICROSECOND, null)),
                field("timestamp_tz", ArrowType.Timestamp(TimeUnit.MICROSECOND, "UTC")),
            ),
        )

    private fun field(name: String, type: ArrowType) =
        Field(name, ArrowFieldType.nullable(type), null)
}
