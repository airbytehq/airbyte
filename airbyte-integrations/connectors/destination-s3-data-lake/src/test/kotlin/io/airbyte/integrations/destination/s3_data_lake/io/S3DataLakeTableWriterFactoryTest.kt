/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_data_lake.io

import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.Dedupe
import io.mockk.every
import io.mockk.mockk
import java.nio.ByteBuffer
import kotlin.random.Random
import kotlin.test.assertNotNull
import org.apache.iceberg.PartitionSpec
import org.apache.iceberg.Schema
import org.apache.iceberg.Table
import org.apache.iceberg.encryption.EncryptedOutputFile
import org.apache.iceberg.encryption.EncryptionKeyMetadata
import org.apache.iceberg.encryption.EncryptionManager
import org.apache.iceberg.io.FileIO
import org.apache.iceberg.io.LocationProvider
import org.apache.iceberg.io.OutputFile
import org.apache.iceberg.types.Types
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

internal class S3DataLakeTableWriterFactoryTest {

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
            every { spec() } returns tableSpec
        }
        val s3DataLakeUtil: S3DataLakeUtil = mockk {
            every { assertGenerationIdSuffixIsOfValidFormat(any()) } returns Unit
        }

        val factory = S3DataLakeTableWriterFactory(s3DataLakeUtil = s3DataLakeUtil)
        val writer =
            factory.create(
                table = table,
                generationId = generationIdSuffix,
                importType =
                    Dedupe(
                        primaryKey = listOf(primaryKeyIds.map { it.toString() }),
                        cursor = primaryKeyIds.map { it.toString() }
                    )
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
            every { spec() } returns tableSpec
        }
        val s3DataLakeUtil: S3DataLakeUtil = mockk {
            every { assertGenerationIdSuffixIsOfValidFormat(any()) } returns Unit
        }

        val factory = S3DataLakeTableWriterFactory(s3DataLakeUtil = s3DataLakeUtil)
        val writer =
            factory.create(
                table = table,
                generationId = "ab-generation-id-${Random.nextLong(100)}",
                importType =
                    Dedupe(
                        primaryKey = listOf(primaryKeyIds.map { it.toString() }),
                        cursor = primaryKeyIds.map { it.toString() }
                    )
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
            every { spec() } returns tableSpec
        }
        val s3DataLakeUtil: S3DataLakeUtil = mockk {
            every { assertGenerationIdSuffixIsOfValidFormat(any()) } returns Unit
        }

        val factory = S3DataLakeTableWriterFactory(s3DataLakeUtil = s3DataLakeUtil)
        val writer =
            factory.create(
                table = table,
                generationId = "ab-generation-id-${Random.nextLong(100)}",
                importType = Append
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
            every { spec() } returns tableSpec
        }
        val s3DataLakeUtil: S3DataLakeUtil = mockk {
            every { assertGenerationIdSuffixIsOfValidFormat(any()) } returns Unit
        }

        val factory = S3DataLakeTableWriterFactory(s3DataLakeUtil = s3DataLakeUtil)
        val writer =
            factory.create(
                table = table,
                generationId = "ab-generation-id-${Random.nextLong(100)}",
                importType = Append
            )
        assertNotNull(writer)
        assertEquals(UnpartitionedAppendWriter::class.java, writer.javaClass)
    }
}
