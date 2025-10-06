/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.hubspot

import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.dlq.ObjectStorageConfig
import io.airbyte.cdk.load.command.dlq.ObjectStorageConfigProvider

sealed interface CredentialsConfig {
    val type: String
}

class OAuthCredentialsConfig(
    val clientId: String,
    val clientSecret: String,
    val refreshToken: String
) : CredentialsConfig {
    override val type: String = "OAuth"
}

data class HubSpotConfiguration(
    val credentials: CredentialsConfig,
    override val objectStorageConfig: ObjectStorageConfig,
) : DestinationConfiguration(), ObjectStorageConfigProvider
