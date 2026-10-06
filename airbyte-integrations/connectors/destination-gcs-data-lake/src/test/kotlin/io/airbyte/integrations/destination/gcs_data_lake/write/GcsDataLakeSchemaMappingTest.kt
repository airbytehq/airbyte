/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_data_lake.write

import io.airbyte.cdk.load.message.Meta
import org.apache.iceberg.Schema
import org.apache.iceberg.types.Types
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

internal class GcsDataLakeSchemaMappingTest {
    @Test
    fun `renamed optional field keeps id, type, doc and optionality`() {
        val schema =
            Schema(
                listOf(
                    Types.NestedField.optional(1, "col with space", Types.StringType.get(), "a doc")
                )
            )

        val mapped =
            transformSchemaWithMappedNames(
                schema,
                mapOf("col with space" to "col_with_space"),
                withIdentifierFields = false,
            )

        val field = mapped.asStruct().fields().single()
        assertEquals(1, field.fieldId())
        assertEquals("col_with_space", field.name())
        assertEquals(Types.StringType.get(), field.type())
        assertEquals("a doc", field.doc())
        assertTrue(field.isOptional)
    }

    @Test
    fun `renamed required field stays required`() {
        val schema =
            Schema(
                listOf(Types.NestedField.required(2, "id!", Types.LongType.get(), "pk")),
                setOf(2),
            )

        val mapped =
            transformSchemaWithMappedNames(
                schema,
                mapOf("id!" to "id"),
                withIdentifierFields = true,
            )

        val field = mapped.asStruct().fields().single()
        assertEquals(2, field.fieldId())
        assertEquals("id", field.name())
        assertEquals(Types.LongType.get(), field.type())
        assertEquals("pk", field.doc())
        assertTrue(field.isRequired)
        assertEquals(setOf(2), mapped.identifierFieldIds())
    }

    @Test
    fun `unmapped and metadata columns are untouched, identifier fields dropped when not requested`() {
        val schema =
            Schema(
                listOf(
                    Types.NestedField.required(3, "plain", Types.StringType.get()),
                    Types.NestedField.optional(
                        4,
                        Meta.COLUMN_NAME_AB_RAW_ID,
                        Types.StringType.get()
                    ),
                ),
                setOf(3),
            )

        val mapped =
            transformSchemaWithMappedNames(
                schema,
                mapOf(Meta.COLUMN_NAME_AB_RAW_ID to "renamed_raw_id"),
                withIdentifierFields = false,
            )

        assertEquals(
            listOf("plain", Meta.COLUMN_NAME_AB_RAW_ID),
            mapped.asStruct().fields().map { it.name() },
        )
        assertTrue(mapped.identifierFieldIds().isEmpty())
    }
}
