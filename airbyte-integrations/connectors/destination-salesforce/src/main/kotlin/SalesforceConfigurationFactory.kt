/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.salesforce

import io.airbyte.cdk.load.command.DestinationConfigurationFactory
import io.airbyte.cdk.load.command.dlq.toObjectStorageConfig
import jakarta.inject.Singleton

@Singleton
class SalesforceConfigurationFactory :
    DestinationConfigurationFactory<SalesforceSpecification, SalesforceConfiguration> {
    override fun makeWithoutExceptionHandling(
        pojo: SalesforceSpecification
    ): SalesforceConfiguration {
        return SalesforceConfiguration(
            clientId = pojo.clientId,
            clientSecret = pojo.clientSecret,
            refreshToken = pojo.refreshToken,
            isSandbox = pojo.isSandbox,
            objectStorageConfig = pojo.objectStorageConfig.toObjectStorageConfig(),
        )
    }
}
