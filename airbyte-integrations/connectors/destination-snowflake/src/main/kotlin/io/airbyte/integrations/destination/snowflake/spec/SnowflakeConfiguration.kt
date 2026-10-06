/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.spec

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationConfigurationFactory
import io.airbyte.cdk.load.table.DEFAULT_AIRBYTE_INTERNAL_NAMESPACE
import io.airbyte.integrations.destination.snowflake.auth.WorkloadIdentityProvider
import jakarta.inject.Singleton
import java.nio.file.InvalidPathException
import java.nio.file.Path

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
    val trimSpace: Boolean,
    val jdbcUrlParams: String?,
    val retentionPeriodDays: Int,
    val numberDataTypeConversion: NumberDataType = NumberDataType.FLOAT,
) : DestinationConfiguration()

sealed interface AuthTypeConfiguration

data class KeyPairAuthConfiguration(
    val privateKey: String,
    val privateKeyPassword: String?,
) : AuthTypeConfiguration

data class UsernamePasswordAuthConfiguration(
    val password: String,
) : AuthTypeConfiguration

data class WorkloadIdentityAuthConfiguration(
    val provider: WorkloadIdentityProvider,
    val tokenFilePath: String? = null,
    val entraResource: String? = null,
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
                is WorkloadIdentityAuthSpecification -> {
                    @Suppress("USELESS_CAST")
                    val workloadIdentitySpec = pojo.credentials as WorkloadIdentityAuthSpecification
                    workloadIdentityConfiguration(workloadIdentitySpec)
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
                    DEFAULT_AIRBYTE_INTERNAL_NAMESPACE
                } else {
                    pojo.internalTableSchema!!
                },
            trimSpace = pojo.trimSpace ?: true,
            jdbcUrlParams = pojo.jdbcUrlParams,
            retentionPeriodDays = pojo.retentionPeriodDays ?: 1,
            numberDataTypeConversion = pojo.numberDataTypeConversion ?: NumberDataType.FLOAT,
        )
    }

    private fun workloadIdentityConfiguration(
        spec: WorkloadIdentityAuthSpecification
    ): WorkloadIdentityAuthConfiguration {
        val provider =
            spec.workloadIdentityProvider
                ?: throw ConfigErrorException(
                    "workload_identity_provider is required for workload identity federation."
                )
        val tokenFilePath = spec.tokenFilePath?.takeUnless { it.isBlank() }
        if (provider == WorkloadIdentityProvider.OIDC) {
            if (tokenFilePath == null) {
                throw ConfigErrorException(
                    "token_file_path is required for OIDC workload identity federation."
                )
            }
            val absolute =
                try {
                    Path.of(tokenFilePath).isAbsolute
                } catch (_: InvalidPathException) {
                    false
                }
            if (!absolute) {
                throw ConfigErrorException(
                    "token_file_path must be a valid absolute path inside the connector container."
                )
            }
        } else if (tokenFilePath != null) {
            throw ConfigErrorException(
                "token_file_path is only supported with the OIDC workload identity provider."
            )
        }
        if (spec.entraResource != null) {
            if (provider != WorkloadIdentityProvider.AZURE || spec.entraResource.isBlank()) {
                throw ConfigErrorException(
                    "entra_resource must be non-empty and is only supported with the AZURE workload identity provider."
                )
            }
        }
        // Validate the configuration without reading credentials or contacting an identity
        // provider.
        return WorkloadIdentityAuthConfiguration(provider, tokenFilePath, spec.entraResource)
    }
}
