/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.sql

import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.component.ColumnType
import io.airbyte.cdk.load.component.ColumnTypeChange
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.TimestampTypeWithTimezone
import io.airbyte.cdk.load.schema.model.ColumnSchema
import io.airbyte.cdk.load.schema.model.StreamTableSchema
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.table.CDC_DELETED_AT_COLUMN
import io.airbyte.integrations.destination.redshift.config.RedshiftConfiguration
import io.mockk.every
import io.mockk.mockk
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertNotNull
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Nested
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows

internal class RedshiftSqlGeneratorTest {

    private lateinit var sqlGenerator: RedshiftSqlGenerator

    private fun mockConfig(dropCascade: Boolean = false): RedshiftConfiguration =
        mockk<RedshiftConfiguration> { every { this@mockk.dropCascade } returns dropCascade }

    @BeforeEach
    fun setUp() {
        sqlGenerator = RedshiftSqlGenerator(mockConfig(dropCascade = false))
    }

    // ================================================================
    // Helpers
    // ================================================================

    private fun assertEqualsIgnoreWhitespace(expected: String, actual: String) {
        assertEquals(dropWhitespace(expected), dropWhitespace(actual))
    }

    private fun dropWhitespace(text: String) =
        text.lines().map { it.trim() }.filter { it.isNotEmpty() }.joinToString("\n") { it.trim() }

    private fun mockStream(
        finalSchema: Map<String, ColumnType>,
        inputSchema: Map<String, FieldType> = emptyMap(),
        primaryKey: List<List<String>> = emptyList(),
        cursor: List<String> = emptyList(),
    ): DestinationStream {
        val columnSchema = ColumnSchema(inputSchema, emptyMap(), finalSchema)
        val streamTableSchema =
            mockk<StreamTableSchema> {
                every { this@mockk.columnSchema } returns columnSchema
                every { getPrimaryKey() } returns primaryKey
                every { getCursor() } returns cursor
                every { importType } returns Dedupe(primaryKey = primaryKey, cursor = cursor)
            }
        return mockk<DestinationStream> { every { tableSchema } returns streamTableSchema }
    }

    private fun mockAppendStream(
        finalSchema: Map<String, ColumnType>,
    ): DestinationStream {
        val columnSchema = ColumnSchema(emptyMap(), emptyMap(), finalSchema)
        val streamTableSchema =
            mockk<StreamTableSchema> {
                every { this@mockk.columnSchema } returns columnSchema
                every { getPrimaryKey() } returns emptyList()
                every { getCursor() } returns emptyList()
                every { importType } returns Append
            }
        return mockk<DestinationStream> { every { tableSchema } returns streamTableSchema }
    }

    // ================================================================
    // DDL: Namespace & Table lifecycle
    // ================================================================

    @Test
    fun `createNamespace generates CREATE SCHEMA`() {
        val sql = sqlGenerator.createNamespace("my_schema")
        assertEquals("""CREATE SCHEMA IF NOT EXISTS "my_schema";""", sql)
    }

    @Test
    fun `namespaceExists queries information_schema`() {
        val sql = sqlGenerator.namespaceExists("my_schema")

        assertTrue(sql.contains("SELECT EXISTS("))
        assertTrue(sql.contains("FROM information_schema.schemata"))
        assertTrue(sql.contains("schema_name = 'my_schema'"))
    }

    @Test
    fun `namespaceExists escapes single quotes`() {
        val sql = sqlGenerator.namespaceExists("my'schema")

        assertTrue(sql.contains("schema_name = 'my''schema'"))
    }

    @Test
    fun `tableExists queries information_schema`() {
        val sql = sqlGenerator.tableExists(TableName(namespace = "my_schema", name = "my_table"))

        assertTrue(sql.contains("SELECT EXISTS("))
        assertTrue(sql.contains("FROM information_schema.tables"))
        assertTrue(sql.contains("table_schema = 'my_schema'"))
        assertTrue(sql.contains("table_name = 'my_table'"))
    }

    @Test
    fun `tableExists escapes single quotes`() {
        val sql = sqlGenerator.tableExists(TableName(namespace = "my'ns", name = "my'tbl"))

        assertTrue(sql.contains("table_schema = 'my''ns'"))
        assertTrue(sql.contains("table_name = 'my''tbl'"))
    }

    @Test
    fun `createTable with replace drops and recreates`() {
        val finalSchema =
            mapOf(
                "id" to ColumnType("bigint", false),
                "name" to ColumnType("varchar(65535)", true),
            )
        val stream = mockStream(finalSchema)
        val tableName = TableName(namespace = "public", name = "users")

        val sql = sqlGenerator.createTable(stream, tableName, replace = true)

        assertTrue(sql.contains("BEGIN TRANSACTION;"))
        assertTrue(sql.contains("""DROP TABLE IF EXISTS "public"."users";"""))
        assertTrue(sql.contains("""CREATE TABLE IF NOT EXISTS "public"."users""""))
        assertTrue(sql.contains(""""_airbyte_raw_id" varchar(36) NOT NULL"""))
        assertTrue(sql.contains(""""_airbyte_extracted_at" timestamptz NOT NULL"""))
        assertTrue(sql.contains(""""_airbyte_meta" super NOT NULL"""))
        assertTrue(sql.contains(""""_airbyte_generation_id" bigint NOT NULL"""))
        assertTrue(sql.contains(""""id" bigint NOT NULL"""))
        assertTrue(sql.contains(""""name" varchar(65535)"""))
        assertTrue(sql.contains("COMMIT;"))
    }

    @Test
    fun `createTable without replace skips drop and transaction wrapper`() {
        val finalSchema = mapOf("id" to ColumnType("bigint", false))
        val stream = mockStream(finalSchema)
        val tableName = TableName(namespace = "public", name = "users")

        val sql = sqlGenerator.createTable(stream, tableName, replace = false)

        assertFalse(sql.contains("DROP TABLE"))
        assertFalse(sql.contains("BEGIN TRANSACTION;"))
        assertFalse(sql.contains("COMMIT;"))
        assertTrue(sql.contains("CREATE TABLE IF NOT EXISTS"))
    }

    @Test
    fun `createTable does not include DISTKEY or SORTKEY`() {
        val finalSchema =
            mapOf(
                "id" to ColumnType("bigint", false),
                "name" to ColumnType("varchar(65535)", true),
            )
        val stream =
            mockStream(
                finalSchema = finalSchema,
                primaryKey = listOf(listOf("id")),
                cursor = listOf("updated_at"),
            )
        val tableName = TableName(namespace = "public", name = "users")

        val sql = sqlGenerator.createTable(stream, tableName, replace = false)

        assertFalse(sql.contains("DISTKEY"), "Should not have DISTKEY")
        assertFalse(sql.contains("SORTKEY"), "Should not have SORTKEY")
    }

    @Test
    fun `createTable for dedup stream with replace wraps in transaction`() {
        val finalSchema =
            mapOf(
                "id" to ColumnType("bigint", false),
                "name" to ColumnType("varchar(65535)", true),
            )
        val stream =
            mockStream(
                finalSchema = finalSchema,
                primaryKey = listOf(listOf("id")),
                cursor = listOf("updated_at"),
            )
        val tableName = TableName(namespace = "public", name = "users")

        val sql = sqlGenerator.createTable(stream, tableName, replace = true)

        assertTrue(sql.contains("BEGIN TRANSACTION;"))
        assertTrue(sql.contains("DROP TABLE IF EXISTS"))
        assertFalse(sql.contains("DISTKEY"), "Should not have DISTKEY")
        assertFalse(sql.contains("SORTKEY"), "Should not have SORTKEY")
        assertTrue(sql.contains("COMMIT;"))
    }

    @Test
    fun `dropTable generates DROP TABLE IF EXISTS`() {
        val sql = sqlGenerator.dropTable(TableName(namespace = "ns", name = "tbl"))
        assertEquals("""DROP TABLE IF EXISTS "ns"."tbl";""", sql)
    }

    @Test
    fun `addColumn generates ALTER TABLE ADD COLUMN`() {
        val sql =
            sqlGenerator.addColumn(
                TableName(namespace = "ns", name = "tbl"),
                "new_col",
                "varchar(65535)",
            )
        assertEquals(
            """ALTER TABLE "ns"."tbl" ADD COLUMN "new_col" varchar(65535);""",
            sql,
        )
    }

    // ================================================================
    // DML: Simple queries
    // ================================================================

    @Test
    fun `countTable generates SELECT COUNT`() {
        val sql = sqlGenerator.countTable(TableName(namespace = "ns", name = "tbl"))
        assertEquals("""SELECT COUNT(*) AS "total" FROM "ns"."tbl";""", sql)
    }

    @Test
    fun `isTableNotEmpty generates SELECT EXISTS with LIMIT 1`() {
        val sql = sqlGenerator.isTableNotEmpty(TableName(namespace = "ns", name = "tbl"))
        assertEquals(
            """SELECT EXISTS(SELECT 1 FROM "ns"."tbl" LIMIT 1) AS "not_empty";""",
            sql,
        )
    }

    @Test
    fun `getGenerationId generates SELECT with LIMIT 1`() {
        val sql = sqlGenerator.getGenerationId(TableName(namespace = "ns", name = "tbl"))
        val expected =
            """
            SELECT "_airbyte_generation_id"
            FROM "ns"."tbl"
            LIMIT 1;
            """
        assertEqualsIgnoreWhitespace(expected, sql)
    }

    @Test
    fun `deleteByRawId generates parameterized DELETE`() {
        val sql = sqlGenerator.deleteByRawId(TableName(namespace = "ns", name = "tbl"))
        assertEquals(
            """DELETE FROM "ns"."tbl" WHERE "_airbyte_raw_id" = ?;""",
            sql,
        )
    }

    // ================================================================
    // Table operations: copy, overwrite
    // ================================================================

    @Test
    fun `copyTable generates ALTER TABLE APPEND`() {
        val source = TableName(namespace = "ns", name = "src")
        val target = TableName(namespace = "ns", name = "tgt")

        val sql = sqlGenerator.copyTable(source, target)

        val expected =
            """
            ALTER TABLE "ns"."tgt"
            APPEND FROM "ns"."src"
            FILLTARGET;
            """
        assertEqualsIgnoreWhitespace(expected, sql)
    }

    @Test
    fun `overwriteTable generates DROP and RENAME`() {
        val source = TableName(namespace = "ns", name = "tmp")
        val target = TableName(namespace = "ns", name = "final")

        val sql = sqlGenerator.overwriteTable(source, target)

        assertTrue(sql.contains("BEGIN TRANSACTION;"))
        assertTrue(sql.contains("""DROP TABLE IF EXISTS "ns"."final""""))
        assertTrue(sql.contains("""ALTER TABLE "ns"."tmp" RENAME TO "final""""))
        assertTrue(sql.contains("COMMIT;"))
    }

    // ================================================================
    // Upsert: internal methods
    // ================================================================

    @Test
    fun `selectDeduped with cursor orders by cursor then extracted_at`() {
        val sql =
            sqlGenerator.selectDeduped(
                primaryKeyTargetColumns = listOf(""""id""""),
                cursorTargetColumn = """"updated_at"""",
                allTargetColumns = listOf(""""id"""", """"name"""", """"updated_at""""),
                sourceTableName = TableName(namespace = "ns", name = "staging"),
            )

        val expected =
            """
            SELECT "id", "name", "updated_at"
            FROM (
              SELECT *,
                ROW_NUMBER() OVER (
                  PARTITION BY "id"
                  ORDER BY
                    "updated_at" DESC NULLS LAST, "_airbyte_extracted_at" DESC
                ) AS row_number
              FROM "ns"."staging"
            ) AS deduplicated
            WHERE row_number = 1
            """
        assertEqualsIgnoreWhitespace(expected, sql)
    }

    @Test
    fun `selectDeduped without cursor orders by extracted_at only`() {
        val sql =
            sqlGenerator.selectDeduped(
                primaryKeyTargetColumns = listOf(""""id""""),
                cursorTargetColumn = null,
                allTargetColumns = listOf(""""id"""", """"name""""),
                sourceTableName = TableName(namespace = "ns", name = "staging"),
            )

        assertTrue(sql.contains(""""_airbyte_extracted_at" DESC"""))
        assertFalse(sql.contains("NULLS LAST"))
    }

    @Test
    fun `updateExistingRows excludes PK from SET assignments`() {
        val target = TableName(namespace = "ns", name = "final")
        val sql =
            sqlGenerator.updateExistingRows(
                dedupTableAlias = "deduped_source",
                targetTableName = target,
                allTargetColumns = listOf(""""id"""", """"name"""", """"updated_at""""),
                primaryKeyTargetColumns = listOf(""""id""""),
                cursorTargetColumn = """"updated_at"""",
                cdcHardDeleteEnabled = false,
            )

        // Extract the SET section (between "SET" and "FROM")
        val setSection = sql.substringAfter("SET").substringBefore("FROM")
        // PK should NOT appear in SET assignments
        assertFalse(setSection.contains(""""id" = deduped_source."id""""))
        // Non-PK columns should be in SET
        assertTrue(setSection.contains(""""name" = deduped_source."name""""))
        assertTrue(setSection.contains(""""updated_at" = deduped_source."updated_at""""))
        // PK should be in WHERE
        assertTrue(sql.contains(""""ns"."final"."id" = deduped_source."id""""))
    }

    @Test
    fun `updateExistingRows with CDC adds deleted_at IS NULL clause`() {
        val target = TableName(namespace = "ns", name = "final")
        val sql =
            sqlGenerator.updateExistingRows(
                dedupTableAlias = "deduped_source",
                targetTableName = target,
                allTargetColumns = listOf(""""id"""", """"name""""),
                primaryKeyTargetColumns = listOf(""""id""""),
                cursorTargetColumn = """"updated_at"""",
                cdcHardDeleteEnabled = true,
            )

        assertTrue(sql.contains(""""_ab_cdc_deleted_at" IS NULL"""))
    }

    @Test
    fun `updateExistingRows without cursor uses extracted_at comparison only`() {
        val target = TableName(namespace = "ns", name = "final")
        val sql =
            sqlGenerator.updateExistingRows(
                dedupTableAlias = "deduped_source",
                targetTableName = target,
                allTargetColumns = listOf(""""id"""", """"name""""),
                primaryKeyTargetColumns = listOf(""""id""""),
                cursorTargetColumn = null,
                cdcHardDeleteEnabled = false,
            )

        assertTrue(
            sql.contains(
                """"ns"."final"."_airbyte_extracted_at" < deduped_source."_airbyte_extracted_at""""
            )
        )
        // Should NOT have the 4-way cursor comparison
        assertFalse(sql.contains("IS NULL AND deduped_source."))
    }

    @Test
    fun `insertNewRows without CDC has no deleted_at clause`() {
        val target = TableName(namespace = "ns", name = "final")
        val sql =
            sqlGenerator.insertNewRows(
                dedupTableAlias = "deduped_source",
                targetTableName = target,
                allTargetColumns = listOf(""""id"""", """"name""""),
                primaryKeyTargetColumns = listOf(""""id""""),
                cdcHardDeleteEnabled = false,
            )

        assertTrue(sql.contains("INSERT INTO"))
        assertTrue(sql.contains("NOT EXISTS"))
        assertFalse(sql.contains("_ab_cdc_deleted_at"))
    }

    @Test
    fun `insertNewRows with CDC adds deleted_at IS NULL clause`() {
        val target = TableName(namespace = "ns", name = "final")
        val sql =
            sqlGenerator.insertNewRows(
                dedupTableAlias = "deduped_source",
                targetTableName = target,
                allTargetColumns = listOf(""""id"""", """"name""""),
                primaryKeyTargetColumns = listOf(""""id""""),
                cdcHardDeleteEnabled = true,
            )

        assertTrue(sql.contains(""""_ab_cdc_deleted_at" IS NULL"""))
    }

    // ================================================================
    // Upsert: integration-level
    // ================================================================

    @Test
    fun `upsertTable with cursor and CDC generates full CTE chain`() {
        val finalSchema =
            mapOf(
                "id" to ColumnType("bigint", false),
                "name" to ColumnType("varchar(65535)", true),
                "updated_at" to ColumnType("timestamptz", true),
                CDC_DELETED_AT_COLUMN to ColumnType("timestamptz", true),
            )
        val inputSchema = mapOf(CDC_DELETED_AT_COLUMN to FieldType(TimestampTypeWithTimezone, true))
        val stream =
            mockStream(
                finalSchema = finalSchema,
                inputSchema = inputSchema,
                primaryKey = listOf(listOf("id")),
                cursor = listOf("updated_at"),
            )

        val source = TableName(namespace = "ns", name = "staging")
        val target = TableName(namespace = "ns", name = "final")

        val sql = sqlGenerator.upsertTable(stream, source, target)

        // Redshift uses separate statements with a session-scoped TEMP TABLE (no namespace prefix)
        val dedup = """"_airbyte_dedup_ns_staging""""
        assertTrue(sql.contains("BEGIN TRANSACTION;"))
        assertTrue(sql.contains("CREATE TEMP TABLE $dedup AS"))
        assertTrue(sql.contains("ROW_NUMBER() OVER"))
        assertTrue(sql.contains("""PARTITION BY "id""""))
        // CDC delete as a separate statement
        assertTrue(sql.contains("DELETE FROM \"ns\".\"final\""))
        assertTrue(sql.contains("USING $dedup"))
        assertTrue(sql.contains("\"_ab_cdc_deleted_at\" IS NOT NULL"))
        // Update as a separate statement
        assertTrue(sql.contains("UPDATE \"ns\".\"final\""))
        assertTrue(sql.contains("FROM $dedup"))
        // Insert new rows
        assertTrue(sql.contains("INSERT INTO \"ns\".\"final\""))
        assertTrue(sql.contains("NOT EXISTS"))
        assertTrue(sql.contains("\"_ab_cdc_deleted_at\" IS NULL"))
        // Cleanup
        assertTrue(sql.contains("DROP TABLE IF EXISTS $dedup;"))
        assertTrue(sql.contains("COMMIT;"))
    }

    @Test
    fun `upsertTable without CDC omits deleted CTE`() {
        val finalSchema =
            mapOf(
                "id" to ColumnType("bigint", false),
                "name" to ColumnType("varchar(65535)", true),
                "updated_at" to ColumnType("timestamptz", true),
            )
        val stream =
            mockStream(
                finalSchema = finalSchema,
                primaryKey = listOf(listOf("id")),
                cursor = listOf("updated_at"),
            )

        val source = TableName(namespace = "ns", name = "staging")
        val target = TableName(namespace = "ns", name = "final")

        val sql = sqlGenerator.upsertTable(stream, source, target)

        assertTrue(sql.contains("BEGIN TRANSACTION;"))
        assertTrue(sql.contains("CREATE TEMP TABLE"))
        assertTrue(sql.contains("_airbyte_dedup_ns_staging"))
        assertFalse(sql.contains("DELETE FROM"))
        assertTrue(sql.contains("UPDATE"))
        assertTrue(sql.contains("INSERT INTO"))
        assertFalse(sql.contains("_ab_cdc_deleted_at"))
        assertTrue(sql.contains("COMMIT;"))
    }

    @Test
    fun `upsertTable truncates dedup temp table name when source name is long`() {
        val longName = "a".repeat(127) // already at Redshift max
        val finalSchema =
            mapOf(
                "id" to ColumnType("bigint", false),
                "name" to ColumnType("varchar(65535)", true),
                "updated_at" to ColumnType("timestamptz", true),
            )
        val stream =
            mockStream(
                finalSchema = finalSchema,
                primaryKey = listOf(listOf("id")),
                cursor = listOf("updated_at"),
            )

        val source = TableName(namespace = "ns", name = longName)
        val target = TableName(namespace = "ns", name = "final")

        val sql = sqlGenerator.upsertTable(stream, source, target)

        // The dedup temp table name should be truncated to 127 chars
        // "_airbyte_dedup_" + 127 chars = 143 chars > 127, so it must be truncated with a hash
        val dedupPrefix = "_airbyte_dedup_"
        assertTrue(sql.contains("CREATE TEMP TABLE"))
        // The full un-truncated name should NOT appear
        assertFalse(sql.contains("$dedupPrefix$longName"))
        // Extract the dedup table name from the CREATE TEMP TABLE statement
        val createTempRegex = Regex("""CREATE TEMP TABLE "([^"]+)" AS""")
        val match = createTempRegex.find(sql)
        assertNotNull(match)
        val dedupTableName = match!!.groupValues[1]
        assertTrue(
            dedupTableName.length <= 127,
            "Dedup temp table name exceeds 127 chars: ${dedupTableName.length}"
        )
        assertTrue(
            dedupTableName.startsWith(dedupPrefix),
            "Dedup temp table name should start with $dedupPrefix"
        )
    }

    @Test
    fun `upsertTable without primary key throws IllegalArgumentException`() {
        val streamTableSchema =
            mockk<StreamTableSchema> {
                every { importType } returns Dedupe(primaryKey = emptyList(), cursor = emptyList())
            }
        val stream = mockk<DestinationStream> { every { tableSchema } returns streamTableSchema }

        val exception =
            assertThrows<IllegalArgumentException> {
                sqlGenerator.upsertTable(
                    stream,
                    TableName(namespace = "ns", name = "src"),
                    TableName(namespace = "ns", name = "tgt"),
                )
            }

        assertEquals("Cannot perform upsert without primary key", exception.message)
    }

    // ================================================================
    // Schema evolution: matchSchemas
    // ================================================================

    @Test
    fun `matchSchemas adds columns`() {
        val tableName = TableName(namespace = "ns", name = "tbl")
        val sql =
            sqlGenerator.matchSchemas(
                tableName,
                columnsToAdd =
                    mapOf(
                        "new_col" to ColumnType("varchar(65535)", true),
                        "another_col" to ColumnType("bigint", false),
                    ),
                columnsToRemove = emptyMap(),
                columnsToModify = emptyMap(),
            )

        assertTrue(sql.contains("BEGIN TRANSACTION;"))
        assertTrue(sql.contains("""ALTER TABLE "ns"."tbl" ADD COLUMN "new_col" varchar(65535);"""))
        assertTrue(sql.contains("""ALTER TABLE "ns"."tbl" ADD COLUMN "another_col" bigint;"""))
        assertTrue(sql.contains("COMMIT;"))
    }

    @Test
    fun `matchSchemas removes columns`() {
        val tableName = TableName(namespace = "ns", name = "tbl")
        val sql =
            sqlGenerator.matchSchemas(
                tableName,
                columnsToAdd = emptyMap(),
                columnsToRemove = mapOf("old_col" to ColumnType("varchar", true)),
                columnsToModify = emptyMap(),
            )

        assertTrue(sql.contains("""ALTER TABLE "ns"."tbl" DROP COLUMN "old_col";"""))
    }

    @Test
    fun `matchSchemas SUPER to VARCHAR uses JSON_SERIALIZE`() {
        val tableName = TableName(namespace = "ns", name = "tbl")
        val sql =
            sqlGenerator.matchSchemas(
                tableName,
                columnsToAdd = emptyMap(),
                columnsToRemove = emptyMap(),
                columnsToModify =
                    mapOf(
                        "json_col" to
                            ColumnTypeChange(
                                originalType = ColumnType("super", true),
                                newType = ColumnType("varchar(65535)", true),
                            )
                    ),
            )

        assertTrue(sql.contains("""ADD COLUMN "_airbyte_tmp_json_col" varchar(65535);"""))
        assertTrue(sql.contains("""JSON_SERIALIZE("json_col")"""))
        assertTrue(sql.contains("""DESTINATION_TYPECAST_ERROR"""))
        assertTrue(sql.contains(""""json_col" IS NOT NULL"""))
        assertTrue(sql.contains(""""_airbyte_tmp_json_col" IS NULL"""))
        assertTrue(sql.contains("""DROP COLUMN "json_col";"""))
        assertTrue(sql.contains("""RENAME COLUMN "_airbyte_tmp_json_col" TO "json_col";"""))
    }

    @Test
    fun `matchSchemas VARCHAR to SUPER uses IS_VALID_JSON`() {
        val tableName = TableName(namespace = "ns", name = "tbl")
        val sql =
            sqlGenerator.matchSchemas(
                tableName,
                columnsToAdd = emptyMap(),
                columnsToRemove = emptyMap(),
                columnsToModify =
                    mapOf(
                        "data_col" to
                            ColumnTypeChange(
                                originalType = ColumnType("varchar(65535)", true),
                                newType = ColumnType("super", true),
                            )
                    ),
            )

        assertTrue(sql.contains("""ADD COLUMN "_airbyte_tmp_data_col" super;"""))
        assertTrue(sql.contains("IS_VALID_JSON("))
        assertTrue(sql.contains("JSON_PARSE("))
        assertFalse(sql.contains("REPLACE("))
        assertTrue(sql.contains("""DESTINATION_TYPECAST_ERROR"""))
        assertTrue(sql.contains(""""data_col" IS NOT NULL"""))
        assertTrue(sql.contains(""""_airbyte_tmp_data_col" IS NULL"""))
        assertTrue(sql.contains("""DROP COLUMN "data_col";"""))
        assertTrue(sql.contains("""RENAME COLUMN "_airbyte_tmp_data_col" TO "data_col";"""))
    }

    @Test
    fun `matchSchemas generic type change uses CAST`() {
        val tableName = TableName(namespace = "ns", name = "tbl")
        val sql =
            sqlGenerator.matchSchemas(
                tableName,
                columnsToAdd = emptyMap(),
                columnsToRemove = emptyMap(),
                columnsToModify =
                    mapOf(
                        "num_col" to
                            ColumnTypeChange(
                                originalType = ColumnType("bigint", false),
                                newType = ColumnType("decimal(38,9)", false),
                            )
                    ),
            )

        assertTrue(sql.contains("""ADD COLUMN "_airbyte_tmp_num_col" decimal(38,9);"""))
        assertTrue(sql.contains("""CAST("num_col" AS decimal(38,9))"""))
        assertTrue(sql.contains("""DESTINATION_TYPECAST_ERROR"""))
        assertTrue(sql.contains(""""num_col" IS NOT NULL"""))
        assertTrue(sql.contains(""""_airbyte_tmp_num_col" IS NULL"""))
        assertTrue(sql.contains("""DROP COLUMN "num_col";"""))
        assertTrue(sql.contains("""RENAME COLUMN "_airbyte_tmp_num_col" TO "num_col";"""))
    }

    @Test
    fun `matchSchemas VARCHAR to decimal uses tolerant cast for scientific notation`() {
        val tableName = TableName(namespace = "ns", name = "tbl")
        val sql =
            sqlGenerator.matchSchemas(
                tableName,
                columnsToAdd = emptyMap(),
                columnsToRemove = emptyMap(),
                columnsToModify =
                    mapOf(
                        "num_col" to
                            ColumnTypeChange(
                                originalType = ColumnType("varchar(65535)", true),
                                newType = ColumnType("decimal(38,9)", true),
                            )
                    ),
            )

        // Must NOT use a bare CAST, which aborts the transaction on scientific-notation values.
        assertFalse(
            sql.contains("""SET "_airbyte_tmp_num_col" = CAST("num_col" AS decimal(38,9));""")
        )
        // Plain numbers cast directly (full precision); scientific notation routes through double.
        assertTrue(sql.contains("""WHEN "num_col" ~ '^[+-]?[0-9]+([.][0-9]+)?$'"""))
        assertTrue(sql.contains("""THEN CAST(CAST("num_col" AS decimal(38,9)) AS decimal(38,9))"""))
        assertTrue(sql.contains("""WHEN "num_col" ~ '^[+-]?[0-9]+([.][0-9]+)?[eE][+-]?[0-9]+$'"""))
        assertTrue(
            sql.contains("""THEN CAST(CAST("num_col" AS double precision) AS decimal(38,9))""")
        )
        assertTrue(sql.contains("ELSE NULL"))
        // Un-castable values still recorded as typecast errors.
        assertTrue(sql.contains("""DESTINATION_TYPECAST_ERROR"""))
        assertTrue(sql.contains(""""num_col" IS NOT NULL"""))
        assertTrue(sql.contains(""""_airbyte_tmp_num_col" IS NULL"""))
    }

    @Test
    fun `matchSchemas VARCHAR to bigint uses tolerant cast`() {
        val tableName = TableName(namespace = "ns", name = "tbl")
        val sql =
            sqlGenerator.matchSchemas(
                tableName,
                columnsToAdd = emptyMap(),
                columnsToRemove = emptyMap(),
                columnsToModify =
                    mapOf(
                        "int_col" to
                            ColumnTypeChange(
                                originalType = ColumnType("varchar(65535)", true),
                                newType = ColumnType("bigint", true),
                            )
                    ),
            )

        assertFalse(sql.contains("""SET "_airbyte_tmp_int_col" = CAST("int_col" AS bigint);"""))
        assertTrue(sql.contains("""THEN CAST(CAST("int_col" AS decimal(38,9)) AS bigint)"""))
        assertTrue(sql.contains("""THEN CAST(CAST("int_col" AS double precision) AS bigint)"""))
        assertTrue(sql.contains("ELSE NULL"))
    }

    // ================================================================
    // Staging & schema discovery
    // ================================================================

    @Test
    fun `copyFromS3 generates COPY command`() {
        val sql =
            sqlGenerator.copyFromS3(
                tableName = TableName(namespace = "ns", name = "tbl"),
                s3Path = "s3://bucket/path/file.csv.gz",
                accessKeyId = "AKIATEST",
                secretAccessKey = "secret123",
                region = "us-east-1",
            )

        assertTrue(sql.contains("""COPY "ns"."tbl""""))
        assertTrue(sql.contains("FROM 's3://bucket/path/file.csv.gz'"))
        assertTrue(
            sql.contains("CREDENTIALS 'aws_access_key_id=AKIATEST;aws_secret_access_key=secret123'")
        )
        assertTrue(sql.contains("CSV GZIP"))
        assertTrue(sql.contains("REGION 'us-east-1'"))
        assertTrue(sql.contains("TIMEFORMAT 'auto'"))
        assertTrue(sql.contains("ROUNDEC"))
        assertTrue(sql.contains("IGNOREHEADER 1"))
        assertTrue(sql.contains("EMPTYASNULL"))
    }

    @Test
    fun `getTableSchema queries information_schema`() {
        val sql = sqlGenerator.getTableSchema(TableName(namespace = "my_schema", name = "my_table"))

        assertTrue(sql.contains("SELECT column_name, data_type, is_nullable"))
        assertTrue(sql.contains("FROM information_schema.columns"))
        assertTrue(sql.contains("table_schema = 'my_schema'"))
        assertTrue(sql.contains("table_name = 'my_table'"))
        assertTrue(sql.contains("ORDER BY ordinal_position"))
    }

    // ================================================================
    // Edge cases
    // ================================================================

    @Test
    fun `blank namespace is passed through without defaulting`() {
        val sql = sqlGenerator.dropTable(TableName(namespace = "", name = "tbl"))
        assertEquals("""DROP TABLE IF EXISTS ""."tbl";""", sql)
    }

    // ================================================================
    // Drop CASCADE tests
    // ================================================================

    @Nested
    inner class DropCascadeTests {

        private lateinit var cascadeGenerator: RedshiftSqlGenerator

        @BeforeEach
        fun setUp() {
            cascadeGenerator = RedshiftSqlGenerator(mockConfig(dropCascade = true))
        }

        @Test
        fun `dropTable with cascade appends CASCADE`() {
            val sql = cascadeGenerator.dropTable(TableName(namespace = "ns", name = "tbl"))
            assertEquals("""DROP TABLE IF EXISTS "ns"."tbl" CASCADE;""", sql)
        }

        @Test
        fun `createTable with replace and cascade appends CASCADE to DROP`() {
            val finalSchema =
                mapOf(
                    "id" to ColumnType("bigint", false),
                    "name" to ColumnType("varchar(65535)", true),
                )
            val stream = mockStream(finalSchema)
            val tableName = TableName(namespace = "public", name = "users")

            val sql = cascadeGenerator.createTable(stream, tableName, replace = true)

            assertTrue(sql.contains("""DROP TABLE IF EXISTS "public"."users" CASCADE;"""))
            assertTrue(sql.contains("BEGIN TRANSACTION;"))
            assertTrue(sql.contains("CREATE TABLE IF NOT EXISTS"))
            assertTrue(sql.contains("COMMIT;"))
        }

        @Test
        fun `createTable without replace and cascade does not add CASCADE`() {
            val finalSchema = mapOf("id" to ColumnType("bigint", false))
            val stream = mockStream(finalSchema)
            val tableName = TableName(namespace = "public", name = "users")

            val sql = cascadeGenerator.createTable(stream, tableName, replace = false)

            assertFalse(sql.contains("CASCADE"))
            assertFalse(sql.contains("DROP TABLE"))
        }

        @Test
        fun `overwriteTable with cascade appends CASCADE to DROP`() {
            val source = TableName(namespace = "ns", name = "tmp")
            val target = TableName(namespace = "ns", name = "final")

            val sql = cascadeGenerator.overwriteTable(source, target)

            assertTrue(sql.contains("""DROP TABLE IF EXISTS "ns"."final" CASCADE;"""))
            assertTrue(sql.contains("""ALTER TABLE "ns"."tmp" RENAME TO "final""""))
        }

        @Test
        fun `matchSchemas removes columns with CASCADE`() {
            val tableName = TableName(namespace = "ns", name = "tbl")
            val sql =
                cascadeGenerator.matchSchemas(
                    tableName,
                    columnsToAdd = emptyMap(),
                    columnsToRemove = mapOf("old_col" to ColumnType("varchar", true)),
                    columnsToModify = emptyMap(),
                )

            assertTrue(sql.contains("""ALTER TABLE "ns"."tbl" DROP COLUMN "old_col" CASCADE;"""))
        }

        @Test
        fun `matchSchemas type change drops column with CASCADE`() {
            val tableName = TableName(namespace = "ns", name = "tbl")
            val sql =
                cascadeGenerator.matchSchemas(
                    tableName,
                    columnsToAdd = emptyMap(),
                    columnsToRemove = emptyMap(),
                    columnsToModify =
                        mapOf(
                            "num_col" to
                                ColumnTypeChange(
                                    originalType = ColumnType("bigint", false),
                                    newType = ColumnType("decimal(38,9)", false),
                                )
                        ),
                )

            assertTrue(sql.contains("""DROP COLUMN "num_col" CASCADE;"""))
            assertTrue(sql.contains("""RENAME COLUMN "_airbyte_tmp_num_col" TO "num_col";"""))
        }

        @Test
        fun `upsertTable temp table drop does not use CASCADE even when enabled`() {
            val finalSchema =
                mapOf(
                    "id" to ColumnType("bigint", false),
                    "name" to ColumnType("varchar(65535)", true),
                    "updated_at" to ColumnType("timestamptz", true),
                )
            val stream =
                mockStream(
                    finalSchema = finalSchema,
                    primaryKey = listOf(listOf("id")),
                    cursor = listOf("updated_at"),
                )

            val source = TableName(namespace = "ns", name = "staging")
            val target = TableName(namespace = "ns", name = "final")

            val sql = cascadeGenerator.upsertTable(stream, source, target)

            // The temp table drop should NOT have CASCADE (temp tables can't have dependent views)
            val dedup = """"_airbyte_dedup_ns_staging""""
            assertTrue(sql.contains("DROP TABLE IF EXISTS $dedup;"))
            assertFalse(sql.contains("DROP TABLE IF EXISTS $dedup CASCADE;"))
        }
    }
}
