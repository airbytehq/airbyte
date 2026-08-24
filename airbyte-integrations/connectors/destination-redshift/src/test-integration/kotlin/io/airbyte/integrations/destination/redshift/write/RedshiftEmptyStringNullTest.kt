/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.write

import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.ObjectTypeWithoutSchema
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.message.InputRecord
import io.airbyte.cdk.load.test.util.OutputRecord
import org.junit.jupiter.api.Test

/**
 * Integration test verifying that the Redshift destination correctly preserves empty strings (`''`)
 * and genuine nulls across VARCHAR, INTEGER, and SUPER column types.
 *
 * This is a regression test for the v4.0 direct-load rewrite which silently converted empty strings
 * to NULL via the `EMPTYASNULL` COPY option. The fix replaces `EMPTYASNULL` with a static null
 * sentinel (`_AB_NULL_`) that the `NULL AS` COPY option maps to SQL NULL, while empty CSV fields
 * are preserved as empty strings for VARCHAR/SUPER columns.
 */
class RedshiftEmptyStringNullTest : RedshiftBaseAcceptanceTest() {

    @Test
    fun testEmptyStringsPreservedAndNullsCorrectForAllColumnTypes() {
        val schema =
            ObjectType(
                linkedMapOf(
                    "id" to FieldType(IntegerType, nullable = false),
                    "str_col" to FieldType(StringType, nullable = true),
                    "int_col" to FieldType(IntegerType, nullable = true),
                    "obj_col" to FieldType(ObjectTypeWithoutSchema, nullable = true),
                ),
            )

        val stream =
            DestinationStream(
                unmappedNamespace = randomizedNamespace,
                unmappedName = "test_empty_string_null",
                generationId = 0,
                minimumGenerationId = 0,
                syncId = 42,
                namespaceMapper = namespaceMapperForMedium(),
                tableSchema = makeTableSchema(schema, Append),
            )

        runSync(
            updatedConfig,
            stream,
            listOf(
                // Record 1: all columns have valid values
                InputRecord(
                    stream = stream,
                    data =
                        """{"id": 1, "str_col": "hello", "int_col": 42, "obj_col": {"key": "value"}}""",
                    emittedAtMs = 1234,
                ),
                // Record 2: all nullable columns are null
                InputRecord(
                    stream = stream,
                    data = """{"id": 2, "str_col": null, "int_col": null, "obj_col": null}""",
                    emittedAtMs = 1234,
                ),
                // Record 3: empty string for varchar, zero for int, empty object for super
                InputRecord(
                    stream = stream,
                    data = """{"id": 3, "str_col": "", "int_col": 0, "obj_col": {}}""",
                    emittedAtMs = 1234,
                ),
            ),
        )

        dumpAndDiffRecords(
            parsedConfig,
            listOf(
                // Record 1: valid values preserved
                OutputRecord(
                    extractedAt = 1234,
                    generationId = 0,
                    data =
                        mapOf(
                            "id" to 1,
                            "str_col" to "hello",
                            "int_col" to 42,
                            "obj_col" to mapOf("key" to "value"),
                        ),
                    airbyteMeta = OutputRecord.Meta(changes = emptyList(), syncId = 42),
                ),
                // Record 2: genuine nulls remain NULL (not empty string)
                OutputRecord(
                    extractedAt = 1234,
                    generationId = 0,
                    data =
                        mapOf(
                            "id" to 2,
                            "str_col" to null,
                            "int_col" to null,
                            "obj_col" to null,
                        ),
                    airbyteMeta = OutputRecord.Meta(changes = emptyList(), syncId = 42),
                ),
                // Record 3: empty string preserved (NOT converted to null), zero and {} preserved
                OutputRecord(
                    extractedAt = 1234,
                    generationId = 0,
                    data =
                        mapOf(
                            "id" to 3,
                            "str_col" to "",
                            "int_col" to 0,
                            "obj_col" to emptyMap<String, Any>(),
                        ),
                    airbyteMeta = OutputRecord.Meta(changes = emptyList(), syncId = 42),
                ),
            ),
            stream,
            primaryKey = listOf(listOf("id")),
            cursor = null,
        )
    }
}
