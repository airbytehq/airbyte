package io.airbyte.cdk.load.http.authentication

import com.fasterxml.jackson.databind.JsonNode
import dev.failsafe.RetryPolicy
import io.airbyte.cdk.load.http.HttpClient
import io.airbyte.cdk.load.http.okhttp.AirbyteOkHttpClient
import io.micronaut.http.HttpHeaders
import okhttp3.Interceptor
import okhttp3.OkHttpClient
import okhttp3.Response as OkHttpResponse
import io.airbyte.cdk.load.http.Request
import io.airbyte.cdk.load.http.RequestMethod
import io.airbyte.cdk.load.http.Response
import io.airbyte.cdk.load.http.decoder.JsonDecoder

class OAuthAuthenticator(
    private val endpoint: String,
    private val clientId: String,
    private val clientSecret: String,
    private val refreshToken: String,
    private val httpClient: HttpClient = AirbyteOkHttpClient(OkHttpClient.Builder().build(), RetryPolicy.ofDefaults())
) :
    Interceptor {
    private val clientIdFieldName: String = "client_id"
    private val clientSecretFieldName: String = "client_secret"
    private val grantTypeFieldName: String = "grant_type"
    private val grantType: String = "refresh_token"
    private val refreshTokenFieldName: String = "refresh_token"

    private val decoder: JsonDecoder = JsonDecoder()
    private var accessToken: String? = null

    override fun intercept(chain: Interceptor.Chain): OkHttpResponse {
        if (needToQueryAccessToken()) {
            refreshAccessToken()
        }

        val requestWithAuthorization = chain.request().newBuilder()
            .addHeader(HttpHeaders.AUTHORIZATION, "Bearer $accessToken")
            .build()
        return chain.proceed(requestWithAuthorization)
    }

    private fun needToQueryAccessToken(): Boolean {
        return accessToken == null || isTokenExpired()
    }

    private fun isTokenExpired(): Boolean {
        return false // TODO as we only supports Salesforce today, the token is keep active until there is no activity for a while which should not happen in our context
    }

    /**
     * We make this available publicly because Salesforce needs the response from OAuth request in order to know which base URL to use for its next HTTP requests.
     */
    fun queryForAccessToken(): JsonNode {
        val requestBody: String = mapOf(
            grantTypeFieldName to grantType,
            clientIdFieldName to clientId,
            clientSecretFieldName to clientSecret,
            refreshTokenFieldName to refreshToken,
        ).map { (key, value) -> "$key=$value" }.joinToString(separator = "&") { it }
        val response: Response = httpClient.sendRequest(
            Request(
                method = RequestMethod.POST,
                url = endpoint,
                headers = mapOf("Content-Type" to "application/x-www-form-urlencoded"),
                body = requestBody.toByteArray(Charsets.UTF_8)
            )
        )
        return decoder.decode(response)
    }

    private fun refreshAccessToken() {
        accessToken = queryForAccessToken().get("access_token").asText()
    }
}
