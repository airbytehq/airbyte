/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mysql

import io.airbyte.cdk.ConfigErrorException
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows

class MySqlSourceTableIncludeRegexTest {

    private fun pojo(
        database: String?,
        regex: List<String>?,
        filters: List<TableFilter>? = null,
    ): MySqlSourceConfigurationSpecification =
        MySqlSourceConfigurationSpecification().apply {
            host = "localhost"
            port = 3306
            username = "user"
            password = "password"
            this.database = database
            tableIncludeRegex = regex
            tableFilters = filters
            checkpointTargetIntervalSeconds = 60
            concurrency = 1
            setIncrementalValue(UserDefinedCursor)
        }

    private fun make(pojo: MySqlSourceConfigurationSpecification): MySqlSourceConfiguration =
        MySqlSourceConfigurationFactory().makeWithoutExceptionHandling(pojo)

    @Test
    fun testDatabaseOnlyIsUnchanged() {
        val config = make(pojo("shop", null))
        Assertions.assertEquals(setOf("shop"), config.namespaces)
        Assertions.assertEquals("shop", config.defaultDatabase)
        Assertions.assertTrue(config.tableIncludeRegex.isEmpty())
    }

    @Test
    fun testRegexOnly() {
        val config = make(pojo(null, listOf("db_.*\\..*", " ", "db_.*\\..*")))
        Assertions.assertEquals(emptySet<String>(), config.namespaces)
        Assertions.assertNull(config.defaultDatabase)
        Assertions.assertEquals(listOf("db_.*\\..*"), config.tableIncludeRegex.map { it.pattern() })
    }

    @Test
    fun testRegexWithDatabase() {
        val config = make(pojo("db_a", listOf("db_.*\\.orders")))
        Assertions.assertEquals(emptySet<String>(), config.namespaces)
        Assertions.assertEquals("db_a", config.defaultDatabase)
    }

    @Test
    fun testNeitherDatabaseNorRegex() {
        assertThrows<ConfigErrorException> { make(pojo(null, null)) }
        assertThrows<ConfigErrorException> { make(pojo("  ", listOf(""))) }
    }

    @Test
    fun testInvalidRegex() {
        val e = assertThrows<ConfigErrorException> { make(pojo(null, listOf("db_(\\..*"))) }
        Assertions.assertTrue(e.message!!.contains("db_(\\..*"))
    }

    @Test
    fun testRegexAndTableFiltersAreExclusive() {
        val filter =
            TableFilter().apply {
                databaseName = "db_a"
                patterns = listOf("orders")
            }
        assertThrows<ConfigErrorException> {
            make(pojo("db_a", listOf("db_a\\..*"), listOf(filter)))
        }
    }

    @Test
    fun testResolve() {
        val config = make(pojo(null, listOf("db_.*\\.orders", "inventory\\..*")))
        val allTables =
            listOf(
                "db_a" to "orders",
                "db_a" to "customers",
                "db_b" to "orders",
                "inventory" to "items",
                "inventory" to "stock_levels",
                "other" to "orders",
                "mysql" to "user",
            )
        val resolved = resolveTableIncludeRegex(config, allTables)
        Assertions.assertEquals(setOf("db_a", "db_b", "inventory"), resolved.namespaces)
        // Fully matched databases (db_b, inventory) need no filter.
        val filters = resolved.tableFilters.associate { it.schemaName to it.patterns }
        Assertions.assertEquals(mapOf("db_a" to listOf("orders")), filters)
    }

    @Test
    fun testResolveMatchesFullName() {
        // "orders" alone must not match "db_a.orders": the whole "database.table" must match.
        val config = make(pojo(null, listOf("orders")))
        assertThrows<ConfigErrorException> {
            resolveTableIncludeRegex(config, listOf("db_a" to "orders"))
        }
    }

    @Test
    fun testResolveEscapesLikeWildcards() {
        val config = make(pojo(null, listOf("db_a\\.order_items")))
        val resolved =
            resolveTableIncludeRegex(
                config,
                listOf("db_a" to "order_items", "db_a" to "orderXitems", "db_a" to "100%"),
            )
        Assertions.assertEquals(listOf("order\\_items"), resolved.tableFilters.single().patterns)
        Assertions.assertEquals("100\\%", escapeLikePattern("100%"))
        Assertions.assertEquals("a\\\\b", escapeLikePattern("a\\b"))
    }
}
