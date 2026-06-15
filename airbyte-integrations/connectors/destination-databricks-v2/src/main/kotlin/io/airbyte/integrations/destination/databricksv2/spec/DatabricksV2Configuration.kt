/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricksv2.spec

import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationConfigurationFactory
import jakarta.inject.Singleton

data class DatabricksV2Configuration(
    val hostname: String,
    val httpPath: String,
    val port: String,
    val database: String,
    val schema: String,
    val authType: DatabricksAuthConfiguration,
    val purgeStagingData: Boolean,
    val acceptTerms: Boolean,
    val cdcDeletionMode: CdcDeletionMode,
) : DestinationConfiguration()

sealed interface DatabricksAuthConfiguration

data class OAuthConfiguration(
    val clientId: String,
    val secret: String,
) : DatabricksAuthConfiguration

data class PersonalAccessTokenConfiguration(
    val personalAccessToken: String,
) : DatabricksAuthConfiguration

@Singleton
class DatabricksV2ConfigurationFactory :
    DestinationConfigurationFactory<DatabricksV2Specification, DatabricksV2Configuration> {
    override fun makeWithoutExceptionHandling(
        pojo: DatabricksV2Specification
    ): DatabricksV2Configuration =
        DatabricksV2Configuration(
            acceptTerms = pojo.acceptTerms,
            hostname = pojo.hostname,
            httpPath = pojo.httpPath,
            port = pojo.port.ifBlank { "443" },
            database = pojo.database,
            schema = pojo.schema.ifBlank { "default" },
            authType = pojo.authentication.toConfiguration(),
            purgeStagingData = pojo.purgeStagingData ?: true,
            cdcDeletionMode = pojo.cdcDeletionMode ?: CdcDeletionMode.HARD_DELETE,
        )
}

private fun DatabricksAuthSpecification?.toConfiguration(): DatabricksAuthConfiguration =
    when (this) {
        is OAuthSpecification -> OAuthConfiguration(clientId, secret)
        is PersonalAccessTokenSpecification -> PersonalAccessTokenConfiguration(personalAccessToken)
        null -> throw IllegalArgumentException("Authentication configuration is required.")
    }
