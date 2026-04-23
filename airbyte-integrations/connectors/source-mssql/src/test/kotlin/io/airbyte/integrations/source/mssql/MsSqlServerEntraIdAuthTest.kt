/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql

import io.airbyte.cdk.ConfigErrorException
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

/**
 * Pure-function tests for the Entra ID authentication wiring.
 *
 * Covers:
 * - [MsSqlServerAuthentication.toJdbcProperties] — the canonical auth-mode → mssql-jdbc properties
 * translation (used by the JDBC session path).
 * - [MsSqlServerAuthentication.toDebeziumDatabaseProperties] — the subset forwarded to Debezium
 * under the `database.*` prefix (auth identity: user, password).
 * - [MsSqlServerAuthentication.toDebeziumDriverProperties] — the subset forwarded to Debezium under
 * the `driver.*` pass-through (the `authentication` mode and any other mssql-jdbc connection
 * property), which is how Debezium 3.5+ wires Microsoft Entra authentication.
 * - [MsSqlServerSourceConfigurationFactory] resolving the auth mode, rejecting invalid combinations
 * (Entra ID + unencrypted; missing legacy credentials), and populating `jdbcProperties` correctly.
 */
class MsSqlServerEntraIdAuthTest {

    // --- toJdbcProperties / toDebeziumDatabaseProperties / toDebeziumDriverProperties ---

    @Test
    fun sqlPasswordAuthEmitsUserPasswordAndAuthenticationKey() {
        val auth = SqlPasswordAuthentication(username = "sa", password = "Password123!")
        val props = auth.toJdbcProperties()
        Assertions.assertEquals("sa", props["user"])
        Assertions.assertEquals("Password123!", props["password"])
        Assertions.assertEquals("SqlPassword", props["authentication"])
        Assertions.assertEquals(3, props.size)
    }

    @Test
    fun sqlPasswordAuthDebeziumSplitSendsIdentityToDatabaseAndModeToDriver() {
        val auth = SqlPasswordAuthentication(username = "sa", password = "Password123!")
        val dbProps = auth.toDebeziumDatabaseProperties()
        Assertions.assertEquals(mapOf("user" to "sa", "password" to "Password123!"), dbProps)

        val driverProps = auth.toDebeziumDriverProperties()
        Assertions.assertEquals(mapOf("authentication" to "SqlPassword"), driverProps)
    }

    @Test
    fun servicePrincipalAuthEmitsClientIdAsUserAndSecretAsPassword() {
        val auth =
            ActiveDirectoryServicePrincipalAuthentication(
                tenantId = "tenant-uuid",
                clientId = "client-uuid",
                clientSecret = "secret-value",
            )
        val props = auth.toJdbcProperties()
        Assertions.assertEquals("client-uuid", props["user"])
        Assertions.assertEquals("secret-value", props["password"])
        Assertions.assertEquals("ActiveDirectoryServicePrincipal", props["authentication"])
        // tenantId is informational only at the current driver version — not forwarded.
        Assertions.assertFalse(props.containsKey("tenant_id"))
        Assertions.assertFalse(props.containsKey("AADSecurePrincipalId"))
        Assertions.assertEquals(3, props.size)
    }

    @Test
    fun servicePrincipalAuthDebeziumSplitSendsIdentityToDatabaseAndModeToDriver() {
        // This is the Debezium 3.5 wiring for Microsoft Entra ID service principal:
        //   database.user=<clientId>
        //   database.password=<clientSecret>
        //   driver.authentication=ActiveDirectoryServicePrincipal
        // Debezium strips the `driver.` prefix and forwards the key to mssql-jdbc as the
        // `authentication` connection property.
        val auth =
            ActiveDirectoryServicePrincipalAuthentication(
                tenantId = "tenant-uuid",
                clientId = "client-uuid",
                clientSecret = "secret-value",
            )
        val dbProps = auth.toDebeziumDatabaseProperties()
        Assertions.assertEquals(
            mapOf("user" to "client-uuid", "password" to "secret-value"),
            dbProps,
        )
        Assertions.assertFalse(
            dbProps.containsKey("authentication"),
            "authentication mode must NOT be forwarded under Debezium's database.* prefix " +
                "(Debezium 3.5+ uses driver.authentication for this).",
        )

        val driverProps = auth.toDebeziumDriverProperties()
        Assertions.assertEquals(
            mapOf("authentication" to "ActiveDirectoryServicePrincipal"),
            driverProps,
        )
        Assertions.assertFalse(driverProps.containsKey("user"))
        Assertions.assertFalse(driverProps.containsKey("password"))
    }

    @Test
    fun servicePrincipalAuthWithNullTenantIdStillEmitsAuthKeys() {
        val auth =
            ActiveDirectoryServicePrincipalAuthentication(
                tenantId = null,
                clientId = "client-uuid",
                clientSecret = "secret-value",
            )
        val props = auth.toJdbcProperties()
        Assertions.assertEquals("client-uuid", props["user"])
        Assertions.assertEquals("secret-value", props["password"])
        Assertions.assertEquals("ActiveDirectoryServicePrincipal", props["authentication"])
    }

    // --- Factory resolution: spec → MsSqlServerSourceConfiguration ---

    @Test
    fun factoryResolvesLegacyFlatUsernamePasswordToSqlPasswordAuth() {
        val pojo = baseEncryptedPojo()
        pojo.username = "legacy-user"
        pojo.password = "legacy-pw"
        // authentication block deliberately not set

        val config = MsSqlServerSourceConfigurationFactory().make(pojo)
        Assertions.assertEquals(
            SqlPasswordAuthentication("legacy-user", "legacy-pw"),
            config.authentication,
        )
        Assertions.assertEquals("legacy-user", config.jdbcProperties["user"])
        Assertions.assertEquals("legacy-pw", config.jdbcProperties["password"])
        Assertions.assertEquals("SqlPassword", config.jdbcProperties["authentication"])
    }

    @Test
    fun factoryRejectsMissingLegacyCredentialsAndNoAuthBlock() {
        val pojo = baseEncryptedPojo()
        // neither legacy fields nor authentication block set
        val ex =
            Assertions.assertThrows(ConfigErrorException::class.java) {
                MsSqlServerSourceConfigurationFactory().makeWithoutExceptionHandling(pojo)
            }
        Assertions.assertTrue(
            ex.message?.contains("Authentication is not configured") == true,
            "Unexpected error message: ${ex.message}",
        )
    }

    @Test
    fun factoryResolvesAuthBlockServicePrincipalAndPopulatesJdbcProperties() {
        val pojo = baseEncryptedPojo()
        pojo.tenantId = "tenant-uuid"
        pojo.clientId = "client-uuid"
        pojo.clientSecret = "secret-value"

        val config = MsSqlServerSourceConfigurationFactory().make(pojo)
        Assertions.assertEquals(
            ActiveDirectoryServicePrincipalAuthentication(
                tenantId = "tenant-uuid",
                clientId = "client-uuid",
                clientSecret = "secret-value",
            ),
            config.authentication,
        )
        Assertions.assertEquals("client-uuid", config.jdbcProperties["user"])
        Assertions.assertEquals("secret-value", config.jdbcProperties["password"])
        Assertions.assertEquals(
            "ActiveDirectoryServicePrincipal",
            config.jdbcProperties["authentication"],
        )
        Assertions.assertEquals("true", config.jdbcProperties["encrypt"])
    }

    @Test
    fun factoryRejectsEntraIdAuthWithUnencryptedSslMode() {
        val pojo = baseUnencryptedPojo()
        pojo.clientId = "client-uuid"
        pojo.clientSecret = "secret-value"

        val ex =
            Assertions.assertThrows(ConfigErrorException::class.java) {
                MsSqlServerSourceConfigurationFactory().makeWithoutExceptionHandling(pojo)
            }
        Assertions.assertTrue(
            ex.message?.contains("Microsoft Entra ID authentication requires an encrypted") == true,
            "Unexpected error message: ${ex.message}",
        )
    }

    @Test
    fun factoryAllowsLegacySqlPasswordWithUnencryptedSslMode() {
        // Unencrypted is still allowed for the legacy SQL auth path (subject to cloud guard).
        val pojo = baseUnencryptedPojo()
        pojo.username = "sa"
        pojo.password = "Password123!"

        val config = MsSqlServerSourceConfigurationFactory().make(pojo)
        Assertions.assertTrue(config.authentication is SqlPasswordAuthentication)
        Assertions.assertEquals("false", config.jdbcProperties["encrypt"])
    }

    @Test
    fun jdbcUrlParamsCannotSpoofResolvedEntraIdAuth() {
        // Defense-in-depth: a jdbc_url_params string attempting to override the resolved Entra ID
        // service-principal auth with a SqlPassword identity must NOT take effect on the JDBC
        // session path. The trusted resolved auth wins.
        val pojo = baseEncryptedPojo()
        pojo.clientId = "client-uuid"
        pojo.clientSecret = "secret-value"
        pojo.jdbcUrlParams =
            "user=attacker&password=pwned&authentication=SqlPassword&applicationIntent=ReadOnly"

        val config = MsSqlServerSourceConfigurationFactory().make(pojo)
        Assertions.assertEquals("client-uuid", config.jdbcProperties["user"])
        Assertions.assertEquals("secret-value", config.jdbcProperties["password"])
        Assertions.assertEquals(
            "ActiveDirectoryServicePrincipal",
            config.jdbcProperties["authentication"],
        )
        // Unrelated operator-supplied params still pass through.
        Assertions.assertEquals("ReadOnly", config.jdbcProperties["applicationIntent"])
    }

    @Test
    fun jdbcUrlParamsCannotSpoofResolvedSqlPasswordAuth() {
        // Same guarantee for the legacy SQL password path: jdbc_url_params cannot swap in a
        // different user/password/auth mode.
        val pojo = baseEncryptedPojo()
        pojo.username = "legit"
        pojo.password = "legit-pw"
        pojo.jdbcUrlParams = "user=attacker&password=pwned&authentication=ActiveDirectoryPassword"

        val config = MsSqlServerSourceConfigurationFactory().make(pojo)
        Assertions.assertEquals("legit", config.jdbcProperties["user"])
        Assertions.assertEquals("legit-pw", config.jdbcProperties["password"])
        Assertions.assertEquals("SqlPassword", config.jdbcProperties["authentication"])
    }

    // --- fixtures ---

    private fun baseEncryptedPojo(): MsSqlServerSourceConfigurationSpecification =
        MsSqlServerSourceConfigurationSpecification().also {
            it.host = "server.database.windows.net"
            it.port = 1433
            it.database = "master"
            it.encryptionJson =
                MsSqlServerEncryptionRequiredTrustServerCertificateConfigurationSpecification
            it.replicationMethodJson = UserDefinedCursor()
        }

    private fun baseUnencryptedPojo(): MsSqlServerSourceConfigurationSpecification =
        MsSqlServerSourceConfigurationSpecification().also {
            it.host = "localhost"
            it.port = 1433
            it.database = "master"
            it.encryptionJson = MsSqlServerEncryptionDisabledConfigurationSpecification
            it.replicationMethodJson = UserDefinedCursor()
        }
}
