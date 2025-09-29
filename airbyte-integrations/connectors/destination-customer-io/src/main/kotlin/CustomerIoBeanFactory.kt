/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.customerio

import io.airbyte.cdk.Operation
import io.airbyte.cdk.load.check.CheckOperationV2
import io.airbyte.cdk.load.check.dlq.DlqChecker
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.lowcode.DeclarativeDestinationFactory
import io.airbyte.cdk.load.pipeline.LoadPipeline
import io.airbyte.cdk.load.spec.DeclarativeCdkConfiguration
import io.airbyte.cdk.load.write.dlq.DlqPipelineFactory
import io.airbyte.cdk.load.write.object_storage.ObjectLoader
import io.airbyte.cdk.output.OutputConsumer
import io.airbyte.cdk.spec.SpecificationFactory
import io.airbyte.cdk.util.Jsons
import io.micronaut.context.annotation.Factory as MicronautFactory
import io.micronaut.context.annotation.Primary
import io.micronaut.context.annotation.Requires
import io.micronaut.context.annotation.Value
import jakarta.inject.Singleton

@MicronautFactory
class CustomerIoBeanFactory {
    @Primary
    @Singleton
    @Requires(property = Operation.PROPERTY, value = "check")
    @Requires(env = ["destination"])
    fun checkOperation(
        factory: DeclarativeDestinationFactory,
        checker: DlqChecker,
        outputConsumer: OutputConsumer
    ): Operation = CheckOperationV2(factory.createDestinationChecker(checker), outputConsumer)

    @Singleton
    fun connectorFactory(
        @Value("\${airbyte.connector.config.json}") configAsJsonString: String? = null,
    ): DeclarativeDestinationFactory =
        DeclarativeDestinationFactory(
            configAsJsonString?.let { Jsons.readTree(configAsJsonString) }
        )

    @Primary
    @Singleton
    fun cdkConfiguration(factory: DeclarativeDestinationFactory): DeclarativeCdkConfiguration =
        factory.cdkConfiguration

    @Primary
    @Singleton
    fun specificationFactory(
        factory: DeclarativeDestinationFactory,
    ): SpecificationFactory = factory.createSpecificationFactory()

    @Singleton
    fun discover(
        factory: DeclarativeDestinationFactory,
    ) = CustomerIoDiscoverer(factory.createOperationProvider())

    @Singleton
    fun objectLoader(): ObjectLoader =
        object : ObjectLoader {
            override val inputPartitions = 1
            override val numPartWorkers = 1
        }

    @Singleton
    fun loadPipeline(
        catalog: DestinationCatalog,
        factory: DeclarativeDestinationFactory,
        dlqPipelineFactory: DlqPipelineFactory,
    ): LoadPipeline = dlqPipelineFactory.createPipeline(factory.createStreamLoader(catalog))

    @Singleton fun writer(factory: DeclarativeDestinationFactory) = factory.createWriter()
}
