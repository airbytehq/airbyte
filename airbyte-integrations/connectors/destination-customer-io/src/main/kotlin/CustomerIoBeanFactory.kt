/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.customerio

import dev.failsafe.RetryPolicy
import io.airbyte.cdk.Operation
import io.airbyte.cdk.load.check.CheckOperationV2
import io.airbyte.cdk.load.check.dlq.DlqChecker
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.http.HttpClient
import io.airbyte.cdk.load.http.authentication.BasicAccessAuthenticator
import io.airbyte.cdk.load.http.okhttp.AirbyteOkHttpClient
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

    @Singleton fun discover() = CustomerIoDiscoverer()

    @Singleton
    fun objectLoader(): ObjectLoader =
        object : ObjectLoader {
            override val inputPartitions = 1
            override val numPartWorkers = 1
        }

    /**
     * Until we migrate everything to low-code, we still need to keep that for the write operation,
     * but we expect this to be instantiated by the DeclarativeDestinationFactory.
     */
    @Singleton
    fun httpClient(factory: DeclarativeDestinationFactory): HttpClient {
        if (factory.config == null) {
            throw IllegalArgumentException(
                "Configuration was not provided and therefore HttpClient can't be instantiated"
            )
        }

        val authenticator =
            BasicAccessAuthenticator(
                factory.config!!.get("credentials").get("siteId").asText(),
                factory.config!!.get("credentials").get("apiKey").asText(),
            )
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
