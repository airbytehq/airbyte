/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.customerio

import io.airbyte.cdk.load.command.DestinationConfigurationFactory
import io.airbyte.cdk.load.command.dlq.toObjectStorageConfig
import jakarta.inject.Singleton

@Singleton
class CustomerIoConfigurationFactory :
    DestinationConfigurationFactory<CustomerIoSpecification, CustomerIoConfiguration> {
    override fun makeWithoutExceptionHandling(
        pojo: CustomerIoSpecification
    ): CustomerIoConfiguration {
        return CustomerIoConfiguration(
            credentials =
                CustomerIoCredentialsConfig(pojo.credentials.siteId, pojo.credentials.apiKey),
            objectStorageConfig = pojo.objectStorageConfig.toObjectStorageConfig(),
        )
    }
}
