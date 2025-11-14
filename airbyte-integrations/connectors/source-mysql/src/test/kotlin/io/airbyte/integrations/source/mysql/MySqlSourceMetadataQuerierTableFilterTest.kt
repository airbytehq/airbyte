/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mysql

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.check.JdbcCheckQueries
import io.airbyte.cdk.discover.MetadataQuerier
import io.airbyte.cdk.jdbc.DefaultJdbcConstants
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import java.sql.Connection
import java.sql.Statement
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.Timeout
import org.junit.jupiter.api.assertThrows
import org.testcontainers.containers.MySQLContainer

class MySqlSourceMetadataQuerierTableFilterTest {
    companion object {
        val dbContainer: MySQLContainer<*> = MySqlContainerFactory.shared(imageName = "mysql:9.2.0")

        // In MySQL, database == schema. We test within 'test' database
        val databaseName = "test"
        val tableNames = listOf("orders", "customers", "products", "invoices")

        val factory =
            MySqlSourceMetadataQuerier.Factory(
                constants = DefaultJdbcConstants(),
                selectQueryGenerator = MySqlSourceOperations(),
                fieldTypeMapper = MySqlSourceOperations(),
                checkQueries = JdbcCheckQueries(),
            )

        @JvmStatic
        @BeforeAll
        @Timeout(value = 300)
        fun setupDatabase() {
            val config: MySqlSourceConfiguration =
                MySqlSourceConfigurationFactory().make(MySqlContainerFactory.config(dbContainer))

            val connectionFactory = JdbcConnectionFactory(config)

            connectionFactory.get().use { connection: Connection ->
                connection.isReadOnly = false
                connection.createStatement().use {
                    it.execute("CREATE DATABASE IF NOT EXISTS test")
                }
                connection.createStatement().use { it.execute("USE test") }

                // Create test tables
                tableNames.forEach { tableName ->
                    connection.createStatement().use { stmt: Statement ->
                        stmt.execute(
                            "CREATE TABLE IF NOT EXISTS $tableName (id INT PRIMARY KEY, name VARCHAR(255))"
                        )
                    }
                }
            }
        }
    }

    @Test
    fun testNoFilter() {
        // When no filters are provided, all tables should be returned
        val configPojo =
            MySqlContainerFactory.config(dbContainer).apply {
                database = databaseName
                tableFilters = null
            }

        val config: MySqlSourceConfiguration = MySqlSourceConfigurationFactory().make(configPojo)

        factory.session(config).use { mdq: MetadataQuerier ->
            // Verify all tables are returned
            val streamNames = mdq.streamNames(databaseName).map { it.name }.sorted()
            Assertions.assertEquals(tableNames.sorted(), streamNames)
        }
    }

    @Test
    fun testTableFilters() {
        val tableFilter =
            TableFilter().apply {
                databaseName = "test"
                patterns = listOf("customers", "orders")
            }

        val configPojo =
            MySqlContainerFactory.config(dbContainer).apply {
                database = databaseName
                tableFilters = listOf(tableFilter)
            }

        val config: MySqlSourceConfiguration = MySqlSourceConfigurationFactory().make(configPojo)

        factory.session(config).use { mdq: MetadataQuerier ->
            val querier = mdq as MySqlSourceMetadataQuerier

            // Check that memoizedTableNames only contains filtered tables
            val filteredTables =
                querier.base.memoizedTableNames
                    .filter { (it.schema ?: it.catalog) == databaseName }
                    .map { it.name }
                    .toSet()

            Assertions.assertEquals(setOf("customers", "orders"), filteredTables)
        }
    }

    @Test
    fun testNoMatchingTables() {
        // Test pattern that doesn't match any tables
        val tableFilter =
            TableFilter().apply {
                databaseName = "test"
                patterns = listOf("nonexistent%")
            }

        val configPojo =
            MySqlContainerFactory.config(dbContainer).apply {
                database = databaseName
                tableFilters = listOf(tableFilter)
            }

        val config: MySqlSourceConfiguration = MySqlSourceConfigurationFactory().make(configPojo)

        factory.session(config).use { mdq: MetadataQuerier ->
            val querier = mdq as MySqlSourceMetadataQuerier
            val filteredTables =
                querier.base.memoizedTableNames
                    .filter { (it.schema ?: it.catalog) == databaseName }
                    .map { it.name }
                    .toSet()

            Assertions.assertEquals(emptySet<String>(), filteredTables)
        }
    }

    @Test
    fun testFilterSchemaNotInConfiguredSchemas() {
        // Filter references a schema that is not in the configured schemas list
        val tableFilter =
            TableFilter().apply {
                databaseName = "nonexistent_schema"
                patterns = listOf("orders", "customers")
            }

        val configPojo =
            MySqlContainerFactory.config(dbContainer).apply {
                database = databaseName
                tableFilters = listOf(tableFilter)
            }

        assertThrows<ConfigErrorException> {
            MySqlSourceConfigurationFactory().makeWithoutExceptionHandling(configPojo)
        }
    }

    @Test
    fun testWildcardPatterns() {
        // Test SQL LIKE wildcards with MySQL
        val tableFilter =
            TableFilter().apply {
                databaseName = "test"
                patterns = listOf("c%") // Should match 'customers'
            }

        val configPojo =
            MySqlContainerFactory.config(dbContainer).apply {
                database = databaseName
                tableFilters = listOf(tableFilter)
            }

        val config: MySqlSourceConfiguration = MySqlSourceConfigurationFactory().make(configPojo)

        factory.session(config).use { mdq: MetadataQuerier ->
            val querier = mdq as MySqlSourceMetadataQuerier
            val filteredTables =
                querier.base.memoizedTableNames
                    .filter { (it.schema ?: it.catalog) == databaseName }
                    .map { it.name }
                    .toSet()

            Assertions.assertEquals(setOf("customers"), filteredTables)
        }
    }

    @Test
    fun testMultiplePatternsInOneFilter() {
        // Test multiple patterns for the same schema
        val tableFilter =
            TableFilter().apply {
                databaseName = "test"
                patterns = listOf("orders", "products", "invoices")
            }

        val configPojo =
            MySqlContainerFactory.config(dbContainer).apply {
                database = databaseName
                tableFilters = listOf(tableFilter)
            }

        val config: MySqlSourceConfiguration = MySqlSourceConfigurationFactory().make(configPojo)

        factory.session(config).use { mdq: MetadataQuerier ->
            val querier = mdq as MySqlSourceMetadataQuerier
            val filteredTables =
                querier.base.memoizedTableNames
                    .filter { (it.schema ?: it.catalog) == databaseName }
                    .map { it.name }
                    .toSet()

            Assertions.assertEquals(setOf("orders", "products", "invoices"), filteredTables)
        }
    }
}
