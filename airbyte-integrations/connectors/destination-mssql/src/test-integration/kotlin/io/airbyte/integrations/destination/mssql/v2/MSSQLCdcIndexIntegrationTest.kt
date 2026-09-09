/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql.v2

import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.NamespaceMapper
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.StringType
import java.sql.Connection
import java.sql.DriverManager
import org.junit.jupiter.api.AfterAll
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Test

/**
 * Integration tests that verify the CDC index fix against a real MSSQL Server instance.
 *
 * These tests validate that when a CDC stream includes `_ab_cdc_deleted_at`, the column is typed as
 * `varchar(200)` (not `varchar(max)`), allowing MSSQL to create a secondary index on it. This
 * directly tests the fix for the bug where `CREATE TABLE` failed with:
 * ```
 * Column '_ab_cdc_deleted_at' in table '...' is of a type that is invalid for use as a key column
 * in an index.
 * ```
 */
class MSSQLCdcIndexIntegrationTest {

    companion object {
        private const val TEST_SCHEMA = "cdc_index_test"

        @JvmStatic
        @BeforeAll
        fun beforeAll() {
            MSSQLContainerHelper.start()
            getConnection().use { conn ->
                // Create test schema
                conn.createStatement().use { stmt ->
                    stmt.execute(
                        """
                        IF NOT EXISTS (SELECT name FROM sys.schemas WHERE name = '$TEST_SCHEMA')
                        BEGIN
                            EXEC ('CREATE SCHEMA [$TEST_SCHEMA]');
                        END
                        """.trimIndent()
                    )
                }
            }
        }

        @JvmStatic
        @AfterAll
        fun afterAll() {
            getConnection().use { conn ->
                conn.createStatement().use { stmt ->
                    // Drop all tables in the test schema, then drop the schema
                    stmt.execute(
                        """
                        DECLARE @sql NVARCHAR(MAX) = N'';
                        SELECT @sql += 'DROP TABLE ' + QUOTENAME(s.name) + '.' + QUOTENAME(t.name) + ';'
                        FROM sys.schemas s
                        JOIN sys.tables t ON s.schema_id = t.schema_id
                        WHERE s.name = '$TEST_SCHEMA';
                        EXEC sp_executesql @sql;
                        """.trimIndent()
                    )
                    stmt.execute("DROP SCHEMA IF EXISTS [$TEST_SCHEMA]")
                }
            }
        }

        private fun getConnection(): Connection {
            val host = MSSQLContainerHelper.getHost()
            val port = MSSQLContainerHelper.getPort()
            val user = MSSQLContainerHelper.getUsername()
            val password = MSSQLContainerHelper.getPassword()
            return DriverManager.getConnection(
                "jdbc:sqlserver://$host:$port;encrypt=false;trustServerCertificate=true",
                user,
                password,
            )
        }

        private fun makeStream(
            name: String,
            importType: io.airbyte.cdk.load.command.ImportType,
            columns: LinkedHashMap<String, FieldType>,
        ): DestinationStream {
            return DestinationStream(
                unmappedNamespace = TEST_SCHEMA,
                unmappedName = name,
                importType = importType,
                schema = ObjectType(properties = columns),
                generationId = 1,
                minimumGenerationId = 0,
                syncId = 42,
                namespaceMapper = NamespaceMapper(),
            )
        }

        /**
         * Query INFORMATION_SCHEMA.COLUMNS for a given table and return a map of column_name ->
         * data_type (e.g. "varchar") and a map of column_name -> character_maximum_length.
         */
        private fun getColumnInfo(
            conn: Connection,
            tableName: String,
        ): Map<String, Pair<String, Long?>> {
            val result = mutableMapOf<String, Pair<String, Long?>>()
            conn
                .prepareStatement(
                    """
                    SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_SCHEMA = ? AND TABLE_NAME = ?
                    ORDER BY ORDINAL_POSITION
                    """.trimIndent()
                )
                .use { stmt ->
                    stmt.setString(1, TEST_SCHEMA)
                    stmt.setString(2, tableName)
                    stmt.executeQuery().use { rs ->
                        while (rs.next()) {
                            val colName = rs.getString("COLUMN_NAME")
                            val dataType = rs.getString("DATA_TYPE")
                            val maxLength =
                                rs.getObject("CHARACTER_MAXIMUM_LENGTH") as? Long
                                    ?: rs.getLong("CHARACTER_MAXIMUM_LENGTH").let {
                                        if (rs.wasNull()) null else it
                                    }
                            result[colName] = Pair(dataType, maxLength)
                        }
                    }
                }
            return result
        }

        /**
         * Query sys.indexes to get the list of non-clustered index names and their columns for a
         * given table.
         */
        private fun getIndexColumns(
            conn: Connection,
            tableName: String,
        ): Map<String, List<String>> {
            val result = mutableMapOf<String, MutableList<String>>()
            conn
                .prepareStatement(
                    """
                    SELECT i.name AS index_name, c.name AS column_name
                    FROM sys.indexes i
                    JOIN sys.index_columns ic ON i.object_id = ic.object_id AND i.index_id = ic.index_id
                    JOIN sys.columns c ON ic.object_id = c.object_id AND ic.column_id = c.column_id
                    WHERE i.object_id = OBJECT_ID(? + '.' + ?)
                      AND i.type_desc = 'NONCLUSTERED'
                    ORDER BY i.name, ic.key_ordinal
                    """.trimIndent()
                )
                .use { stmt ->
                    stmt.setString(1, TEST_SCHEMA)
                    stmt.setString(2, tableName)
                    stmt.executeQuery().use { rs ->
                        while (rs.next()) {
                            val indexName = rs.getString("index_name")
                            val columnName = rs.getString("column_name")
                            result.getOrPut(indexName) { mutableListOf() }.add(columnName)
                        }
                    }
                }
            return result
        }
    }

    @Test
    fun `CDC Append stream creates table with VARCHAR 200 for _ab_cdc_deleted_at and a secondary index`() {
        val tableName = "cdc_append_test"
        val columns =
            linkedMapOf(
                "id" to FieldType(IntegerType, true),
                "name" to FieldType(StringType, true),
                MSSQLQueryBuilder.AIRBYTE_CDC_DELETED_AT to FieldType(StringType, true),
            )
        val stream = makeStream(tableName, Append, columns)
        val builder = MSSQLQueryBuilder(defaultSchema = TEST_SCHEMA, stream = stream)

        assertTrue(builder.hasCdc, "Stream with _ab_cdc_deleted_at should be detected as CDC")

        getConnection().use { conn ->
            // This is the critical call — it was failing before the fix with:
            // "Column '_ab_cdc_deleted_at' is of a type that is invalid for use as a key column"
            builder.createTableIfNotExists(conn)

            // Verify column types
            val columnInfo = getColumnInfo(conn, tableName)

            // _ab_cdc_deleted_at must be VARCHAR(200), not VARCHAR(MAX) (-1 in MSSQL)
            val cdcColInfo = columnInfo[MSSQLQueryBuilder.AIRBYTE_CDC_DELETED_AT]
            assertEquals(
                "varchar",
                cdcColInfo?.first,
                "_ab_cdc_deleted_at should be a varchar type",
            )
            assertEquals(
                200L,
                cdcColInfo?.second,
                "_ab_cdc_deleted_at should be VARCHAR(200), not VARCHAR(MAX). " +
                    "VARCHAR(MAX) would show as -1.",
            )

            // Non-indexed string column "name" should be VARCHAR(MAX)
            val nameColInfo = columnInfo["name"]
            assertEquals("varchar", nameColInfo?.first, "name should be a varchar type")
            assertEquals(
                -1L,
                nameColInfo?.second,
                "Non-indexed string column 'name' should be VARCHAR(MAX) (shown as -1)",
            )

            // Verify that a non-clustered index exists that includes _ab_cdc_deleted_at
            val indexes = getIndexColumns(conn, tableName)
            val cdcIndexExists =
                indexes.values.any { cols ->
                    cols.contains(MSSQLQueryBuilder.AIRBYTE_CDC_DELETED_AT)
                }
            assertTrue(
                cdcIndexExists,
                "A non-clustered index on _ab_cdc_deleted_at should exist. " +
                    "Found indexes: $indexes",
            )
        }
    }

    @Test
    fun `non-CDC Append stream creates table with VARCHAR MAX for all string columns`() {
        val tableName = "non_cdc_append_test"
        val columns =
            linkedMapOf(
                "id" to FieldType(IntegerType, true),
                "description" to FieldType(StringType, true),
            )
        val stream = makeStream(tableName, Append, columns)
        val builder = MSSQLQueryBuilder(defaultSchema = TEST_SCHEMA, stream = stream)

        assertFalse(
            builder.hasCdc,
            "Stream without _ab_cdc_deleted_at should not be detected as CDC"
        )

        getConnection().use { conn ->
            builder.createTableIfNotExists(conn)

            val columnInfo = getColumnInfo(conn, tableName)

            // All string columns should be VARCHAR(MAX) since nothing is indexed
            val descColInfo = columnInfo["description"]
            assertEquals("varchar", descColInfo?.first)
            assertEquals(
                -1L,
                descColInfo?.second,
                "Non-indexed string column should be VARCHAR(MAX) (shown as -1)",
            )

            // No non-clustered indexes should exist (Append has no uniqueness key)
            val indexes = getIndexColumns(conn, tableName)
            assertTrue(
                indexes.isEmpty(),
                "Non-CDC Append stream should have no non-clustered indexes. Found: $indexes",
            )
        }
    }

    @Test
    fun `CDC Dedupe stream creates table with VARCHAR 200 for both primary key and _ab_cdc_deleted_at`() {
        val tableName = "cdc_dedupe_test"
        val columns =
            linkedMapOf(
                "id" to FieldType(StringType, true),
                "name" to FieldType(StringType, true),
                MSSQLQueryBuilder.AIRBYTE_CDC_DELETED_AT to FieldType(StringType, true),
            )
        val stream =
            makeStream(
                tableName,
                Dedupe(primaryKey = listOf(listOf("id")), cursor = emptyList()),
                columns,
            )
        val builder = MSSQLQueryBuilder(defaultSchema = TEST_SCHEMA, stream = stream)

        assertTrue(builder.hasCdc)

        getConnection().use { conn ->
            builder.createTableIfNotExists(conn)

            val columnInfo = getColumnInfo(conn, tableName)

            // Primary key "id" must be VARCHAR(200) since it's in the uniqueness key
            val idColInfo = columnInfo["id"]
            assertEquals("varchar", idColInfo?.first)
            assertEquals(
                200L,
                idColInfo?.second,
                "Dedupe primary key 'id' should be VARCHAR(200)",
            )

            // _ab_cdc_deleted_at must also be VARCHAR(200)
            val cdcColInfo = columnInfo[MSSQLQueryBuilder.AIRBYTE_CDC_DELETED_AT]
            assertEquals("varchar", cdcColInfo?.first)
            assertEquals(
                200L,
                cdcColInfo?.second,
                "_ab_cdc_deleted_at should be VARCHAR(200) on CDC Dedupe streams",
            )

            // Non-indexed string column "name" should remain VARCHAR(MAX)
            val nameColInfo = columnInfo["name"]
            assertEquals("varchar", nameColInfo?.first)
            assertEquals(
                -1L,
                nameColInfo?.second,
                "Non-indexed string column 'name' should remain VARCHAR(MAX)",
            )

            // Verify indexes: should have index on "id" (uniqueness key) and on _ab_cdc_deleted_at
            val indexes = getIndexColumns(conn, tableName)
            val hasIdIndex = indexes.values.any { cols -> cols.contains("id") }
            val hasCdcIndex =
                indexes.values.any { cols ->
                    cols.contains(MSSQLQueryBuilder.AIRBYTE_CDC_DELETED_AT)
                }
            assertTrue(hasIdIndex, "Index on primary key 'id' should exist. Found: $indexes")
            assertTrue(
                hasCdcIndex,
                "Index on _ab_cdc_deleted_at should exist. Found: $indexes",
            )
        }
    }
}
