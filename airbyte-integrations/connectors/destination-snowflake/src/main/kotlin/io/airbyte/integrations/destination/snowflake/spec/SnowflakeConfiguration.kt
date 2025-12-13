/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.spec

import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationConfigurationFactory
import io.airbyte.cdk.load.write.db.DbConstants
import jakarta.inject.Singleton

data class SnowflakeConfiguration(
    val host: String,
    val role: String,
    val warehouse: String,
    val database: String,
    val schema: String,
    val username: String,
    val authType: AuthTypeConfiguration,
    val cdcDeletionMode: CdcDeletionMode,
    val legacyRawTablesOnly: Boolean,
    val internalTableSchema: String,
    val jdbcUrlParams: String?,
    val retentionPeriodDays: Int,
) : DestinationConfiguration()

sealed interface AuthTypeConfiguration

data class KeyPairAuthConfiguration(
    val privateKey: String,
    val privateKeyPassword: String?,
) : AuthTypeConfiguration

data class UsernamePasswordAuthConfiguration(
    val password: String,
) : AuthTypeConfiguration

@Singleton
class SnowflakeConfigurationFactory :
    DestinationConfigurationFactory<SnowflakeSpecification, SnowflakeConfiguration> {
    override fun makeWithoutExceptionHandling(
        pojo: SnowflakeSpecification
    ): SnowflakeConfiguration {
        val authTypeConfig =
            when (pojo.credentials) {
                is KeyPairAuthSpecification -> {
                    // Despite what Kotlin thinks, this cast is necessary
                    @Suppress("USELESS_CAST")
                    val keyPairAuthSpec = pojo.credentials as KeyPairAuthSpecification
                    KeyPairAuthConfiguration(
                        keyPairAuthSpec.privateKey,
                        keyPairAuthSpec.privateKeyPassword
                    )
                }
                is UsernamePasswordAuthSpecification -> {
                    // Despite what Kotlin thinks, this cast is necessary
                    @Suppress("USELESS_CAST")
                    val usernamePasswordAuthSpec =
                        pojo.credentials as UsernamePasswordAuthSpecification
                    UsernamePasswordAuthConfiguration(usernamePasswordAuthSpec.password)
                }
                null -> {
                    UsernamePasswordAuthConfiguration("")
                }
            }

        return SnowflakeConfiguration(
            host = pojo.host,
            role = pojo.role,
            warehouse = pojo.warehouse,
            database = pojo.database,
            schema = pojo.schema,
            username = pojo.username,
            authType = authTypeConfig,
            cdcDeletionMode = pojo.cdcDeletionMode ?: CdcDeletionMode.HARD_DELETE,
            legacyRawTablesOnly = pojo.legacyRawTablesOnly ?: false,
            internalTableSchema =
                if (pojo.internalTableSchema.isNullOrBlank()) {
                    DbConstants.DEFAULT_RAW_TABLE_NAMESPACE
                } else {
                    pojo.internalTableSchema!!
                },
            jdbcUrlParams = pojo.jdbcUrlParams,
            retentionPeriodDays = pojo.retentionPeriodDays ?: 1
        )
    }
}
