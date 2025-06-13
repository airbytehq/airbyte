package io.airbyte.integrations.destination.shelby

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.dlq.ObjectStorageConfig
import io.airbyte.cdk.load.pipeline.LoadPipeline
import io.airbyte.cdk.load.write.dlq.DlqPipelineFactory
import io.airbyte.cdk.load.write.object_storage.ObjectLoader
import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton

@Factory
class ShelbyBeanFactory {
    @Singleton
    fun check() = ShelbyChecker()

    @Singleton
    fun discover() = ShelbyDiscoverer()

    @Singleton
    fun getConfig(config: DestinationConfiguration) = config as ShelbyConfiguration

    @Singleton
    fun objectLoader(): ObjectLoader = object : ObjectLoader {
        override val inputPartitions = 1
        override val numPartWorkers = 1
    }

    @Singleton
    fun loadPipeline(
        catalog: DestinationCatalog,
        dlqPipelineFactory: DlqPipelineFactory,
    ): LoadPipeline = dlqPipelineFactory.createPipeline(ShelbyLoader(catalog = catalog))
}
