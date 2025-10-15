/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.sap_hana

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.check.JdbcCheckQueries
import io.airbyte.cdk.jdbc.DefaultJdbcConstants
import java.sql.SQLException
import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

class SapHanaTableFilterTest {
    var db =
        SapHanaTestDatabase(
            "1bd5e6cf-2112-4b8d-b9d2-3ea58d8a6a8e.hna0.prod-us10.hanacloud.ondemand.com",
            443,
            "DBADMIN",
            "Dbsource12345!"
        )

    val hanaQuerierFactory =
        SapHanaSourceMetadataQuerier.Factory(
            selectQueryGenerator = SapHanaSourceOperations(),
            fieldTypeMapper = SapHanaSourceOperations(),
            checkQueries = JdbcCheckQueries(),
            constants = DefaultJdbcConstants(),
        )

    // Create schema and table names for testing
    val schemaNames = listOf("SCHEMA_1", "SCHEMA_2")
    val tableNames = listOf("ORDERS", "CUSTOMERS", "PRODUCTS", "INVOICES")

    @BeforeEach
    fun setUp() {
        try {
            db.connect()
            for (i in 0..schemaNames.size - 1) {
                db.execute("CREATE SCHEMA ${schemaNames[i]}")
                for (j in 0..tableNames.size - 1) {
                    db.execute(
                        "CREATE TABLE ${schemaNames[i]}.${tableNames[j]} (ID INT PRIMARY KEY, NAME VARCHAR(255))"
                    )
                }
            }
        } catch (e: SQLException) {
            e.printStackTrace()
        }
    }

    @AfterEach
    fun tearDown() {
        try {
            for (i in 0..schemaNames.size - 1) db.execute("DROP SCHEMA ${schemaNames[i]} CASCADE")
            db.disconnect()
        } catch (e: SQLException) {
            e.printStackTrace()
        }
    }

    @Test
    fun testNoFilter() {
        // When no filters are provided, all tables should be returned
        val configPojo =
            SapHanaSourceConfigurationSpecification().apply {
                port = db.port
                host = db.host
                schemas = schemaNames
                username = db.username
                password = db.password
                filters = null
            }

        val config: SapHanaSourceConfiguration =
            SapHanaSourceConfigurationFactory().makeWithoutExceptionHandling(configPojo)

        // Verify all tables are returned for each schema
        schemaNames.forEach { schema ->
            val streamNames =
                hanaQuerierFactory.session(config).streamNames(schema).map { it.name }.toSet()

            assertEquals(tableNames.toSet(), streamNames)
        }
    }

    @Test
    fun testTableFilters() {
        val tableFilter1 =
            TableFilter().apply {
                schemaName = "SCHEMA_1"
                filters = listOf("CUSTOMERS")
            }

        val tableFilter2 =
            TableFilter().apply {
                schemaName = "SCHEMA_2"
                filters = listOf("ORDERS")
            }

        val configPojo =
            SapHanaSourceConfigurationSpecification().apply {
                port = db.port
                host = db.host
                schemas = schemaNames
                username = db.username
                password = db.password
                filters = listOf(tableFilter1, tableFilter2)
            }

        val config: SapHanaSourceConfiguration =
            SapHanaSourceConfigurationFactory().makeWithoutExceptionHandling(configPojo)

        val querier = hanaQuerierFactory.session(config) as SapHanaSourceMetadataQuerier

        // Check that memoizedTableNames only contains filtered tables
        val schema1Tables =
            querier.memoizedTableNames.filter { it.schema == "SCHEMA_1" }.map { it.name }.toSet()

        assertEquals(setOf("CUSTOMERS"), schema1Tables)

        val schema2Tables =
            querier.memoizedTableNames.filter { it.schema == "SCHEMA_2" }.map { it.name }.toSet()

        assertEquals(setOf("ORDERS"), schema2Tables)
    }

    @Test
    fun testFilterSchemaNotInConfiguredSchemas() {
        // Filter references a schema that is not in the configured schemas list
        val tableFilter =
            TableFilter().apply {
                schemaName = "NONEXISTENT_SCHEMA"
                filters = listOf("ORDERS", "CUSTOMERS")
            }

        val configPojo =
            SapHanaSourceConfigurationSpecification().apply {
                port = db.port
                host = db.host
                schemas = schemaNames
                username = db.username
                password = db.password
                filters = listOf(tableFilter)
            }

        assertThrows(ConfigErrorException::class.java) {
            SapHanaSourceConfigurationFactory().makeWithoutExceptionHandling(configPojo)
        }
    }
}
