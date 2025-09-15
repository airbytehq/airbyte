/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.salesforce

import com.google.common.base.Suppliers
import dev.failsafe.RetryPolicy
import io.airbyte.cdk.Operation
import io.airbyte.cdk.load.check.CheckOperationV2
import io.airbyte.cdk.load.check.dlq.DlqChecker
import io.airbyte.cdk.load.checker.CompositeDlqChecker
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.http.HttpClient
import io.airbyte.cdk.load.http.authentication.OAuthAuthenticator
import io.airbyte.cdk.load.http.okhttp.AirbyteOkHttpClient
import io.airbyte.cdk.load.lowcode.DeclarativeDestinationFactory
import io.airbyte.cdk.load.pipeline.LoadPipeline
import io.airbyte.cdk.load.spec.DeclarativeCdkConfiguration
import io.airbyte.cdk.load.write.dlq.DlqPipelineFactory
import io.airbyte.cdk.load.write.object_storage.ObjectLoader
import io.airbyte.cdk.output.OutputConsumer
import io.airbyte.cdk.spec.SpecificationFactory
import io.airbyte.cdk.util.Jsons
import io.airbyte.integrations.destination.salesforce.io.airbyte.integrations.destination.salesforce.http.SalesforceOperationRepository
import io.airbyte.integrations.destination.salesforce.io.airbyte.integrations.destination.salesforce.http.job.JobRepository
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Primary
import io.micronaut.context.annotation.Requires
import io.micronaut.context.annotation.Value
import jakarta.inject.Singleton
import java.lang.IllegalStateException
import java.util.function.Supplier
import okhttp3.OkHttpClient

@Factory
class SalesforceBeanFactory {

    @Primary
    @Singleton
    @Requires(property = Operation.PROPERTY, value = "check")
    @Requires(env = ["destination"])
    fun checkOperation(
        httpClient: HttpClient,
        baseUrl: Supplier<String>,
        dlqChecker: DlqChecker,
        config: DeclarativeCdkConfiguration,
        outputConsumer: OutputConsumer
    ): Operation =
        CheckOperationV2(
            CompositeDlqChecker(
                SalesforceChecker(httpClient, baseUrl),
                dlqChecker,
                config.objectStorageConfig,
            ),
            outputConsumer,
        )

    @Singleton
    fun discover(operationRepository: SalesforceOperationRepository) =
        SalesforceDiscoverer(operationRepository)

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
    fun getAuthenticator(factory: DeclarativeDestinationFactory): OAuthAuthenticator {
        if (factory.config == null) {
            throw IllegalArgumentException(
                "Config should be provided when running operations that requires authentication"
            )
        }

        val authEndpoint =
            "https://${if (factory.config!!.get("is_sandbox").asBoolean()) "test" else "login"}.salesforce.com/services/oauth2/token"
        return OAuthAuthenticator(
            authEndpoint,
            factory.config!!.get("client_id").asText(),
            factory.config!!.get("client_secret").asText(),
            factory.config!!.get("refresh_token").asText(),
        )
    }

    @Singleton
    fun getBaseUrlSupplier(authenticator: OAuthAuthenticator): Supplier<String> {
        return Suppliers.memoize {
            authenticator.queryForAccessToken().get("instance_url")?.asText()
                ?: throw IllegalStateException(
                    "Authentication failed: Could not extract `instance_url` from authentication response."
                )
        }
    }

    @Singleton
    fun getHttpClient(authenticator: OAuthAuthenticator): HttpClient {
        val okhttpClient: OkHttpClient =
            OkHttpClient.Builder().addInterceptor(authenticator).build()
        return AirbyteOkHttpClient(okhttpClient, RetryPolicy.ofDefaults())
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
        dlqPipelineFactory: DlqPipelineFactory,
        jobRepository: JobRepository,
    ): LoadPipeline = dlqPipelineFactory.createPipeline(SalesforceLoader(jobRepository, catalog))
}
