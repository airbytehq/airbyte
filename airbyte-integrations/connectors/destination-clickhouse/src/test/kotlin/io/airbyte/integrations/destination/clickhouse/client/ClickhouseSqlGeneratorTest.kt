/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse.client

import com.github.vertical_blank.sqlformatter.SqlFormatter
import com.github.vertical_blank.sqlformatter.languages.Dialect
import io.airbyte.cdk.load.component.ColumnChangeset
import io.airbyte.cdk.load.component.ColumnType
import io.airbyte.cdk.load.component.ColumnTypeChange
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.table.ColumnNameMapping
import io.airbyte.integrations.destination.clickhouse.spec.ClickhouseConfiguration
import io.mockk.mockk
import kotlin.test.assertTrue
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertDoesNotThrow
import org.junit.jupiter.api.assertThrows
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.Arguments
import org.junit.jupiter.params.provider.MethodSource

class ClickhouseSqlGeneratorTest {
    private val clickhouseConfiguration: ClickhouseConfiguration = mockk(relaxed = true)

    private val clickhouseSqlGenerator = ClickhouseSqlGenerator(clickhouseConfiguration)

    @Test
    fun testCreateNamespace() {
        val namespace = "test_namespace"
        val expected = "CREATE DATABASE IF NOT EXISTS `$namespace`;"
        val actual = clickhouseSqlGenerator.createNamespace(namespace)
        assert(expected == actual) { "Expected: $expected, but got: $actual" }
    }

    @ParameterizedTest
    @MethodSource("alterTableTestCases")
    fun testAlterTableContainsClauses(
        columnChangeset: ColumnChangeset,
        expectedClauses: List<String>
    ) {
        val tableName = TableName("my_namespace", "my_table")
        val actualSql = clickhouseSqlGenerator.alterTable(columnChangeset, tableName)
        expectedClauses.forEach { clause ->
            assertTrue(
                actualSql.contains(clause),
                "Expected SQL to contain: $clause, but got: $actualSql"
            )
        }
    }

    @Test
    fun testAlterTableValidSql() {
        val columnChangeset =
            ColumnChangeset(
                columnsToAdd =
                    mapOf(
                        "col1" to ColumnType("Int32", true),
                        "col2" to ColumnType("String", true)
                    ),
                columnsToChange =
                    mapOf(
                        "col3" to
                            ColumnTypeChange(
                                ColumnType("IrrelevantValue", true),
                                ColumnType("String", true),
                            ),
                        "col4" to
                            ColumnTypeChange(
                                ColumnType("IrrelevantValue", true),
                                ColumnType("Int64", true),
                            ),
                    ),
                columnsToDrop =
                    mapOf(
                        "col5" to ColumnType("IrrelevantValue", true),
                        "col6" to ColumnType("IrrelevantValue", true)
                    ),
                columnsToRetain = emptyMap(),
            )
        val tableName = TableName("my_namespace", "my_table")
        val sql = clickhouseSqlGenerator.alterTable(columnChangeset, tableName)

        assertDoesNotThrow {
            // Using the StandardSql dialect as a substitute for clickhouse SQL syntax validation.
            // The formatter will parse the SQL, and an invalid statement will throw an exception.
            SqlFormatter.of(Dialect.StandardSql).format(sql)
        }
    }

    @Test
    fun `test extractPks with single primary key`() {
        val primaryKey = listOf(listOf("id"))
        val columnNameMapping = ColumnNameMapping(mapOf("id" to "id_column"))
        val expected = listOf("id_column")
        val actual = clickhouseSqlGenerator.extractPks(primaryKey, columnNameMapping)
        Assertions.assertEquals(expected, actual)
    }

    @Test
    fun `test extractPks with multiple primary keys`() {
        val primaryKey = listOf(listOf("id"), listOf("name"))
        val columnNameMapping =
            ColumnNameMapping(mapOf("id" to "id_column", "name" to "name_column"))
        val expected = listOf("id_column", "name_column")
        val actual = clickhouseSqlGenerator.extractPks(primaryKey, columnNameMapping)
        Assertions.assertEquals(expected, actual)
    }

    @Test
    fun `test extractPks with empty primary key list`() {
        val primaryKey = emptyList<List<String>>()
        val columnNameMapping = ColumnNameMapping(emptyMap<String, String>())
        val expected = listOf<String>()
        val actual = clickhouseSqlGenerator.extractPks(primaryKey, columnNameMapping)
        Assertions.assertEquals(expected, actual)
    }

    @Test
    fun `test extractPks without column mapping`() {
        val primaryKey = listOf(listOf("id"))
        val columnNameMapping = ColumnNameMapping(mapOf())
        val expected = listOf("id")
        val actual = clickhouseSqlGenerator.extractPks(primaryKey, columnNameMapping)
        Assertions.assertEquals(expected, actual)
    }

    @Test
    fun `test extractPks with nested primary key`() {
        val primaryKey = listOf(listOf("user", "id"))
        val columnNameMapping =
            ColumnNameMapping(
                mapOf("user.id" to "user_id_column")
            ) // This mapping is not used but here for completeness.
        assertThrows<UnsupportedOperationException> {
            clickhouseSqlGenerator.extractPks(primaryKey, columnNameMapping)
        }
    }

    @Test
    fun `test exchangeTable`() {
        val sourceTable = TableName("source_db", "source_table")
        val targetTable = TableName("target_db", "target_table")
        val expectedSql =
            """
            EXCHANGE TABLES `source_db`.`source_table`
                AND `target_db`.`target_table`;
        """.trimIndent()
        val actualSql = clickhouseSqlGenerator.exchangeTable(sourceTable, targetTable)

        Assertions.assertEquals(actualSql, expectedSql)
    }

    @Test
    fun `test copyTable`() {
        val sourceTable = TableName("source_namespace", "source_table")
        val targetTable = TableName("target_namespace", "target_table")
        val columnNameMapping =
            ColumnNameMapping(mapOf("source_col1" to "target_col1", "source_col2" to "target_col2"))

        val expectedSql =
            """
            INSERT INTO `target_namespace`.`target_table`
            (
                _airbyte_raw_id,
                _airbyte_extracted_at,
                _airbyte_meta,
                _airbyte_generation_id,
                target_col1,target_col2
            )
            SELECT
                _airbyte_raw_id,
                _airbyte_extracted_at,
                _airbyte_meta,
                _airbyte_generation_id,
                target_col1,target_col2
            FROM `source_namespace`.`source_table`
        """.trimIndent()

        val actualSql =
            clickhouseSqlGenerator.copyTable(columnNameMapping, sourceTable, targetTable)
        Assertions.assertEquals(expectedSql, actualSql)
    }

    companion object {
        @JvmStatic
        fun alterTableTestCases(): List<Arguments> =
            listOf(
                Arguments.of(
                    ColumnChangeset(
                        columnsToAdd = mapOf("new_column" to ColumnType("Int32", false)),
                        columnsToChange =
                            mapOf(
                                "existing_column" to
                                    ColumnTypeChange(
                                        ColumnType("IrrelevantValue", false),
                                        ColumnType("String", false)
                                    )
                            ),
                        columnsToDrop = mapOf("old_column" to ColumnType("IrrelevantValue", false)),
                        columnsToRetain = emptyMap(),
                    ),
                    listOf(
                        " ADD COLUMN `new_column` Int32",
                        " MODIFY COLUMN `existing_column` String",
                        " DROP COLUMN `old_column`"
                    )
                ),
                Arguments.of(
                    ColumnChangeset(
                        columnsToAdd = mapOf("new_column" to ColumnType("Int32", false)),
                        columnsToChange = emptyMap(),
                        columnsToDrop = mapOf(),
                        columnsToRetain = emptyMap(),
                    ),
                    listOf(" ADD COLUMN `new_column` Int32")
                ),
                Arguments.of(
                    ColumnChangeset(
                        columnsToAdd = emptyMap(),
                        columnsToChange =
                            mapOf(
                                "existing_column" to
                                    ColumnTypeChange(
                                        ColumnType("IrrelevantValue", false),
                                        ColumnType("String", false)
                                    )
                            ),
                        columnsToDrop = mapOf(),
                        columnsToRetain = emptyMap(),
                    ),
                    listOf(" MODIFY COLUMN `existing_column` String")
                ),
                Arguments.of(
                    ColumnChangeset(
                        columnsToAdd = emptyMap(),
                        columnsToChange = emptyMap(),
                        columnsToDrop = mapOf("old_column" to ColumnType("IrrelevantValue", false)),
                        columnsToRetain = emptyMap(),
                    ),
                    listOf(" DROP COLUMN `old_column`")
                ),
                Arguments.of(
                    ColumnChangeset(
                        columnsToAdd =
                            mapOf(
                                "col1" to ColumnType("Int32", false),
                                "col2" to ColumnType("String", true),
                            ),
                        columnsToChange =
                            mapOf(
                                "col3" to
                                    ColumnTypeChange(
                                        ColumnType("IrrelevantValue", false),
                                        ColumnType("String", false)
                                    ),
                                "col4" to
                                    ColumnTypeChange(
                                        ColumnType("IrrelevantValue", false),
                                        ColumnType("Int64", true)
                                    ),
                            ),
                        columnsToDrop =
                            mapOf(
                                "col5" to ColumnType("String", false),
                                "col6" to ColumnType("String", false),
                            ),
                        columnsToRetain = emptyMap(),
                    ),
                    listOf(
                        " ADD COLUMN `col1` Int32",
                        " ADD COLUMN `col2` Nullable(String)",
                        " MODIFY COLUMN `col3` String",
                        " MODIFY COLUMN `col4` Nullable(Int64)",
                        " DROP COLUMN `col5`",
                        " DROP COLUMN `col6`"
                    )
                ),
            )
    }
}
