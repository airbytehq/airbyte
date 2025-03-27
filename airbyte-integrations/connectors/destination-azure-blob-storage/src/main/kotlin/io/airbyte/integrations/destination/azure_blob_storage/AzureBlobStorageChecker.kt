/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.azure_blob_storage

import io.airbyte.cdk.load.check.DestinationChecker
import io.airbyte.cdk.load.command.DestinationConfiguration
import javax.inject.Singleton

// TODO use actual azure config object once it exists
@Singleton
class AzureBlobStorageChecker : DestinationChecker<DestinationConfiguration> {
    override fun check(config: DestinationConfiguration) {
        // TODO check the config
    }
}
