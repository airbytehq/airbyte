/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.http.authentication

import com.fasterxml.jackson.databind.JsonNode
import dev.failsafe.RetryPolicy
import io.airbyte.cdk.load.http.HttpClient
import io.airbyte.cdk.load.http.Request
import io.airbyte.cdk.load.http.RequestMethod
import io.airbyte.cdk.load.http.Response
import io.airbyte.cdk.load.http.consumeBodyToString
import io.airbyte.cdk.load.http.decoder.JsonDecoder
import io.airbyte.cdk.load.http.okhttp.AirbyteOkHttpClient
import io.micronaut.http.HttpHeaders
import java.lang.IllegalStateException
import okhttp3.Interceptor
import okhttp3.OkHttpClient
import okhttp3.Response as OkHttpResponse

class OAuthAuthenticator(
    private val endpoint: String,
    private val clientId: String,
    private val clientSecret: String,
    private val refreshToken: String,
    private val httpClient: HttpClient =
        AirbyteOkHttpClient(OkHttpClient.Builder().build(), RetryPolicy.ofDefaults())
) : Interceptor {
    object Constants {
        const val CLIENT_ID_FIELD_NAME: String = "client_id"
        const val CLIENT_SECRET_FIELD_NAME: String = "client_secret"
        const val GRANT_TYPE_FIELD_NAME: String = "grant_type"
        const val GRANT_TYPE: String = "refresh_token"
        const val REFRESH_TOKEN_FIELD_NAME: String = "refresh_token"
    }

    private val decoder: JsonDecoder = JsonDecoder()
    private var accessToken: String? = null

    override fun intercept(chain: Interceptor.Chain): OkHttpResponse {
        if (needToQueryAccessToken()) {
            refreshAccessToken()
        }

        val requestWithAuthorization =
            chain
                .request()
                .newBuilder()
                .addHeader(HttpHeaders.AUTHORIZATION, "Bearer $accessToken")
                .build()
        return chain.proceed(requestWithAuthorization)
    }

    private fun needToQueryAccessToken(): Boolean {
        return accessToken == null || isTokenExpired()
    }

    private fun isTokenExpired(): Boolean {
        return false // TODO as we only supports Salesforce today, the token is keep active until
        // there is no activity for a while which should not happen in our context
    }

    /**
     * We make this available publicly because Salesforce needs the response from OAuth request in
     * order to know which base URL to use for its next HTTP requests.
     */
    fun queryForAccessToken(): JsonNode {
        val requestBody: String =
            mapOf(
                    Constants.GRANT_TYPE_FIELD_NAME to Constants.GRANT_TYPE,
                    Constants.CLIENT_ID_FIELD_NAME to clientId,
                    Constants.CLIENT_SECRET_FIELD_NAME to clientSecret,
                    Constants.REFRESH_TOKEN_FIELD_NAME to refreshToken,
                )
                .map { (key, value) -> "$key=$value" }
                .joinToString(separator = "&") { it }
        val response: Response =
            httpClient.send(
                Request(
                    method = RequestMethod.POST,
                    url = endpoint,
                    headers = mapOf("Content-Type" to "application/x-www-form-urlencoded"),
                    body = requestBody.toByteArray(Charsets.UTF_8)
                )
            )
        if (response.statusCode !in 200..299) {
            throw kotlin.IllegalStateException(
                "Could not log in. Response from server is ${response.statusCode}: ${response.consumeBodyToString()}"
            )
        }
        return response.use { it.body?.let { body -> decoder.decode(body) } }
            ?: throw IllegalStateException("Response body was expected but is empty")
    }

    private fun refreshAccessToken() {
        accessToken = queryForAccessToken().get("access_token").asText()
    }
}
