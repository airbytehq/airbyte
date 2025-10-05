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
    val sslMode: SslMode?,
    val jdbcUrlParams: String?,
    val cdcDeletionMode: CdcDeletionMode,
    val legacyRawTablesOnly: Boolean?,
    val internalTableSchema: String?,
    val tunnelMethod: SshTunnelMethodConfiguration?,
) : DestinationConfiguration()

@Singleton
class PostgresConfigurationFactory :
    DestinationConfigurationFactory<PostgresSpecification, PostgresConfiguration> {
    override fun makeWithoutExceptionHandling(
        pojo: PostgresSpecification
    ): PostgresConfiguration {
        return PostgresConfiguration(
            host = pojo.host,
            port = pojo.port,
            database = pojo.database,
            schema = pojo.schema,
            username = pojo.username,
            password = pojo.password,
            sslMode = pojo.sslMode,
            jdbcUrlParams = pojo.jdbcUrlParams,
            cdcDeletionMode = pojo.cdcDeletionMode ?: CdcDeletionMode.HARD_DELETE,
            legacyRawTablesOnly = pojo.legacyRawTablesOnly ?: false,
            internalTableSchema =
                if (pojo.legacyRawTablesOnly == true) {
                    if (pojo.internalTableSchema.isNullOrBlank()) {
                        DbConstants.DEFAULT_RAW_TABLE_NAMESPACE
                    } else {
                        pojo.internalTableSchema
                    }
                } else {
                    null
                },
            tunnelMethod = pojo.getTunnelMethodValue()
        )
    }
}
