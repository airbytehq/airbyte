/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.hubspot

import io.airbyte.cdk.load.command.DestinationConfigurationFactory
import io.airbyte.cdk.load.command.dlq.toObjectStorageConfig
import jakarta.inject.Singleton

@Singleton
class HubSpotConfigurationFactory :
    DestinationConfigurationFactory<HubSpotSpecification, HubSpotConfiguration> {
    override fun makeWithoutExceptionHandling(pojo: HubSpotSpecification): HubSpotConfiguration {
        val oauthCredentials = pojo.credentials as OAuthCredentialsSpec
        return HubSpotConfiguration(
            credentials =
                OAuthCredentialsConfig(
                    oauthCredentials.clientId,
                    oauthCredentials.clientSecret,
                    oauthCredentials.refreshToken
                ),
            objectStorageConfig = pojo.objectStorageConfig.toObjectStorageConfig(),
        )
    }
}
