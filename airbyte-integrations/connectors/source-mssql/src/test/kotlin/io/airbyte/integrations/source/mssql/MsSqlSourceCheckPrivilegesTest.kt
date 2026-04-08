/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql

import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.check.JdbcCheckQueries
import io.airbyte.cdk.discover.JdbcMetadataQuerier
import io.airbyte.cdk.jdbc.DefaultJdbcConstants
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.github.oshai.kotlinlogging.KotlinLogging
import java.sql.Connection
import org.junit.jupiter.api.*
import org.junit.jupiter.api.Assertions.*
import org.testcontainers.containers.MSSQLServerContainer

private val log = KotlinLogging.logger {}

/**
 * Tests for the checkPrivileges behavior in [MsSqlSourceMetadataQuerier.fields].
 *
 * Verifies that columns with DENY SELECT are filtered out during discovery when checkPrivileges is
 * enabled, and that all columns are returned when checkPrivileges is disabled.
 */
@TestInstance(TestInstance.Lifecycle.PER_CLASS)
class MsSqlSourceCheckPrivilegesTest {

    private lateinit var dbContainer: MSSQLServerContainer<*>

    companion object {
        private const val RESTRICTED_USER = "restricted_test_user"
        private const val RESTRICTED_PASSWORD = "RestrictedPass123!"
        private const val TEST_TABLE = "privilege_test_table"
    }

    @BeforeAll
    @Timeout(value = 300)
    fun setUp() {
        dbContainer =
            MsSqlServerContainerFactory.shared(
                "mcr.microsoft.com/mssql/server:2022-latest",
                MsSqlServerContainerFactory.WithNetwork,
                MsSqlServerContainerFactory.WithTestDatabase
            )

        // Set up test table and restricted user using the SA account
        val saSpec = MsSqlServerContainerFactory.config(dbContainer)
        saSpec.setIncrementalValue(UserDefinedCursor())
        val saConfig = MsSqlServerSourceConfigurationFactory().make(saSpec)

        JdbcConnectionFactory(saConfig).get().use { conn: Connection ->
            conn.isReadOnly = false

            // Create the test table
            conn.createStatement().use { stmt ->
                stmt.execute("DROP TABLE IF EXISTS dbo.$TEST_TABLE")
                stmt.execute(
                    """
                    CREATE TABLE dbo.$TEST_TABLE (
                        id INT NOT NULL PRIMARY KEY,
                        public_col NVARCHAR(100),
                        secret_col NVARCHAR(100),
                        another_secret_col INT
                    )
                    """
                )
                stmt.execute(
                    """
                    INSERT INTO dbo.$TEST_TABLE VALUES 
                        (1, 'public1', 'secret1', 100),
                        (2, 'public2', 'secret2', 200)
                    """
                )
            }

            // Create a restricted login and user with DENY SELECT on specific columns
            conn.createStatement().use { stmt ->
                // Drop existing user/login if present
                stmt.execute(
                    """
                    IF EXISTS (SELECT 1 FROM sys.database_principals WHERE name = '$RESTRICTED_USER')
                        DROP USER [$RESTRICTED_USER]
                    """
                )
            }
            // Use a separate statement for the login since it needs master context
            conn.createStatement().use { stmt ->
                stmt.execute(
                    """
                    IF NOT EXISTS (SELECT 1 FROM sys.server_principals WHERE name = '$RESTRICTED_USER')
                        CREATE LOGIN [$RESTRICTED_USER] WITH PASSWORD = '$RESTRICTED_PASSWORD'
                    """
                )
            }
            conn.createStatement().use { stmt ->
                stmt.execute("CREATE USER [$RESTRICTED_USER] FOR LOGIN [$RESTRICTED_USER]")
                // Grant SELECT on the table overall
                stmt.execute("GRANT SELECT ON dbo.$TEST_TABLE TO [$RESTRICTED_USER]")
                // DENY SELECT on specific columns
                stmt.execute(
                    "DENY SELECT ON dbo.$TEST_TABLE (secret_col) TO [$RESTRICTED_USER]"
                )
                stmt.execute(
                    "DENY SELECT ON dbo.$TEST_TABLE (another_secret_col) TO [$RESTRICTED_USER]"
                )
            }
        }
    }

    /**
     * Creates a [MsSqlServerSourceConfiguration] for the restricted user with the specified
     * checkPrivileges setting.
     */
    private fun createRestrictedConfig(
        checkPrivileges: Boolean
    ): MsSqlServerSourceConfiguration {
        val spec =
            MsSqlServerSourceConfigurationSpecification().apply {
                host = dbContainer.host
                port =
                    dbContainer.getMappedPort(MSSQLServerContainer.MS_SQL_SERVER_PORT)
                username = RESTRICTED_USER
                password = RESTRICTED_PASSWORD
                jdbcUrlParams = ""
                database = "test"
                schemas = listOf("dbo")
                checkpointTargetIntervalSeconds = 60
                concurrency = 1
                this.checkPrivileges = checkPrivileges
                setIncrementalValue(UserDefinedCursor())
            }
        return MsSqlServerSourceConfigurationFactory().make(spec)
    }

    /** Creates a [MsSqlSourceMetadataQuerier] for the given config. */
    private fun createQuerier(config: MsSqlServerSourceConfiguration): MsSqlSourceMetadataQuerier {
        val jdbcConnectionFactory = JdbcConnectionFactory(config)
        val sourceOperations = MsSqlSourceOperations()
        val base =
            JdbcMetadataQuerier(
                DefaultJdbcConstants(),
                config,
                sourceOperations,
                sourceOperations,
                JdbcCheckQueries(),
                jdbcConnectionFactory
            )
        return MsSqlSourceMetadataQuerier(base)
    }

    @Test
    @DisplayName(
        "With checkPrivileges=true, columns with DENY SELECT should be filtered out"
    )
    fun testFieldsFiltersInaccessibleColumnsWhenCheckPrivilegesEnabled() {
        val config = createRestrictedConfig(checkPrivileges = true)
        val querier = createQuerier(config)

        val streamId =
            StreamIdentifier.from(
                StreamDescriptor().withName(TEST_TABLE).withNamespace("dbo")
            )

        val fields = querier.fields(streamId)
        val fieldNames = fields.map { it.id }

        log.info { "Fields with checkPrivileges=true: $fieldNames" }

        // Should only contain accessible columns
        assertTrue(fieldNames.contains("id"), "Should contain accessible column 'id'")
        assertTrue(
            fieldNames.contains("public_col"),
            "Should contain accessible column 'public_col'"
        )
        // Should NOT contain denied columns
        assertFalse(
            fieldNames.contains("secret_col"),
            "Should NOT contain denied column 'secret_col'"
        )
        assertFalse(
            fieldNames.contains("another_secret_col"),
            "Should NOT contain denied column 'another_secret_col'"
        )

        assertEquals(
            2,
            fields.size,
            "Should only have 2 accessible fields (id, public_col)"
        )
    }

    @Test
    @DisplayName(
        "With checkPrivileges=false, all columns should be returned including denied ones"
    )
    fun testFieldsReturnsAllColumnsWhenCheckPrivilegesDisabled() {
        val config = createRestrictedConfig(checkPrivileges = false)
        val querier = createQuerier(config)

        val streamId =
            StreamIdentifier.from(
                StreamDescriptor().withName(TEST_TABLE).withNamespace("dbo")
            )

        val fields = querier.fields(streamId)
        val fieldNames = fields.map { it.id }

        log.info { "Fields with checkPrivileges=false: $fieldNames" }

        // Should contain ALL columns including denied ones
        assertTrue(fieldNames.contains("id"), "Should contain column 'id'")
        assertTrue(fieldNames.contains("public_col"), "Should contain column 'public_col'")
        assertTrue(
            fieldNames.contains("secret_col"),
            "Should contain column 'secret_col' (not filtered when checkPrivileges=false)"
        )
        assertTrue(
            fieldNames.contains("another_secret_col"),
            "Should contain column 'another_secret_col' (not filtered when checkPrivileges=false)"
        )

        assertEquals(4, fields.size, "Should have all 4 columns")
    }

    @AfterAll
    fun tearDown() {
        try {
            val saSpec = MsSqlServerContainerFactory.config(dbContainer)
            saSpec.setIncrementalValue(UserDefinedCursor())
            val saConfig = MsSqlServerSourceConfigurationFactory().make(saSpec)

            JdbcConnectionFactory(saConfig).get().use { conn: Connection ->
                conn.isReadOnly = false
                conn.createStatement().use { stmt ->
                    try {
                        stmt.execute("DROP TABLE IF EXISTS dbo.$TEST_TABLE")
                    } catch (e: Exception) {
                        log.debug { "Error dropping test table: ${e.message}" }
                    }
                    try {
                        stmt.execute("DROP USER IF EXISTS [$RESTRICTED_USER]")
                    } catch (e: Exception) {
                        log.debug { "Error dropping test user: ${e.message}" }
                    }
                }
            }
        } catch (e: Exception) {
            log.error { "Error during teardown: ${e.message}" }
        }
    }
}
