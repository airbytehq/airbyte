package io.airbyte.integrations.destination.shelby

import dev.failsafe.RetryPolicy
import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.http.HttpClient
import io.airbyte.cdk.load.http.authentication.OAuthAuthenticator
import io.airbyte.cdk.load.http.okhttp.AirbyteOkHttpClient
import io.airbyte.integrations.destination.shelby.http.clientId
import io.airbyte.integrations.destination.shelby.http.clientSecret
import io.airbyte.integrations.destination.shelby.http.discover.SalesforceOperationRepository
import io.airbyte.integrations.destination.shelby.http.isSandbox
import io.airbyte.integrations.destination.shelby.http.refreshToken
import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton
import okhttp3.OkHttpClient

@Factory
class ShelbyBeanFactory {
    @Singleton
    fun check() = ShelbyChecker()

    @Singleton
    fun discover(operationRepository: SalesforceOperationRepository) = ShelbyDiscoverer(operationRepository)

    @Singleton
    fun getConfig(config: DestinationConfiguration) = config as ShelbyConfiguration

    @Singleton
    fun getAuthenticator(config: ShelbyConfiguration): OAuthAuthenticator {
        val authEndpoint: String = "https://${if (config.isSandbox) "test" else "login"}.salesforce.com/services/oauth2/token"
        return OAuthAuthenticator(authEndpoint, config.clientId, config.clientSecret, config.refreshToken)
    }

    @Singleton
    fun getBaseUrl(authenticator: OAuthAuthenticator) = authenticator.queryForAccessToken().get("instance_url").asText()

    @Singleton
    fun getHttpClient(authenticator: OAuthAuthenticator, baseUrl: String): HttpClient {
        val okhttpClient: OkHttpClient = OkHttpClient.Builder().addInterceptor(authenticator).build()
        return AirbyteOkHttpClient(okhttpClient, RetryPolicy.ofDefaults())
    }

    @Singleton
    fun getOperationRepository(httpClient: HttpClient, baseUrl: String): SalesforceOperationRepository {
        return SalesforceOperationRepository(httpClient, baseUrl)
    }

}
