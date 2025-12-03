/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres.spec

import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationConfigurationFactory
import io.airbyte.cdk.load.write.db.DbConstants
import io.airbyte.cdk.ssh.SshTunnelMethodConfiguration
import jakarta.inject.Singleton

data class PostgresConfiguration(
    val host: String,
    val port: Int,
    val database: String,
    val schema: String,
    val username: String,
    val password: String?,
    val ssl: Boolean,
    val sslMode: SslMode?,
    val jdbcUrlParams: String?,
    val cdcDeletionMode: CdcDeletionMode,
    val legacyRawTablesOnly: Boolean,
    val internalTableSchema: String?,
    val dropCascade: Boolean?,
    val unconstrainedNumber: Boolean?,
    val tunnelMethod: SshTunnelMethodConfiguration?,
) : DestinationConfiguration()

@Singleton
class PostgresConfigurationFactory :
    DestinationConfigurationFactory<PostgresSpecification, PostgresConfiguration> {
    override fun makeWithoutExceptionHandling(pojo: PostgresSpecification): PostgresConfiguration {
        return makeWithOverrides(spec = pojo)
    }

    fun makeWithOverrides(
        spec: PostgresSpecification,
        overrides: Map<String, String> = emptyMap()
    ): PostgresConfiguration {
        return PostgresConfiguration(
            host = overrides.getOrDefault("host", spec.host),
            port = overrides.getOrDefault("port", spec.port.toString()).toInt(),
            database = overrides.getOrDefault("database", spec.database),
            schema = overrides.getOrDefault("schema", spec.schema),
            username = overrides.getOrDefault("username", spec.username),
            password = overrides.getOrDefault("password", spec.password),
            ssl = spec.ssl ?: true,
            sslMode = spec.sslMode,
            jdbcUrlParams = overrides.getOrDefault("jdbcUrlParams", spec.jdbcUrlParams),
            cdcDeletionMode = spec.cdcDeletionMode ?: CdcDeletionMode.HARD_DELETE,
            legacyRawTablesOnly = spec.legacyRawTablesOnly ?: false,
            internalTableSchema =
                if (spec.legacyRawTablesOnly == true) {
                    if (spec.internalTableSchema.isNullOrBlank()) {
                        DbConstants.DEFAULT_RAW_TABLE_NAMESPACE
                    } else {
                        spec.internalTableSchema
                    }
                } else {
                    null
                },
            dropCascade = spec.dropCascade ?: false,
            unconstrainedNumber = spec.unconstrainedNumber ?: false,
            tunnelMethod = spec.getTunnelMethodValue()
        )
    }
}
