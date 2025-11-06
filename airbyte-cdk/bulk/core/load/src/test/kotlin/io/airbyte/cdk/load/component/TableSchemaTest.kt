/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.component

import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Test

class TableSchemaTest {
    @Test
    fun testComputeChangeset() {
        val schema1 =
            TableSchema(
                mapOf(
                    "to_drop_nullable" to ColumnType("a", true),
                    "to_drop_notnull" to ColumnType("b", false),
                    "to_change_type_nullable" to ColumnType("c", true),
                    "to_change_type_notnull" to ColumnType("d", false),
                    "to_change_nullability_nullable" to ColumnType("e", true),
                    "to_change_nullability_notnull" to ColumnType("f", false),
                    "to_retain_nullable" to ColumnType("g", true),
                    "to_retain_notnull" to ColumnType("h", false),
                )
            )
        val schema2 =
            TableSchema(
                mapOf(
                    "to_change_type_nullable" to ColumnType("c2", true),
                    "to_change_type_notnull" to ColumnType("d2", false),
                    "to_change_nullability_nullable" to ColumnType("e", false),
                    "to_change_nullability_notnull" to ColumnType("f", true),
                    "to_retain_nullable" to ColumnType("g", true),
                    "to_retain_notnull" to ColumnType("h", false),
                    "to_add_nullable" to ColumnType("i", true),
                    "to_add_notnull" to ColumnType("j", false),
                )
            )

        val diff = schema1.computeChangeset(schema2)

        assertEquals(
            ColumnChangeset(
                columnsToAdd =
                    mapOf(
                        "to_add_nullable" to ColumnType("i", true),
                        "to_add_notnull" to ColumnType("j", false),
                    ),
                columnsToDrop =
                    mapOf(
                        "to_drop_nullable" to ColumnType("a", true),
                        "to_drop_notnull" to ColumnType("b", false),
                    ),
                columnsToChange =
                    mapOf(
                        "to_change_type_nullable" to
                            ColumnTypeChange(
                                ColumnType("c", true),
                                ColumnType("c2", true),
                            ),
                        "to_change_type_notnull" to
                            ColumnTypeChange(
                                ColumnType("d", false),
                                ColumnType("d2", false),
                            ),
                        "to_change_nullability_nullable" to
                            ColumnTypeChange(
                                ColumnType("e", true),
                                ColumnType("e", false),
                            ),
                        "to_change_nullability_notnull" to
                            ColumnTypeChange(
                                ColumnType("f", false),
                                ColumnType("f", true),
                            ),
                    ),
                columnsToRetain =
                    mapOf(
                        "to_retain_nullable" to ColumnType("g", true),
                        "to_retain_notnull" to ColumnType("h", false),
                    ),
            ),
            diff,
        )
    }
}
