/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql

import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.airbyte.protocol.models.v0.SyncMode
import io.github.oshai.kotlinlogging.KotlinLogging
import java.sql.Connection
import org.junit.jupiter.api.AfterAll
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.TestInstance
import org.junit.jupiter.api.Timeout
import org.testcontainers.containers.MSSQLServerContainer

@TestInstance(TestInstance.Lifecycle.PER_CLASS)
class MsSqlServerCdcLsnValidationIntegrationTest {

    private val testOps = MsSqlServerCdcLsnValidationTestOperations

    /**
     * Validates getAccessibleCaptureInstances(): as the admin (db_owner) user, every CDC-enabled
     * capture instance should be returned.
     */
    @Test
    fun assertAdminHasAccessToAllCaptureInstances() {
        val config = testOps.adminConfig(dbContainer)
        // The catalog is irrelevant here, getAccessibleCaptureInstances never reads it,
        // we are only testing the user access.
        val debeziumOps = testOps.ops(config, testOps.catalogOfAllConfigured())

        val accessible =
            JdbcConnectionFactory(config).get().use { connection ->
                debeziumOps.getAccessibleCaptureInstances(connection)
            }

        assertTrue(
            accessible.containsAll(
                listOf(
                    CaptureInstance("dbo", "users", "dbo_users"),
                    CaptureInstance("dbo", "orders", "dbo_orders"),
                    CaptureInstance("dbo", "restricted", "dbo_restricted")
                )
            )
        )
    }

    /**
     * Validates getAccessibleCaptureInstances() with limitedConfig: the limited user has
     * db_datareader but is not a member of the cdc_restricted gating role, so dbo_restricted is
     * filtered out while the two ungated instances remain.
     */
    @Test
    fun assertLimitedUserHasLimitedAccessToCaptureInstances() {
        val config = testOps.limitedConfig(dbContainer)
        // The catalog is irrelevant here, getAccessibleCaptureInstances never reads it,
        // we are only testing the user access.
        val debeziumOps = testOps.ops(config, testOps.catalogOfAllConfigured())

        val accessible =
            JdbcConnectionFactory(config).get().use { connection ->
                debeziumOps.getAccessibleCaptureInstances(connection)
            }

        assertEquals(
            // Only the two ungated instances. dbo_restricted is gated by a role limited isn't in.
            setOf(
                CaptureInstance("dbo", "users", "dbo_users"),
                CaptureInstance("dbo", "orders", "dbo_orders"),
            ),
            accessible.toSet(),
        )
    }

    companion object {

        lateinit var dbContainer: MSSQLServerContainer<*>

        @JvmStatic
        @BeforeAll
        @Timeout(value = 300)
        fun startAndProvisionTestContainer() {
            // exclusive (not shared): this test mutates security state as it contains logins, roles
            // and grants.
            dbContainer =
                MsSqlServerContainerFactory.exclusive(
                    "mcr.microsoft.com/mssql/server:2022-latest",
                    MsSqlServerContainerFactory.WithNetwork,
                    MsSqlServerContainerFactory.WithTestDatabase,
                )
            val ops = MsSqlServerCdcLsnValidationTestOperations
            val adminConfig = ops.adminConfig(dbContainer)
            ops.createStreams(adminConfig) // CDC + tables + gating roles + scan
            ops.createLimitedUser(
                adminConfig
            ) // creates the limited user: login + db_datareader, no gating role
        }

        @JvmStatic
        @AfterAll
        fun stopTestContainer() {
            if (::dbContainer.isInitialized) dbContainer.stop()
        }
    }
}

object MsSqlServerCdcLsnValidationTestOperations {

    private val log = KotlinLogging.logger {}

    const val LIMITED_USER = "limited"
    const val LIMITED_PASSWORD = "Passw0rd!"

    val configFactory = MsSqlServerSourceConfigurationFactory()

    val captureInstances =
        listOf(
            CaptureInstanceFixture("dbo", "users", "dbo_users", gatingRole = null),
            CaptureInstanceFixture("dbo", "orders", "dbo_orders", gatingRole = null),
            // Gated by cdc_restricted (users & orders have no gating role). The limited user is
            // never added to this role,
            // so getAccessibleCaptureInstances should hide this instance from it.
            CaptureInstanceFixture(
                "dbo",
                "restricted",
                "dbo_restricted",
                gatingRole = "cdc_restricted"
            ),
        )

    fun globalConfigSpec(
        container: MSSQLServerContainer<*>
    ): MsSqlServerSourceConfigurationSpecification =
        MsSqlServerContainerFactory.config(container).also { it.setIncrementalValue(Cdc()) }

    fun limitedGlobalConfigSpec(
        container: MSSQLServerContainer<*>
    ): MsSqlServerSourceConfigurationSpecification =
        globalConfigSpec(container).also {
            it.username = LIMITED_USER
            it.password = LIMITED_PASSWORD
        }

    fun limitedConfig(container: MSSQLServerContainer<*>): MsSqlServerSourceConfiguration =
        configFactory.make(limitedGlobalConfigSpec(container))

    fun adminConfig(container: MSSQLServerContainer<*>): MsSqlServerSourceConfiguration =
        configFactory.make(globalConfigSpec(container))

    fun createStreams(config: MsSqlServerSourceConfiguration) {
        JdbcConnectionFactory(config).get().use { connection: Connection ->
            connection.isReadOnly = false

            // Enable CDC
            try {
                val enableDbCdcSql = "EXEC sys.sp_cdc_enable_db"
                log.info { "Enabling CDC on database: $enableDbCdcSql" }
                connection.createStatement().use { stmt -> stmt.execute(enableDbCdcSql) }
                log.info { "Successfully enabled CDC on database" }
            } catch (e: Exception) {
                log.warn {
                    "Failed to enable CDC on database (may already be enabled): ${e.message}"
                }
            }

            for (ci in captureInstances) {
                connection.createStatement().use { stmt ->
                    stmt.execute("CREATE TABLE ${ci.schema}.${ci.table} (id INT PRIMARY KEY)")
                    val roleArg = ci.gatingRole?.let { "'$it'" } ?: "NULL"
                    // roles are listed in the capture instance
                    stmt.execute(
                        "EXEC sys.sp_cdc_enable_table " +
                            "@source_schema='${ci.schema}', @source_name='${ci.table}', " +
                            "@role_name=$roleArg, @capture_instance='${ci.captureInstance}'"
                    )
                }
            }
        }
    }

    /**
     * We are creating a user with limited access:
     * 1. Create the login (with password) and the database user.
     * 2. Add the user to the db_datareader role.
     * 3. createStreams() creates one table gated by the cdc_restricted role, which this limited
     * ```
     *    user is not a member of.
     * ```
     * 4. Because we never grant that role to the user, it has no access to that table.
     */
    fun createLimitedUser(config: MsSqlServerSourceConfiguration) {
        JdbcConnectionFactory(config).get().use { connection: Connection ->
            connection.isReadOnly = false
            connection.createStatement().use { stmt ->
                stmt.execute("CREATE LOGIN $LIMITED_USER WITH PASSWORD='$LIMITED_PASSWORD'")
                stmt.execute("CREATE USER $LIMITED_USER FOR LOGIN $LIMITED_USER")
                stmt.execute("ALTER ROLE db_datareader ADD MEMBER $LIMITED_USER")
            }
        }
    }

    fun catalogOfAllConfigured(): ConfiguredAirbyteCatalog =
        ConfiguredAirbyteCatalog()
            .withStreams(
                captureInstances.map { ci ->
                    ConfiguredAirbyteStream()
                        .withStream(AirbyteStream().withNamespace(ci.schema).withName(ci.table))
                        .withSyncMode(SyncMode.INCREMENTAL)
                }
            )

    fun ops(
        config: MsSqlServerSourceConfiguration,
        catalog: ConfiguredAirbyteCatalog,
    ): MsSqlServerDebeziumOperations =
        MsSqlServerDebeziumOperations(JdbcConnectionFactory(config), config, catalog)
}

/**
 * One CDC-enabled table in the test. schema / table -> source table (dbo.users). captureInstance ->
 * CDC capture-instance name (dbo_users). gatingRole -> the CDC role that gates access to this
 * capture instance.
 */
data class CaptureInstanceFixture(
    val schema: String,
    val table: String,
    val captureInstance: String,
    val gatingRole: String?,
)
