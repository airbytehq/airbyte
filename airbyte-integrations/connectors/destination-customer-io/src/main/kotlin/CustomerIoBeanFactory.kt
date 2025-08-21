/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.customerio

import dev.failsafe.RetryPolicy
import io.airbyte.cdk.Operation
import io.airbyte.cdk.load.check.CheckOperationWithoutGeneric
import io.airbyte.cdk.load.check.dlq.DlqChecker
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.http.HttpClient
import io.airbyte.cdk.load.http.authentication.BasicAccessAuthenticator
import io.airbyte.cdk.load.http.okhttp.AirbyteOkHttpClient
import io.airbyte.cdk.load.lowcode.DeclarativeDestinationFactory
import io.airbyte.cdk.load.pipeline.LoadPipeline
import io.airbyte.cdk.load.write.dlq.DlqPipelineFactory
import io.airbyte.cdk.load.write.object_storage.ObjectLoader
import io.airbyte.cdk.output.OutputConsumer
import io.airbyte.cdk.spec.SpecificationFactory
import io.micronaut.context.annotation.Factory as MicronautFactory
import io.micronaut.context.annotation.Primary
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton
import okhttp3.OkHttpClient

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
    ): Operation = CheckOperationWithoutGeneric(factory.createDestinationChecker(checker), outputConsumer)

    @Primary
    @Singleton
    fun specificationFactory(
        factory: DeclarativeDestinationFactory,
    ): SpecificationFactory = factory.createSpecificationFactory()

    @Singleton
    fun destinationFactory(
        config: CustomerIoConfiguration
    ): DeclarativeDestinationFactory = DeclarativeDestinationFactory(config)

    // TODO replace for ObjectStorageConfigProvider
    @Singleton fun getConfig(config: DestinationConfiguration) = config as CustomerIoConfiguration

    @Singleton fun discover() = CustomerIoDiscoverer()

    @Singleton
    fun objectLoader(): ObjectLoader =
        object : ObjectLoader {
            override val inputPartitions = 1
            override val numPartWorkers = 1
        }

    // TODO to replace for declarative config
    @Singleton
    fun httpClient(config: CustomerIoConfiguration): HttpClient {
        val authenticator =
            BasicAccessAuthenticator(config.credentials.siteId, config.credentials.apiKey)
        val okhttpClient: OkHttpClient =
            OkHttpClient.Builder().addInterceptor(authenticator).build()
        return AirbyteOkHttpClient(okhttpClient, RetryPolicy.ofDefaults())
    }

    @Singleton
    fun loadPipeline(
        catalog: DestinationCatalog,
        dlqPipelineFactory: DlqPipelineFactory,
        httpClient: HttpClient,
    ): LoadPipeline = dlqPipelineFactory.createPipeline(CustomerIoLoader(httpClient, catalog))
}
