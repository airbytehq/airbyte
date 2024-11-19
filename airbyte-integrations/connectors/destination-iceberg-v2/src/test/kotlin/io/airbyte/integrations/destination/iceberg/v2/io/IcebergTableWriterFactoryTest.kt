/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg.v2.io

import io.airbyte.integrations.destination.iceberg.v2.io.IcebergTableWriterFactory
import io.airbyte.integrations.destination.iceberg.v2.io.PartitionedAppendWriter
import io.airbyte.integrations.destination.iceberg.v2.io.PartitionedDeltaWriter
import io.airbyte.integrations.destination.iceberg.v2.io.UnpartitionedAppendWriter
import io.airbyte.integrations.destination.iceberg.v2.io.UnpartitionedDeltaWriter
import io.mockk.every
import io.mockk.mockk
import java.nio.ByteBuffer
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
import org.apache.iceberg.types.Type
import org.apache.iceberg.types.Types
import org.apache.iceberg.types.Types.IntegerType
import org.apache.iceberg.types.Types.StructType
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

internal class IcebergTableWriterFactoryTest {

    @Test
    fun testCreateWriterPartitionedDeltas() {
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
            every { newDataLocation(any(), any(), any()) } returns "location"
        }
        val tableProperties = mapOf<String, String>()
        val tableSchema: Schema = mockk {
            every { aliases } returns emptyMap()
            every { asStruct() } returns struct
            every { columns() } returns columns
            every { identifierFieldIds() } returns primaryKeyIds
            every { schemaId() } returns 1
        }
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

        val factory = IcebergTableWriterFactory()
        val writer = factory.create(table = table)
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
        val struct: StructType = mockk {
            every { asPrimitiveType() } returns IntegerType()
            every { fields() } returns columns.subList(0, 1)
            every { typeId() } returns Type.TypeID.INTEGER
        }
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
            every { newDataLocation(any(), any(), any()) } returns "location"
        }
        val tableProperties = mapOf<String, String>()
        val tableSchema: Schema = mockk {
            every { aliases } returns emptyMap()
            every { asStruct() } returns struct
            every { columns() } returns columns
            every { identifierFieldIds() } returns primaryKeyIds
            every { schemaId() } returns 1
        }
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

        val factory = IcebergTableWriterFactory()
        val writer = factory.create(table = table)
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
        val struct: StructType = mockk {
            every { asPrimitiveType() } returns IntegerType()
            every { fields() } returns columns.subList(0, 1)
            every { typeId() } returns Type.TypeID.INTEGER
        }
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
            every { newDataLocation(any(), any(), any()) } returns "location"
        }
        val tableProperties = mapOf<String, String>()
        val tableSchema: Schema = mockk {
            every { aliases } returns emptyMap()
            every { asStruct() } returns struct
            every { columns() } returns columns
            every { identifierFieldIds() } returns emptySet()
            every { schemaId() } returns 1
        }
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

        val factory = IcebergTableWriterFactory()
        val writer = factory.create(table = table)
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
        val struct: StructType = mockk {
            every { asPrimitiveType() } returns IntegerType()
            every { fields() } returns columns.subList(0, 1)
            every { typeId() } returns Type.TypeID.INTEGER
        }
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
        val tableSchema: Schema = mockk {
            every { aliases } returns emptyMap()
            every { asStruct() } returns struct
            every { columns() } returns columns
            every { identifierFieldIds() } returns emptySet()
            every { schemaId() } returns 1
        }
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

        val factory = IcebergTableWriterFactory()
        val writer = factory.create(table = table)
        assertNotNull(writer)
        assertEquals(UnpartitionedAppendWriter::class.java, writer.javaClass)
    }
}
