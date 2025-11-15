/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.component

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.table.ColumnNameMapping
import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Test

class TableSchemaEvolutionClientTest {
    private val defaultClientImpl =
        object : TableSchemaEvolutionClient {
            override suspend fun discoverSchema(tableName: TableName): TableSchema {
                throw NotImplementedError()
            }

            override fun computeSchema(
                stream: DestinationStream,
                columnNameMapping: ColumnNameMapping
            ): TableSchema {
                throw NotImplementedError()
            }

            override suspend fun applyChangeset(
                stream: DestinationStream,
                columnNameMapping: ColumnNameMapping,
                tableName: TableName,
                expectedColumns: TableColumns,
                columnChangeset: ColumnChangeset,
            ) {
                throw NotImplementedError()
            }
        }

    @Test
    fun testComputeChangeset() {
        val columns1 =
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
        val columns2 =
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

        val changeset = defaultClientImpl.computeChangeset(columns1, columns2)

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
            changeset,
        )
    }
}
