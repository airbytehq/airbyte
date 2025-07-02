/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.salesforce

import com.google.common.base.Suppliers
import dev.failsafe.RetryPolicy
import io.airbyte.cdk.load.check.dlq.DlqChecker
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.http.HttpClient
import io.airbyte.cdk.load.http.authentication.OAuthAuthenticator
import io.airbyte.cdk.load.http.okhttp.AirbyteOkHttpClient
import io.airbyte.cdk.load.pipeline.LoadPipeline
import io.airbyte.cdk.load.write.dlq.DlqPipelineFactory
import io.airbyte.cdk.load.write.object_storage.ObjectLoader
import io.airbyte.integrations.destination.salesforce.io.airbyte.integrations.destination.salesforce.http.SalesforceOperationRepository
import io.airbyte.integrations.destination.salesforce.io.airbyte.integrations.destination.salesforce.http.job.JobRepository
import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton
import java.lang.IllegalStateException
import java.util.function.Supplier
import okhttp3.OkHttpClient

@Factory
class SalesforceBeanFactory {
    @Singleton
    fun check(httpClient: HttpClient, baseUrl: Supplier<String>, dlqChecker: DlqChecker) =
        SalesforceChecker(httpClient, baseUrl, dlqChecker)

    @Singleton
    fun discover(operationRepository: SalesforceOperationRepository) =
        SalesforceDiscoverer(operationRepository)

    @Singleton fun getConfig(config: DestinationConfiguration) = config as SalesforceConfiguration

    @Singleton
    fun getAuthenticator(config: SalesforceConfiguration): OAuthAuthenticator {
        val authEndpoint: String =
            "https://${if (config.isSandbox) "test" else "login"}.salesforce.com/services/oauth2/token"
        return OAuthAuthenticator(
            authEndpoint,
            config.clientId,
            config.clientSecret,
            config.refreshToken
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
