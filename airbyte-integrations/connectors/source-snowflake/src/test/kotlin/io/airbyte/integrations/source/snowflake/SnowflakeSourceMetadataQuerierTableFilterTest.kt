/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.snowflake

import io.airbyte.cdk.check.JdbcCheckQueries
import io.airbyte.cdk.command.TableFilter
import io.airbyte.cdk.discover.JdbcMetadataQuerier
import io.airbyte.cdk.jdbc.DefaultJdbcConstants
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.cdk.read.SelectQueryGenerator
import io.mockk.every
import io.mockk.mockk
import java.sql.Connection
import java.sql.DatabaseMetaData
import java.sql.ResultSet
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

/**
 * Tests for SnowflakeSourceMetadataQuerier table filtering behavior.
 *
 * This test suite validates the complex table filtering logic when schema is null, ensuring that:
 * - Schemas with filters only return tables matching the filter patterns
 * - Schemas without filters return ALL tables (unfiltered discovery)
 * - The behavior is correct across different filtering scenarios
 */
class SnowflakeSourceMetadataQuerierTableFilterTest {

    private fun createMockConnection(
        namespace: String,
        schemasAndTables: Map<String, List<String>>
    ): Connection {
        val conn = mockk<Connection>()
        val dbmd = mockk<DatabaseMetaData>()

        every { conn.metaData } returns dbmd

        // Mock getTables calls
        every { dbmd.getTables(namespace, null, null, null) } answers
            {
                createTableResultSet(namespace, schemasAndTables)
            }

        // Mock getTables with specific schema and pattern
        schemasAndTables.forEach { (schema, tables) ->
            // Mock with null pattern (get all tables)
            every { dbmd.getTables(namespace, schema, null, null) } answers
                {
                    createTableResultSet(namespace, mapOf(schema to tables))
                }

            // Mock with exact table name matches
            tables.forEach { table ->
                every { dbmd.getTables(namespace, schema, table, null) } answers
                    {
                        createTableResultSet(namespace, mapOf(schema to listOf(table)))
                    }
                // Also mock lowercase schema for case insensitivity tests
                every { dbmd.getTables(namespace, schema.lowercase(), table, null) } answers
                    {
                        createTableResultSet(namespace, mapOf(schema to listOf(table)))
                    }
            }

            // Mock pattern matching (simplified - just exact matches and prefix matches for
            // testing)
            every {
                dbmd.getTables(namespace, schema, match { !tables.contains(it) }, null)
            } answers
                {
                    val pattern = arg<String>(2)
                    val matchingTables =
                        if (pattern.endsWith("%")) {
                            val prefix = pattern.removeSuffix("%")
                            tables.filter { it.startsWith(prefix) }
                        } else {
                            emptyList()
                        }
                    createTableResultSet(namespace, mapOf(schema to matchingTables))
                }

            // Also mock lowercase schema for case insensitivity
            every { dbmd.getTables(namespace, schema.lowercase(), match { true }, null) } answers
                {
                    val pattern = arg<String>(2)
                    val matchingTables =
                        if (pattern.endsWith("%")) {
                            val prefix = pattern.removeSuffix("%")
                            tables.filter { it.startsWith(prefix) }
                        } else if (tables.contains(pattern)) {
                            listOf(pattern)
                        } else {
                            emptyList()
                        }
                    createTableResultSet(namespace, mapOf(schema to matchingTables))
                }
        }

        // Mock getColumns, getPrimaryKeys (returning empty for simplicity)
        every { dbmd.getColumns(any(), any(), any(), any()) } returns createEmptyResultSet()
        every { dbmd.getPrimaryKeys(any(), any(), any()) } returns createEmptyResultSet()

        return conn
    }

    private fun createTableResultSet(
        catalog: String,
        schemasAndTables: Map<String, List<String>>
    ): ResultSet {
        val rs = mockk<ResultSet>()
        val allTables =
            schemasAndTables.flatMap { (schema, tables) ->
                tables.map { Triple(catalog, schema, it) }
            }

        var currentIndex = -1

        every { rs.next() } answers
            {
                currentIndex++
                currentIndex < allTables.size
            }

        every { rs.getString("TABLE_CAT") } answers { allTables.getOrNull(currentIndex)?.first }

        every { rs.getString("TABLE_SCHEM") } answers { allTables.getOrNull(currentIndex)?.second }

        every { rs.getString("TABLE_NAME") } answers { allTables.getOrNull(currentIndex)?.third }

        every { rs.getString("TABLE_TYPE") } returns "TABLE"

        every { rs.close() } returns Unit

        return rs
    }

    private fun createEmptyResultSet(): ResultSet {
        val rs = mockk<ResultSet>()
        every { rs.next() } returns false
        every { rs.close() } returns Unit
        return rs
    }

    private fun createMetadataQuerier(
        conn: Connection,
        schema: String?,
        tableFilters: List<TableFilter> = emptyList()
    ): SnowflakeSourceMetadataQuerier {
        val config = mockk<SnowflakeSourceConfiguration>()
        every { config.namespaces } returns setOf("TEST_DATABASE")
        every { config.tableFilters } returns tableFilters
        every { config.checkPrivileges } returns false
        every { config.schemas } returns (schema?.let { listOf(it) } ?: emptyList())

        val constants = DefaultJdbcConstants()
        val selectQueryGenerator = mockk<SelectQueryGenerator>()
        val fieldTypeMapper = mockk<JdbcMetadataQuerier.FieldTypeMapper>()
        val checkQueries = mockk<JdbcCheckQueries>()
        val jdbcConnectionFactory = mockk<JdbcConnectionFactory>()

        every { jdbcConnectionFactory.get() } returns conn

        val base =
            JdbcMetadataQuerier(
                constants,
                config,
                selectQueryGenerator,
                fieldTypeMapper,
                checkQueries,
                jdbcConnectionFactory
            )

        return SnowflakeSourceMetadataQuerier(base)
    }

    @Test
    fun testNoSchemaNoFilters() {
        // When schema is null and no filters, all tables from all schemas should be returned
        val schemasAndTables =
            mapOf(
                "PUBLIC" to listOf("CUSTOMERS", "ORDERS", "PRODUCTS"),
                "PRIVATE" to listOf("INTERNAL_USERS", "AUDIT_LOG")
            )

        val conn = createMockConnection("TEST_DATABASE", schemasAndTables)
        val querier = createMetadataQuerier(conn, schema = null, tableFilters = emptyList())

        val allTables = querier.memoizedTableNames.map { it.schema to it.name }.toSet()

        val expectedTables =
            setOf(
                "PUBLIC" to "CUSTOMERS",
                "PUBLIC" to "ORDERS",
                "PUBLIC" to "PRODUCTS",
                "PRIVATE" to "INTERNAL_USERS",
                "PRIVATE" to "AUDIT_LOG"
            )

        assertEquals(expectedTables, allTables)
    }

    @Test
    fun testNoSchemaWithFilterOnOneSchema() {
        // When schema is null and filter is applied to one schema (PUBLIC),
        // PUBLIC should be filtered, PRIVATE should return all tables
        val schemasAndTables =
            mapOf(
                "PUBLIC" to listOf("CUSTOMERS", "ORDERS", "PRODUCTS"),
                "PRIVATE" to listOf("INTERNAL_USERS", "AUDIT_LOG")
            )

        val filter =
            TableFilter().apply {
                schemaName = "PUBLIC"
                patterns = listOf("CUSTOMERS", "ORDERS")
            }

        val conn = createMockConnection("TEST_DATABASE", schemasAndTables)
        val querier = createMetadataQuerier(conn, schema = null, tableFilters = listOf(filter))

        val publicTables =
            querier.memoizedTableNames.filter { it.schema == "PUBLIC" }.map { it.name }.toSet()

        val privateTables =
            querier.memoizedTableNames.filter { it.schema == "PRIVATE" }.map { it.name }.toSet()

        // PUBLIC should only have filtered tables
        assertEquals(
            setOf("CUSTOMERS", "ORDERS"),
            publicTables,
            "PUBLIC schema should only have filtered tables"
        )

        // PRIVATE should have ALL tables (unfiltered discovery)
        assertEquals(
            setOf("INTERNAL_USERS", "AUDIT_LOG"),
            privateTables,
            "PRIVATE schema (without filter) should have ALL tables"
        )
    }

    @Test
    fun testWithSchemaSpecifiedAndFilter() {
        // When schema is specified (not null), only that schema should be queried
        val schemasAndTables = mapOf("PUBLIC" to listOf("CUSTOMERS", "ORDERS", "PRODUCTS"))

        val filter =
            TableFilter().apply {
                schemaName = "PUBLIC"
                patterns = listOf("CUSTOMERS", "ORDERS")
            }

        val conn = createMockConnection("TEST_DATABASE", schemasAndTables)
        val querier = createMetadataQuerier(conn, schema = "PUBLIC", tableFilters = listOf(filter))

        val allTables = querier.memoizedTableNames.map { it.name }.toSet()

        // Only filtered tables should be returned
        assertEquals(setOf("CUSTOMERS", "ORDERS"), allTables)
    }
}
