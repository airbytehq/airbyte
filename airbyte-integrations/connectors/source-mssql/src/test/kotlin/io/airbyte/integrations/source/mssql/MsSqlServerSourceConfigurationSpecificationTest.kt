/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mssql

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.command.ConfigurationSpecificationSupplier
import io.airbyte.cdk.ssh.SshPasswordAuthTunnelMethod
import io.airbyte.cdk.ssh.SshTunnelMethodConfiguration
import io.micronaut.context.annotation.Property
import io.micronaut.context.env.Environment
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

@MicronautTest(environments = [Environment.TEST], rebuildContext = true)
class MsSqlServerSourceConfigurationSpecificationTest {

    @Inject
    lateinit var supplier:
        ConfigurationSpecificationSupplier<MsSqlServerSourceConfigurationSpecification>

    @Test
    fun testSchemaViolation() {
        Assertions.assertThrows(ConfigErrorException::class.java, supplier::get)
    }

    @Test
    @Property(name = "airbyte.connector.config.json", value = CONFIG_JSON)
    fun testJson() {
        val pojo: MsSqlServerSourceConfigurationSpecification = supplier.get()
        Assertions.assertEquals("localhost", pojo.host)
        Assertions.assertEquals(1433, pojo.port)
        Assertions.assertEquals("sa", pojo.username)
        Assertions.assertEquals("Password123!", pojo.password)
        Assertions.assertEquals("master", pojo.database)
        Assertions.assertArrayEquals(arrayOf("dbo", "custom_schema"), pojo.schemas)

        val encryption: EncryptionSpecification = pojo.getEncryptionValue()!!
        Assertions.assertTrue(
            encryption
                is MsSqlServerEncryptionRequiredTrustServerCertificateConfigurationSpecification,
            encryption::class.toString()
        )

        val tunnelMethod: SshTunnelMethodConfiguration? = pojo.getTunnelMethodValue()
        Assertions.assertTrue(
            tunnelMethod is SshPasswordAuthTunnelMethod,
            tunnelMethod!!::class.toString(),
        )

        val replicationMethod: IncrementalConfigurationSpecification = pojo.getIncrementalValue()
        Assertions.assertTrue(replicationMethod is Cdc, replicationMethod::class.toString())

        Assertions.assertEquals(300, pojo.checkpointTargetIntervalSeconds)
        Assertions.assertEquals(2, pojo.concurrency)
        Assertions.assertEquals(true, pojo.checkPrivileges)
        Assertions.assertEquals(
            "integratedSecurity=false&trustServerCertificate=true",
            pojo.jdbcUrlParams
        )
    }

    /**
     * Verifies that the encryption mode is correctly set to "required" as the default value in the
     * MsSqlServerSourceConfigurationSpecification class.
     */
    @Test
    @Property(name = "airbyte.connector.config.json", value = CONFIG_JSON_ENCRYPTION_CHECK)
    fun testDefaultEncryption() {
        val pojo: MsSqlServerSourceConfigurationSpecification = supplier.get()
        val encryption: EncryptionSpecification = pojo.getEncryptionValue()!!
        Assertions.assertTrue(
            encryption is MsSqlServerEncryptionDisabledConfigurationSpecification,
            encryption::class.toString()
        )
    }

    /** Verifies that the default replication method is UserDefinedCursor when not specified. */
    @Test
    @Property(name = "airbyte.connector.config.json", value = CONFIG_JSON_DEFAULT_REPLICATION)
    fun testDefaultReplicationMethod() {
        val pojo: MsSqlServerSourceConfigurationSpecification = supplier.get()
        val replicationMethod: IncrementalConfigurationSpecification = pojo.getIncrementalValue()
        Assertions.assertTrue(
            replicationMethod is UserDefinedCursor,
            replicationMethod::class.toString()
        )
    }

    /** Verifies that CDC replication method is correctly parsed. */
    @Test
    @Property(name = "airbyte.connector.config.json", value = CONFIG_JSON_CDC)
    fun testCdcReplicationMethod() {
        val pojo: MsSqlServerSourceConfigurationSpecification = supplier.get()
        val replicationMethod: IncrementalConfigurationSpecification = pojo.getIncrementalValue()
        Assertions.assertTrue(replicationMethod is Cdc, replicationMethod::class.toString())
    }

    /**
     * Verifies that empty schemas array defaults to empty set, which will trigger discovery of all
     * schemas (legacy connector behavior).
     */
    @Test
    @Property(name = "airbyte.connector.config.json", value = CONFIG_JSON_EMPTY_SCHEMAS)
    fun testEmptySchemasArrayDefaultsToEmptySet() {
        val pojo: MsSqlServerSourceConfigurationSpecification = supplier.get()
        val factory = MsSqlServerSourceConfigurationFactory()
        val config = factory.make(pojo)

        // Empty schemas array should default to empty set (discover all schemas)
        Assertions.assertEquals(emptySet<String>(), config.namespaces)
    }

    /**
     * Verifies that null schemas defaults to empty set, which will trigger discovery of all schemas
     * (legacy connector behavior).
     */
    @Test
    @Property(name = "airbyte.connector.config.json", value = CONFIG_JSON_NULL_SCHEMAS)
    fun testNullSchemasDefaultsToEmptySet() {
        val pojo: MsSqlServerSourceConfigurationSpecification = supplier.get()
        val factory = MsSqlServerSourceConfigurationFactory()
        val config = factory.make(pojo)

        // Null schemas should default to empty set (discover all schemas)
        Assertions.assertEquals(emptySet<String>(), config.namespaces)
    }

    /**
     * Verifies that a legacy config using the flat root `username`/`password` fields (no
     * `authentication` block) still parses and resolves to a [SqlPasswordAuthentication]. This is
     * the soft back-compat path.
     */
    @Test
    @Property(name = "airbyte.connector.config.json", value = CONFIG_JSON_LEGACY_SQL_AUTH)
    fun testLegacySqlAuthBackCompat() {
        val pojo: MsSqlServerSourceConfigurationSpecification = supplier.get()
        Assertions.assertNull(pojo.clientId)
        Assertions.assertEquals("sa", pojo.username)
        Assertions.assertEquals("Password123!", pojo.password)

        val config = MsSqlServerSourceConfigurationFactory().make(pojo)
        val auth = config.authentication
        Assertions.assertTrue(
            auth is SqlPasswordAuthentication,
            auth::class.toString(),
        )
        auth as SqlPasswordAuthentication
        Assertions.assertEquals("sa", auth.username)
        Assertions.assertEquals("Password123!", auth.password)
    }

    @Test
    @Property(name = "airbyte.connector.config.json", value = CONFIG_JSON_AUTH_SERVICE_PRINCIPAL)
    fun testAuthBlockServicePrincipal() {
        val pojo: MsSqlServerSourceConfigurationSpecification = supplier.get()
        Assertions.assertEquals("tenant-uuid", pojo.tenantId)
        Assertions.assertEquals("client-uuid", pojo.clientId)
        Assertions.assertEquals("client-secret-value", pojo.clientSecret)

        val config = MsSqlServerSourceConfigurationFactory().make(pojo)
        Assertions.assertEquals(
            ActiveDirectoryServicePrincipalAuthentication(
                tenantId = "tenant-uuid",
                clientId = "client-uuid",
                clientSecret = "client-secret-value",
            ),
            config.authentication,
        )
    }

    /** Entra ID auth with ssl_mode=unencrypted must be rejected by the factory. */
    @Test
    @Property(name = "airbyte.connector.config.json", value = CONFIG_JSON_AUTH_ENTRA_UNENCRYPTED)
    fun testEntraIdAuthRejectsUnencrypted() {
        val pojo: MsSqlServerSourceConfigurationSpecification = supplier.get()
        val ex =
            Assertions.assertThrows(ConfigErrorException::class.java) {
                MsSqlServerSourceConfigurationFactory().makeWithoutExceptionHandling(pojo)
            }
        Assertions.assertTrue(
            ex.message?.contains("Microsoft Entra ID authentication requires an encrypted") == true,
            "Unexpected error message: ${ex.message}",
        )
    }

    companion object {

        const val CONFIG_JSON: String =
            """
{
  "host": "localhost",
  "port": 1433,
  "username": "sa",
  "password": "Password123!",
  "database": "master",
  "schemas": ["dbo", "custom_schema"],
  "ssl_mode": {
    "mode": "encrypted_trust_server_certificate"
  },
  "tunnel_method": {
    "tunnel_method": "SSH_PASSWORD_AUTH",
    "tunnel_host": "localhost",
    "tunnel_port": 2222,
    "tunnel_user": "sshuser",
    "tunnel_user_password": "sshpass"
  },
  "replication_method": {
    "method": "CDC"
  },
  "checkpoint_target_interval_seconds": 300,
  "jdbc_url_params": "integratedSecurity=false&trustServerCertificate=true",
  "concurrency": 2,
  "check_privileges": true
}
"""

        const val CONFIG_JSON_ENCRYPTION_CHECK: String =
            """
{
  "host": "localhost",
  "port": 1433,
  "username": "sa",
  "password": "Password123!",
  "database": "master",
  "schemas": ["dbo"],
  "tunnel_method": {
    "tunnel_method": "SSH_PASSWORD_AUTH",
    "tunnel_host": "localhost",
    "tunnel_port": 2222,
    "tunnel_user": "sshuser",
    "tunnel_user_password": "sshpass"
  },
  "replication_method": {
    "method": "STANDARD"
  },
  "checkpoint_target_interval_seconds": 300,
  "jdbc_url_params": "integratedSecurity=false&trustServerCertificate=true",
  "concurrency": 1
}
"""

        const val CONFIG_JSON_DEFAULT_REPLICATION: String =
            """
{
  "host": "localhost",
  "port": 1433,
  "username": "sa",
  "password": "Password123!",
  "database": "master",
  "schemas": ["dbo"],
  "ssl_mode": {
    "mode": "encrypted_trust_server_certificate"
  },
  "replication_method": {
    "method": "STANDARD"
  }
}
"""

        const val CONFIG_JSON_CDC: String =
            """
{
  "host": "localhost",
  "port": 1433,
  "username": "sa",
  "password": "Password123!",
  "database": "master",
  "schemas": ["dbo"],
  "ssl_mode": {
    "mode": "encrypted_trust_server_certificate"
  },
  "replication_method": {
    "method": "CDC"
  }
}
"""

        const val CONFIG_JSON_EMPTY_SCHEMAS: String =
            """
{
  "host": "localhost",
  "port": 1433,
  "username": "sa",
  "password": "Password123!",
  "database": "master",
  "schemas": [],
  "ssl_mode": {
    "mode": "encrypted_trust_server_certificate"
  },
  "replication_method": {
    "method": "CDC"
  }
}
"""

        const val CONFIG_JSON_NULL_SCHEMAS: String =
            """
{
  "host": "localhost",
  "port": 1433,
  "username": "sa",
  "password": "Password123!",
  "database": "master",
  "ssl_mode": {
    "mode": "encrypted_trust_server_certificate"
  },
  "replication_method": {
    "method": "CDC"
  }
}
"""

        const val CONFIG_JSON_LEGACY_SQL_AUTH: String =
            """
{
  "host": "localhost",
  "port": 1433,
  "username": "sa",
  "password": "Password123!",
  "database": "master",
  "ssl_mode": {
    "mode": "encrypted_trust_server_certificate"
  },
  "replication_method": {
    "method": "STANDARD"
  }
}
"""

        const val CONFIG_JSON_AUTH_SERVICE_PRINCIPAL: String =
            """
{
  "host": "server.database.windows.net",
  "port": 1433,
  "database": "master",
  "ssl_mode": {
    "mode": "encrypted_trust_server_certificate"
  },
  "replication_method": {
    "method": "STANDARD"
  },
  "tenant_id": "tenant-uuid",
  "client_id": "client-uuid",
  "client_secret": "client-secret-value"
}
"""

        const val CONFIG_JSON_AUTH_ENTRA_UNENCRYPTED: String =
            """
{
  "host": "server.database.windows.net",
  "port": 1433,
  "database": "master",
  "ssl_mode": {
    "mode": "unencrypted"
  },
  "replication_method": {
    "method": "STANDARD"
  },
  "client_id": "client-uuid",
  "client_secret": "client-secret-value"
}
"""
    }
}
