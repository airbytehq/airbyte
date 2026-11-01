/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.toolkits.iceberg.parquet.io

import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.Dedupe
import io.mockk.every
import io.mockk.mockk
import java.nio.ByteBuffer
import java.nio.file.Files
import java.time.OffsetDateTime
import kotlin.random.Random
import kotlin.test.assertNotNull
import org.apache.hadoop.conf.Configuration
import org.apache.iceberg.FileFormat
import org.apache.iceberg.PartitionSpec
import org.apache.iceberg.Schema
import org.apache.iceberg.SortOrder
import org.apache.iceberg.Table
import org.apache.iceberg.TableProperties
import org.apache.iceberg.catalog.TableIdentifier
import org.apache.iceberg.data.GenericRecord
import org.apache.iceberg.encryption.EncryptedOutputFile
import org.apache.iceberg.encryption.EncryptionKeyMetadata
import org.apache.iceberg.encryption.EncryptionManager
import org.apache.iceberg.hadoop.HadoopCatalog
import org.apache.iceberg.io.FileIO
import org.apache.iceberg.io.LocationProvider
import org.apache.iceberg.io.OutputFile
import org.apache.iceberg.types.Types
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

internal class IcebergTableWriterFactoryTest {

    private val generationIdSuffix: String = "ab-generation-id-0-e"

    @Test
    fun testCreateWriterPartitionedDeltas() {
        val columns =
            mutableListOf(
                Types.NestedField.required(1, "id", Types.IntegerType.get()),
                Types.NestedField.required(2, "name", Types.StringType.get()),
                Types.NestedField.required(3, "timestamp", Types.TimestampType.withZone()),
            )
        val primaryKeyIds = setOf(1)
        val outputFile: OutputFile = mockk { every { location() } returns "location" }
        val encryptionKeyMetadata: EncryptionKeyMetadata = mockk {
            every { buffer() } returns ByteBuffer.allocate(8)
        }
        val encryptedOutputFile: EncryptedOutputFile = mockk {
            every { encryptingOutputFile() } returns outputFile
            every { keyMetadata() } returns encryptionKeyMetadata
        }
        val encryptionManager: EncryptionManager = mockk {
            every { encrypt(any<OutputFile>()) } returns encryptedOutputFile
        }
        val fileIo: FileIO = mockk { every { newOutputFile(any()) } returns outputFile }
        val locationProvider: LocationProvider = mockk {
            every { newDataLocation(any()) } returns "location"
            every { newDataLocation(any(), any(), any()) } returns "location"
        }
        val tableProperties = mapOf<String, String>()
        val tableSchema = Schema(columns, primaryKeyIds)
        val tableSpec: PartitionSpec = mockk {
            every { fields() } returns emptyList()
            every { isUnpartitioned } returns false
        }
        val table: Table = mockk {
            every { encryption() } returns encryptionManager
            every { io() } returns fileIo
            every { locationProvider() } returns locationProvider
            every { properties() } returns tableProperties
            every { schema() } returns tableSchema
            every { sortOrder() } returns SortOrder.unsorted()
            every { spec() } returns tableSpec
        }

        val factory = IcebergTableWriterFactory()
        val writer =
            factory.create(
                table = table,
                generationId = generationIdSuffix,
                importType =
                    Dedupe(
                        primaryKey = listOf(primaryKeyIds.map { it.toString() }),
                        cursor = primaryKeyIds.map { it.toString() },
                    ),
                tableSchema,
            )
        assertNotNull(writer)
        assertEquals(PartitionedDeltaWriter::class.java, writer.javaClass)
    }

    @Test
    fun testCreateWriterUnPartitionedDeltas() {
        val columns =
            mutableListOf(
                Types.NestedField.required(1, "id", Types.IntegerType.get()),
                Types.NestedField.required(2, "name", Types.StringType.get()),
                Types.NestedField.required(3, "timestamp", Types.TimestampType.withZone()),
            )
        val primaryKeyIds = setOf(1)
        val outputFile: OutputFile = mockk { every { location() } returns "location" }
        val encryptionKeyMetadata: EncryptionKeyMetadata = mockk {
            every { buffer() } returns ByteBuffer.allocate(8)
        }
        val encryptedOutputFile: EncryptedOutputFile = mockk {
            every { encryptingOutputFile() } returns outputFile
            every { keyMetadata() } returns encryptionKeyMetadata
        }
        val encryptionManager: EncryptionManager = mockk {
            every { encrypt(any<OutputFile>()) } returns encryptedOutputFile
        }
        val fileIo: FileIO = mockk { every { newOutputFile(any()) } returns outputFile }
        val locationProvider: LocationProvider = mockk {
            every { newDataLocation(any()) } returns "location"
            every { newDataLocation(any(), any(), any()) } returns "location"
        }
        val tableProperties = mapOf<String, String>()
        val tableSchema = Schema(columns, primaryKeyIds)
        val tableSpec: PartitionSpec = mockk {
            every { fields() } returns emptyList()
            every { isUnpartitioned } returns true
        }
        val table: Table = mockk {
            every { encryption() } returns encryptionManager
            every { io() } returns fileIo
            every { locationProvider() } returns locationProvider
            every { properties() } returns tableProperties
            every { schema() } returns tableSchema
            every { sortOrder() } returns SortOrder.unsorted()
            every { spec() } returns tableSpec
        }

        val factory = IcebergTableWriterFactory()
        val writer =
            factory.create(
                table = table,
                generationId = "ab-generation-id-${Random.nextLong(100)}-e",
                importType =
                    Dedupe(
                        primaryKey = listOf(primaryKeyIds.map { it.toString() }),
                        cursor = primaryKeyIds.map { it.toString() },
                    ),
                tableSchema,
            )
        assertNotNull(writer)
        assertEquals(UnpartitionedDeltaWriter::class.java, writer.javaClass)
    }

    @Test
    fun testCreateWriterPartitionedAppend() {
        val columns =
            mutableListOf(
                Types.NestedField.required(1, "id", Types.IntegerType.get()),
                Types.NestedField.required(2, "name", Types.StringType.get()),
                Types.NestedField.required(3, "timestamp", Types.TimestampType.withZone()),
            )
        val outputFile: OutputFile = mockk { every { location() } returns "location" }
        val encryptionKeyMetadata: EncryptionKeyMetadata = mockk {
            every { buffer() } returns ByteBuffer.allocate(8)
        }
        val encryptedOutputFile: EncryptedOutputFile = mockk {
            every { encryptingOutputFile() } returns outputFile
            every { keyMetadata() } returns encryptionKeyMetadata
        }
        val encryptionManager: EncryptionManager = mockk {
            every { encrypt(any<OutputFile>()) } returns encryptedOutputFile
        }
        val fileIo: FileIO = mockk { every { newOutputFile(any()) } returns outputFile }
        val locationProvider: LocationProvider = mockk {
            every { newDataLocation(any()) } returns "location"
            every { newDataLocation(any(), any(), any()) } returns "location"
        }
        val tableProperties = mapOf<String, String>()
        val tableSchema = Schema(columns)
        val tableSpec: PartitionSpec = mockk {
            every { fields() } returns emptyList()
            every { isUnpartitioned } returns false
        }
        val table: Table = mockk {
            every { encryption() } returns encryptionManager
            every { io() } returns fileIo
            every { locationProvider() } returns locationProvider
            every { properties() } returns tableProperties
            every { schema() } returns tableSchema
            every { sortOrder() } returns SortOrder.unsorted()
            every { spec() } returns tableSpec
        }

        val factory = IcebergTableWriterFactory()
        val writer =
            factory.create(
                table = table,
                generationId = "ab-generation-id-${Random.nextLong(100)}-e",
                importType = Append,
                tableSchema,
            )
        assertNotNull(writer)
        assertEquals(PartitionedAppendWriter::class.java, writer.javaClass)
    }

    @Test
    fun testCreateWriterUnPartitionedAppend() {
        val columns =
            mutableListOf(
                Types.NestedField.required(1, "id", Types.IntegerType.get()),
                Types.NestedField.required(2, "name", Types.StringType.get()),
                Types.NestedField.required(3, "timestamp", Types.TimestampType.withZone()),
            )
        val outputFile: OutputFile = mockk { every { location() } returns "location" }
        val encryptionKeyMetadata: EncryptionKeyMetadata = mockk {
            every { buffer() } returns ByteBuffer.allocate(8)
        }
        val encryptedOutputFile: EncryptedOutputFile = mockk {
            every { encryptingOutputFile() } returns outputFile
            every { keyMetadata() } returns encryptionKeyMetadata
        }
        val encryptionManager: EncryptionManager = mockk {
            every { encrypt(any<OutputFile>()) } returns encryptedOutputFile
        }
        val fileIo: FileIO = mockk { every { newOutputFile(any()) } returns outputFile }
        val locationProvider: LocationProvider = mockk {
            every { newDataLocation(any()) } returns "location"
            every { newDataLocation(any(), any(), any()) } returns "location"
        }
        val tableProperties = mapOf<String, String>()
        val tableSchema = Schema(columns)
        val tableSpec: PartitionSpec = mockk {
            every { fields() } returns emptyList()
            every { isUnpartitioned } returns true
        }
        val table: Table = mockk {
            every { encryption() } returns encryptionManager
            every { io() } returns fileIo
            every { locationProvider() } returns locationProvider
            every { properties() } returns tableProperties
            every { schema() } returns tableSchema
            every { sortOrder() } returns SortOrder.unsorted()
            every { spec() } returns tableSpec
        }

        val factory = IcebergTableWriterFactory()
        val writer =
            factory.create(
                table = table,
                generationId = "ab-generation-id-${Random.nextLong(100)}-e",
                importType = Append,
                tableSchema,
            )
        assertNotNull(writer)
        assertEquals(UnpartitionedAppendWriter::class.java, writer.javaClass)
    }

    @Test
    fun `partitioned append writer accepts interleaved partitions`() {
        val warehouse = Files.createTempDirectory("iceberg-interleaved-append")
        val catalog = HadoopCatalog(Configuration(), warehouse.toString())
        val tableId = TableIdentifier.of("db", "interleaved_append")
        val schema =
            Schema(
                listOf(
                    Types.NestedField.required(1, "id", Types.IntegerType.get()),
                    Types.NestedField.required(2, "updated_at", Types.TimestampType.withZone()),
                ),
                setOf(1),
            )
        catalog.createNamespace(tableId.namespace())
        val table =
            catalog
                .buildTable(tableId, schema)
                .withProperty(
                    TableProperties.DEFAULT_FILE_FORMAT,
                    FileFormat.PARQUET.name.lowercase(),
                )
                .withPartitionSpec(PartitionSpec.builderFor(schema).day("updated_at").build())
                .create()
        fun record(id: Int, at: String) =
            GenericRecord.create(schema).apply {
                setField("id", id)
                setField("updated_at", OffsetDateTime.parse(at))
            }
        val writer = IcebergTableWriterFactory().create(table, generationIdSuffix, Append, schema)

        writer.write(record(1, "2025-01-01T12:00:00Z"))
        writer.write(record(2, "2025-01-02T12:00:00Z"))
        writer.write(record(3, "2025-01-01T13:00:00Z"))
        val result = writer.complete()

        assertEquals(2, result.dataFiles().size)
        assertEquals(2, result.dataFiles().map { it.partition() }.toSet().size)
        assertEquals(0, result.deleteFiles().size)

        catalog.dropTable(tableId)
        warehouse.toFile().deleteRecursively()
    }
}
