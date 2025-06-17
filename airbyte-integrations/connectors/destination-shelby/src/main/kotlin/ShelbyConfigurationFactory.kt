package io.airbyte.integrations.destination.shelby

import io.airbyte.cdk.load.command.DestinationConfigurationFactory
import io.airbyte.cdk.load.command.dlq.ObjectStorageConfig
import io.airbyte.cdk.load.command.dlq.toObjectStorageConfig
import io.airbyte.cdk.load.command.object_storage.ObjectStoragePathConfiguration
import jakarta.inject.Singleton

@Singleton
class ShelbyConfigurationFactory :
    DestinationConfigurationFactory<ShelbySpecification, ShelbyConfiguration> {
    override fun makeWithoutExceptionHandling(pojo: ShelbySpecification): ShelbyConfiguration =
        ShelbyConfiguration(
            objectStorageConfig = pojo.objectStorageConfig.toObjectStorageConfig(),
        )
}
