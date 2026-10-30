/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_data_lake.write

import org.apache.iceberg.Schema
import org.apache.iceberg.catalog.Namespace
import org.apache.iceberg.catalog.TableIdentifier
import org.apache.iceberg.inmemory.InMemoryCatalog
import org.apache.iceberg.types.Types
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

internal class GcsDataLakeIdentifierFieldsTest {
    @Test
    fun `optional primary key becomes required before setting identifier field`() {
        val catalog = createCatalog()
        val table =
            catalog.createTable(
                tableIdentifier("optional_pk"),
                Schema(
                    Types.NestedField.optional(1, "id", Types.LongType.get()),
                    Types.NestedField.optional(2, "name", Types.StringType.get()),
                ),
            )
        table.newFastAppend().commit()

        reconcileIdentifierFields(table, listOf("id"))

        assertTrue(table.schema().findField("id").isRequired)
        assertEquals(setOf("id"), table.schema().identifierFieldNames())
        assertFalse(table.schema().findField("name").isRequired)
    }

    @Test
    fun `new table gets identifier fields for required primary key`() {
        val catalog = createCatalog()
        val table =
            catalog.createTable(
                tableIdentifier("new_table"),
                Schema(Types.NestedField.required(1, "id", Types.LongType.get())),
            )

        reconcileIdentifierFields(table, listOf("id"))

        assertEquals(setOf("id"), table.schema().identifierFieldNames())
    }

    @Test
    fun `existing identifier fields are left for schema synchronizer`() {
        val catalog = createCatalog()
        val table =
            catalog.createTable(
                tableIdentifier("existing_identifiers"),
                Schema(
                    listOf(
                        Types.NestedField.required(1, "id", Types.LongType.get()),
                        Types.NestedField.optional(2, "name", Types.StringType.get()),
                    ),
                    setOf(1),
                ),
            )
        table.newFastAppend().commit()

        reconcileIdentifierFields(table, listOf("name"))

        assertEquals(setOf("id"), table.schema().identifierFieldNames())
        assertFalse(table.schema().findField("name").isRequired)
    }

    @Test
    fun `empty primary keys leave schema unchanged`() {
        val catalog = createCatalog()
        val initialSchema =
            Schema(
                Types.NestedField.optional(1, "id", Types.LongType.get()),
                Types.NestedField.optional(2, "name", Types.StringType.get()),
            )
        val table = catalog.createTable(tableIdentifier("empty_primary_keys"), initialSchema)

        reconcileIdentifierFields(table, emptyList())

        assertEquals(initialSchema.asStruct(), table.schema().asStruct())
        assertTrue(table.schema().identifierFieldIds().isEmpty())
    }

    private fun createCatalog(): InMemoryCatalog =
        InMemoryCatalog().apply {
            initialize("test", emptyMap())
            createNamespace(Namespace.of("test"))
        }

    private fun tableIdentifier(name: String): TableIdentifier = TableIdentifier.of("test", name)
}
