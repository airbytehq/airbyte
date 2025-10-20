/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.oracle

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.github.oshai.kotlinlogging.KotlinLogging
import java.sql.Connection
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.Timeout
import org.junit.jupiter.api.function.Executable
import org.testcontainers.containers.OracleContainer

class OracleSourceTableFilterIntegrationTest {
    private val log = KotlinLogging.logger {}

    @Test
    @Timeout(300)
    fun testNoFilter() {
        testRunner.testNoFilter()
    }

    @Test
    @Timeout(300)
    fun testTableFilters() {
        testRunner.testTableFilters()
    }

    @Test
    @Timeout(300)
    fun testFilterSchemaNotInConfiguredSchemas() {
        testRunner.testFilterSchemaNotInConfiguredSchemas()
    }

    companion object {
        lateinit var dbContainer: OracleContainer
        lateinit var testRunner: SetupAndTestFilters

        @JvmStatic
        @BeforeAll
        @Timeout(value = 300)
        fun startAndProvisionTestContainer() {
            dbContainer = OracleContainerFactory.exclusive("gvenzl/oracle-free:23.6-slim-faststart")
            testRunner = SetupAndTestFilters { dbContainer }
            testRunner.execute()
        }
    }
}

class SetupAndTestFilters(databaseContainerSupplier: () -> OracleContainer) : Executable {
    private val log = KotlinLogging.logger {}
    private val dbContainer: OracleContainer by lazy { databaseContainerSupplier() }

    // Test data
    val schemaNames = listOf(dbContainer.username.uppercase())
    val tableNames = listOf("ORDERS", "CUSTOMERS", "PRODUCTS", "INVOICES")

    lateinit var jdbcConnectionFactory: JdbcConnectionFactory
    lateinit var oracleQuerierFactory: OracleSourceMetadataQuerier.Factory

    override fun execute() {
        log.info { "Generating JDBC config." }
        val jdbcConfigSpec = OracleContainerFactory.configSpecification(dbContainer)
        val jdbcConfig = OracleSourceConfigurationFactory().make(jdbcConfigSpec)
        jdbcConnectionFactory = JdbcConnectionFactory(jdbcConfig)

        log.info { "Creating OracleSourceMetadataQuerier factory." }
        oracleQuerierFactory =
            OracleSourceMetadataQuerier.Factory(
                selectQueryGenerator = OracleSourceOperations(),
                fieldTypeMapper = OracleSourceOperations(),
                checkQueries = io.airbyte.cdk.check.JdbcCheckQueries(),
                constants = io.airbyte.cdk.jdbc.DefaultJdbcConstants(),
            )

        log.info { "Executing DDL statements." }
        jdbcConnectionFactory.get().use { connection: Connection ->
            connection.createStatement().use { stmt ->
                for (schema in schemaNames) {

                    // Create tables in each schema
                    for (table in tableNames) {
                        try {
                            log.info { "Creating table: $schema.$table" }
                            stmt.execute(
                                "CREATE TABLE $schema.$table (ID NUMBER PRIMARY KEY, NAME VARCHAR2(255))"
                            )
                        } catch (e: Exception) {
                            log.warn { "Table $schema.$table might already exist: ${e.message}" }
                        }
                    }
                }
            }
        }
        log.info { "Done setting up test schemas and tables." }
    }

    fun testNoFilter() {
        log.info { "Running testNoFilter" }
        // When no filters are provided, all tables should be returned
        val configPojo =
            OracleSourceConfigurationSpecification().apply {
                port = dbContainer.oraclePort
                host = dbContainer.host
                schemas = schemaNames
                username = dbContainer.username
                password = dbContainer.password
                setConnectionDataValue(ServiceName().apply { serviceName = "FREEPDB1" })
                filters = null
            }

        val config: OracleSourceConfiguration =
            OracleSourceConfigurationFactory().makeWithoutExceptionHandling(configPojo)

        // Verify all tables are returned for each schema
        schemaNames.forEach { schema ->
            val streamNames =
                oracleQuerierFactory
                    .session(config)
                    .streamNames(schema.uppercase())
                    .map { it.name }
                    .toSet()

            log.info { "Schema $schema has tables: $streamNames" }
            assertEquals(tableNames.toSet(), streamNames, "Schema $schema should have all tables")
        }
        log.info { "testNoFilter passed" }
    }

    fun testTableFilters() {
        log.info { "Running testTableFilters" }
        val tableFilter =
            TableFilter().apply {
                schemaName = schemaNames[0]
                patterns = listOf("CUSTOMERS", "ORDERS")
            }

        val configPojo =
            OracleSourceConfigurationSpecification().apply {
                port = dbContainer.oraclePort
                host = dbContainer.host
                schemas = schemaNames
                username = dbContainer.username
                password = dbContainer.password
                setConnectionDataValue(ServiceName().apply { serviceName = "FREEPDB1" })
                filters = listOf(tableFilter)
            }

        val config: OracleSourceConfiguration =
            OracleSourceConfigurationFactory().makeWithoutExceptionHandling(configPojo)

        schemaNames.forEach { schema ->
            val streamNames =
                oracleQuerierFactory
                    .session(config)
                    .streamNames(schema.uppercase())
                    .map { it.name }
                    .toSet()

            log.info { "Schema $schema has tables: $streamNames" }
            assertEquals(
                listOf("CUSTOMERS", "ORDERS").toSet(),
                streamNames,
                "Schema $schema should have specified tables"
            )
        }

        log.info { "testTableFilters passed" }
    }

    fun testFilterSchemaNotInConfiguredSchemas() {
        log.info { "Running testFilterSchemaNotInConfiguredSchemas" }
        // Filter references a schema that is not in the configured schemas list
        val tableFilter =
            TableFilter().apply {
                schemaName = "NONEXISTENT_SCHEMA"
                patterns = listOf("ORDERS", "CUSTOMERS")
            }

        val configPojo =
            OracleSourceConfigurationSpecification().apply {
                port = dbContainer.oraclePort
                host = dbContainer.host
                schemas = schemaNames
                username = dbContainer.username
                password = dbContainer.password
                setConnectionDataValue(ServiceName().apply { serviceName = "FREEPDB1" })
                filters = listOf(tableFilter)
            }

        assertThrows(ConfigErrorException::class.java) {
            OracleSourceConfigurationFactory().makeWithoutExceptionHandling(configPojo)
        }
        log.info { "testFilterSchemaNotInConfiguredSchemas passed - correctly threw exception" }
    }
}
