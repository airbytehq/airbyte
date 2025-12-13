/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.hubspot

import io.airbyte.cdk.Operation
import io.airbyte.cdk.command.CONNECTOR_CONFIG_PREFIX
import io.airbyte.cdk.load.check.CheckOperationV2
import io.airbyte.cdk.load.check.dlq.DlqChecker
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.http.HttpClient
import io.airbyte.cdk.load.http.authentication.OAuthAuthenticator
import io.airbyte.cdk.load.http.okhttp.AirbyteOkHttpClient
import io.airbyte.cdk.load.lowcode.DeclarativeDestinationFactory
import io.airbyte.cdk.load.pipeline.LoadPipeline
import io.airbyte.cdk.load.write.dlq.DlqPipelineFactory
import io.airbyte.cdk.load.write.object_storage.ObjectLoader
import io.airbyte.cdk.output.OutputConsumer
import io.airbyte.cdk.util.Jsons
import io.airbyte.integrations.destination.hubspot.http.HubSpotOperationRepository
import io.airbyte.integrations.destination.hubspot.io.airbyte.integrations.destination.hubspot.http.HubSpotObjectTypeIdMapper
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Primary
import io.micronaut.context.annotation.Requires
import io.micronaut.context.annotation.Value
import jakarta.inject.Singleton
import okhttp3.OkHttpClient

@Factory
class HubSpotBeanFactory {
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
    fun factory(
        @Value("\${${CONNECTOR_CONFIG_PREFIX}.json}") jsonPropertyValue: String? = null,
    ): DeclarativeDestinationFactory =
        DeclarativeDestinationFactory(Jsons.readTree(jsonPropertyValue))

    @Singleton
    fun discover(httpClient: HttpClient): HubSpotDiscoverer {
        return HubSpotDiscoverer(HubSpotOperationRepository(httpClient))
    }

    @Singleton fun getConfig(config: DestinationConfiguration) = config as HubSpotConfiguration

    @Singleton
    fun getAuthenticator(config: HubSpotConfiguration): OAuthAuthenticator {
        when (config.credentials.type) {
            "OAuth" -> {
                val credentials = config.credentials as OAuthCredentialsConfig
                return OAuthAuthenticator(
                    "https://api.hubapi.com/oauth/v1/token",
                    credentials.clientId,
                    credentials.clientSecret,
                    credentials.refreshToken
                )
            }
            else ->
                throw IllegalArgumentException(
                    "Unsupported authenticator type: ${config.credentials.type}"
                )
        }
    }

    @Singleton
    fun getHttpClient(authenticator: OAuthAuthenticator): HttpClient {
        val okhttpClient: OkHttpClient =
            OkHttpClient.Builder().addInterceptor(authenticator).build()
        return AirbyteOkHttpClient(okhttpClient)
    }

    @Singleton
    fun objectLoader(): ObjectLoader =
        object : ObjectLoader {
            override val inputPartitions = 1
            override val numPartWorkers = 1
        }

    @Singleton
    fun loadPipeline(
        catalog: DestinationCatalog,
        httpClient: HttpClient,
        dlqPipelineFactory: DlqPipelineFactory,
    ): LoadPipeline =
        dlqPipelineFactory.createPipeline(
            HubSpotLoader(httpClient, HubSpotObjectTypeIdMapper(httpClient), catalog)
        )

    @Singleton fun writer() = HubSpotWriter()
}
