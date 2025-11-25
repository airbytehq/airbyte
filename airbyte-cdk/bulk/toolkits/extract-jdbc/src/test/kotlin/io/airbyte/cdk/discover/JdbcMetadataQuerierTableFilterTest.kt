/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.discover

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.check.JdbcCheckQueries
import io.airbyte.cdk.command.TableFilter
import io.airbyte.cdk.h2.H2TestFixture
import io.airbyte.cdk.h2source.H2SourceConfiguration
import io.airbyte.cdk.h2source.H2SourceConfigurationFactory
import io.airbyte.cdk.h2source.H2SourceConfigurationSpecification
import io.airbyte.cdk.h2source.H2SourceOperations
import io.airbyte.cdk.jdbc.DefaultJdbcConstants
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows

class JdbcMetadataQuerierTableFilterTest {
    val h2 = H2TestFixture()

    // Create schema and table names for testing
    val schemaNames = listOf("SCHEMA1", "SCHEMA2")
    val tableNames = listOf("ORDERS", "CUSTOMERS", "PRODUCTS", "INVOICES")

    init {
        // Create two schemas
        schemaNames.forEach { schemaName ->
            h2.execute("CREATE SCHEMA $schemaName")

            // Create tables in each schema
            tableNames.forEach { tableName ->
                h2.execute(
                    "CREATE TABLE $schemaName.$tableName (ID INT PRIMARY KEY, NAME VARCHAR(255))"
                )
            }
        }
    }

    val factory =
        JdbcMetadataQuerier.Factory(
            selectQueryGenerator = H2SourceOperations(),
            fieldTypeMapper = H2SourceOperations(),
            checkQueries = JdbcCheckQueries(),
            constants = DefaultJdbcConstants(),
        )

    @Test
    fun testNoFilter() {
        // When no filters are provided, all tables should be returned
        val configPojo =
            H2SourceConfigurationSpecification().apply {
                port = h2.port
                database = h2.database
                schemas = schemaNames
                tableFilters = null
            }

        val config: H2SourceConfiguration = H2SourceConfigurationFactory().make(configPojo)

        factory.session(config).use { mdq: MetadataQuerier ->
            // Verify all tables are returned for each schema
            schemaNames.forEach { schema ->
                val streamNames = mdq.streamNames(schema).map { it.name }.sorted()
                Assertions.assertEquals(tableNames.sorted(), streamNames)
            }
        }
    }

    @Test
    fun testTableFilters() {
        val tableFilter1 =
            TableFilter().apply {
                schemaName = "SCHEMA1"
                patterns = listOf("CUSTOMERS")
            }

        val tableFilter2 =
            TableFilter().apply {
                schemaName = "SCHEMA2"
                patterns = listOf("ORDERS")
            }

        val configPojo =
            H2SourceConfigurationSpecification().apply {
                port = h2.port
                database = h2.database
                schemas = schemaNames
                tableFilters = listOf(tableFilter1, tableFilter2)
            }

        val config: H2SourceConfiguration = H2SourceConfigurationFactory().make(configPojo)

        factory.session(config).use { mdq: MetadataQuerier ->
            val querier = mdq as JdbcMetadataQuerier

            // Check that memoizedTableNames only contains filtered tables
            val schema1Tables =
                querier.memoizedTableNames.filter { it.schema == "SCHEMA1" }.map { it.name }.toSet()

            Assertions.assertEquals(setOf("CUSTOMERS"), schema1Tables)

            val schema2Tables =
                querier.memoizedTableNames.filter { it.schema == "SCHEMA2" }.map { it.name }.toSet()

            Assertions.assertEquals(setOf("ORDERS"), schema2Tables)
        }
    }

    @Test
    fun testSelectiveSchemaFiltering() {
        // Apply filter to ONLY SCHEMA1
        // SCHEMA2 should return ALL tables
        val tableFilter =
            TableFilter().apply {
                schemaName = "SCHEMA1"
                patterns = listOf("CUSTOMERS", "ORDERS")
            }

        val configPojo =
            H2SourceConfigurationSpecification().apply {
                port = h2.port
                database = h2.database
                schemas = schemaNames
                tableFilters = listOf(tableFilter)
            }

        val config: H2SourceConfiguration = H2SourceConfigurationFactory().make(configPojo)

        factory.session(config).use { mdq: MetadataQuerier ->
            val querier = mdq as JdbcMetadataQuerier

            // Verify SCHEMA1 has only filtered tables
            val schema1Tables =
                querier.memoizedTableNames.filter { it.schema == "SCHEMA1" }.map { it.name }.toSet()

            Assertions.assertEquals(
                setOf("CUSTOMERS", "ORDERS"),
                schema1Tables,
                "SCHEMA1 should have only filtered tables (CUSTOMERS, ORDERS)"
            )

            // Verify SCHEMA2 (without filter) has ALL tables
            val schema2Tables =
                querier.memoizedTableNames.filter { it.schema == "SCHEMA2" }.map { it.name }.toSet()

            Assertions.assertEquals(
                tableNames.toSet(),
                schema2Tables,
                "SCHEMA2 (without filter) should have ALL tables"
            )
        }
    }

    @Test
    fun testNoMatchingTables() {
        // Test pattern that doesn't match any tables
        val tableFilter =
            TableFilter().apply {
                schemaName = "SCHEMA1"
                patterns = listOf("NONEXISTENT%")
            }

        val configPojo =
            H2SourceConfigurationSpecification().apply {
                port = h2.port
                database = h2.database
                schemas = schemaNames
                tableFilters = listOf(tableFilter)
            }

        val config: H2SourceConfiguration = H2SourceConfigurationFactory().make(configPojo)

        factory.session(config).use { mdq: MetadataQuerier ->
            val querier = mdq as JdbcMetadataQuerier
            val schema1Tables =
                querier.memoizedTableNames.filter { it.schema == "SCHEMA1" }.map { it.name }.toSet()

            Assertions.assertEquals(emptySet<String>(), schema1Tables)
        }
    }

    @Test
    fun testFilterSchemaNotInConfiguredSchemas() {
        // Filter references a schema that is not in the configured schemas list
        val tableFilter =
            TableFilter().apply {
                schemaName = "NONEXISTENT_SCHEMA"
                patterns = listOf("ORDERS", "CUSTOMERS")
            }

        val configPojo =
            H2SourceConfigurationSpecification().apply {
                port = h2.port
                database = h2.database
                schemas = schemaNames
                tableFilters = listOf(tableFilter)
            }

        assertThrows<ConfigErrorException> {
            H2SourceConfigurationFactory().makeWithoutExceptionHandling(configPojo)
        }
    }
}
