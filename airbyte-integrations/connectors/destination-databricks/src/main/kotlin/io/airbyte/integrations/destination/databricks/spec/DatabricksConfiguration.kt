/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks.spec

import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationConfigurationFactory
import jakarta.inject.Singleton

data class DatabricksConfiguration(
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
class DatabricksConfigurationFactory :
    DestinationConfigurationFactory<DatabricksSpecification, DatabricksConfiguration> {
    override fun makeWithoutExceptionHandling(
        pojo: DatabricksSpecification
    ): DatabricksConfiguration =
        DatabricksConfiguration(
            acceptTerms = pojo.acceptTerms,
            hostname = pojo.hostname,
            httpPath = pojo.httpPath,
            port = pojo.port?.takeIf { it.isNotBlank() } ?: "443",
            database = pojo.database,
            schema = pojo.schema?.takeIf { it.isNotBlank() } ?: "default",
            authType = pojo.authentication.toConfiguration(),
            purgeStagingData = pojo.purgeStagingData ?: true,
            cdcDeletionMode = pojo.cdcDeletionMode ?: CdcDeletionMode.HARD_DELETE,
        )
}

private fun DatabricksAuthSpecification.toConfiguration(): DatabricksAuthConfiguration =
    when (this) {
        is OAuthSpecification -> OAuthConfiguration(clientId, secret)
        is PersonalAccessTokenSpecification -> PersonalAccessTokenConfiguration(personalAccessToken)
    }
