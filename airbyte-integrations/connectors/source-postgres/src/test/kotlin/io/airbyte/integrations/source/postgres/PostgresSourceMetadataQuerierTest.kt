/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.check.JdbcCheckQueries
import io.airbyte.cdk.command.FeatureFlag
import io.airbyte.cdk.discover.JdbcMetadataQuerier
import io.airbyte.cdk.jdbc.DefaultJdbcConstants
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.cdk.ssh.SshNoTunnelMethod
import io.airbyte.integrations.source.postgres.config.EncryptionAllow
import io.airbyte.integrations.source.postgres.config.PostgresSourceConfiguration
import io.airbyte.integrations.source.postgres.config.PostgresSourceConfigurationFactory
import io.airbyte.integrations.source.postgres.config.PostgresSourceConfigurationSpecification
import io.airbyte.integrations.source.postgres.config.StandardReplicationMethodConfigurationSpecification
import io.airbyte.integrations.source.postgres.operations.PostgresSourceFieldTypeMapper
import io.airbyte.integrations.source.postgres.operations.PostgresSourceSelectQueryGenerator
import io.mockk.every
import io.mockk.mockk
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Test

class PostgresSourceMetadataQuerierTest {

    @Test
    fun `extraChecks rejects unsafe SSL mode in cloud without echoing configured value`() {
        val config = postgresConfigWithAllowSsl()
        val querier =
            PostgresSourceMetadataQuerier(
                base = mockJdbcMetadataQuerier(config),
                postgresSourceConfig = config,
                featureFlags = setOf(FeatureFlag.AIRBYTE_CLOUD_DEPLOYMENT)
            )

        val exception =
            assertThrows(ConfigErrorException::class.java) { querier.validateSslConfiguration() }

        assertEquals(
            "Airbyte Cloud Postgres connections require SSL mode \"require\", \"verify-ca\", \"verify-full\", or an SSH tunnel.",
            exception.message,
        )
    }

    @Test
    fun `extraChecks allows unsafe SSL mode outside cloud`() {
        val config = postgresConfigWithAllowSsl()
        val querier =
            PostgresSourceMetadataQuerier(
                base = mockJdbcMetadataQuerier(config),
                postgresSourceConfig = config,
                featureFlags = emptySet()
            )

        querier.validateSslConfiguration()
    }

    private fun mockJdbcMetadataQuerier(config: PostgresSourceConfiguration): JdbcMetadataQuerier {
        return JdbcMetadataQuerier(
            constants = DefaultJdbcConstants(),
            config = config,
            selectQueryGenerator = PostgresSourceSelectQueryGenerator(),
            fieldTypeMapper = PostgresSourceFieldTypeMapper(),
            checkQueries = JdbcCheckQueries(),
            jdbcConnectionFactory =
                mockk<JdbcConnectionFactory>(relaxed = true) {
                    every { get() } returns mockk(relaxed = true)
                }
        )
    }

    private fun postgresConfigWithAllowSsl(): PostgresSourceConfiguration {
        val configSpec =
            PostgresSourceConfigurationSpecification().apply {
                host = "localhost"
                port = 5432
                username = "user"
                password = "password"
                database = "database"
                setEncryptionValue(EncryptionAllow)
                setTunnelMethodValue(SshNoTunnelMethod)
                setIncrementalConfigurationSpecificationValue(
                    StandardReplicationMethodConfigurationSpecification
                )
            }
        return PostgresSourceConfigurationFactory().makeWithoutExceptionHandling(configSpec)
    }
}
