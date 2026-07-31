/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.toolkits.iceberg.parquet.io

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.AirbyteValueCoercer
import io.airbyte.cdk.load.toolkits.iceberg.parquet.SimpleTableIdGenerator
import io.mockk.every
import io.mockk.mockk
import org.apache.iceberg.BaseTable
import org.apache.iceberg.Schema
import org.apache.iceberg.TableMetadata
import org.apache.iceberg.TableOperations
import org.apache.iceberg.catalog.Catalog
import org.apache.iceberg.types.Types
import org.junit.jupiter.api.Assertions.assertDoesNotThrow
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows

internal class IcebergUtilVariantTest {

    private val icebergUtil =
        IcebergUtil(
            tableIdGenerator = SimpleTableIdGenerator(),
            coercer = AirbyteValueCoercer(),
        )
    private val streamDescriptor = DestinationStream.Descriptor("namespace", "name")
    private val variantSchema =
        Schema(Types.NestedField.optional(1, "payload", Types.VariantType.get()))

    @Test
    fun `loading an existing table below format version 3 fails`() {
        val catalog = catalogWithExistingTable(formatVersion = 2)

        val exception =
            assertThrows<ConfigErrorException> {
                icebergUtil.createTable(streamDescriptor, catalog, variantSchema)
            }

        assertTrue(exception.message!!.contains("format version 2"))
    }

    @Test
    fun `loading an existing format version 3 table succeeds`() {
        val catalog = catalogWithExistingTable(formatVersion = 3)

        assertDoesNotThrow { icebergUtil.createTable(streamDescriptor, catalog, variantSchema) }
    }

    @Test
    fun `loading an existing v2 table fails when v3 is configured without variant`() {
        val catalog = catalogWithExistingTable(formatVersion = 2)
        val stringSchema = Schema(Types.NestedField.optional(1, "payload", Types.StringType.get()))

        assertThrows<ConfigErrorException> {
            icebergUtil.createTable(streamDescriptor, catalog, stringSchema, tableFormatVersion = 3)
        }
    }

    @Test
    fun `loading an existing v3 table succeeds when v2 is configured`() {
        val catalog = catalogWithExistingTable(formatVersion = 3)
        val stringSchema = Schema(Types.NestedField.optional(1, "payload", Types.StringType.get()))

        assertDoesNotThrow {
            icebergUtil.createTable(streamDescriptor, catalog, stringSchema, tableFormatVersion = 2)
        }
    }

    @Test
    fun `a variant schema is rejected when a lower format version is configured`() {
        val catalog = catalogWithExistingTable(formatVersion = 3)

        assertThrows<ConfigErrorException> {
            icebergUtil.createTable(streamDescriptor, catalog, variantSchema, tableFormatVersion = 2)
        }
    }

    private fun catalogWithExistingTable(formatVersion: Int): Catalog {
        val metadata = mockk<TableMetadata> { every { formatVersion() } returns formatVersion }
        val operations = mockk<TableOperations> { every { current() } returns metadata }
        val table = mockk<BaseTable> { every { operations() } returns operations }
        return mockk {
            every { tableExists(any()) } returns true
            every { loadTable(any()) } returns table
        }
    }
}
