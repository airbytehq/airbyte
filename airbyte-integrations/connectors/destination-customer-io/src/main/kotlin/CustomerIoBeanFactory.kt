/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.customerio

import dev.failsafe.RetryPolicy
import io.airbyte.cdk.load.check.DestinationChecker
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
import io.micronaut.context.annotation.Factory as MicronautFactory
import jakarta.inject.Singleton
import okhttp3.OkHttpClient

@MicronautFactory
class CustomerIoBeanFactory {
    @Singleton
    fun check(
        factory: DeclarativeDestinationFactory<CustomerIoConfiguration>,
        checker: DlqChecker,
    ): DestinationChecker<CustomerIoConfiguration> = factory.createDestinationChecker(checker)

    @Singleton
    fun factory(
        config: CustomerIoConfiguration
    ): DeclarativeDestinationFactory<CustomerIoConfiguration> =
        DeclarativeDestinationFactory(config)

    @Singleton fun getConfig(config: DestinationConfiguration) = config as CustomerIoConfiguration

    @Singleton fun discover() = CustomerIoDiscoverer()

    @Singleton
    fun objectLoader(): ObjectLoader =
        object : ObjectLoader {
            override val inputPartitions = 1
            override val numPartWorkers = 1
        }

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
