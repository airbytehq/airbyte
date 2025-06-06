package io.airbyte.cdk.load.http.authentication

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.util.Jsons
import io.micronaut.http.HttpHeaders
import okhttp3.*

class OAuthAuthenticator(endpoint: String, clientId: String, clientSecret: String, refreshToken: String, httpClient: OkHttpClient = OkHttpClient.Builder().build()) : Interceptor {
    private val httpClient: OkHttpClient = httpClient  // TODO: discuss about if we want to add an abstraction for HttpClient like we have [here](https://github.com/airbytehq/airbyte-python-cdk/blob/155cdc8c99f73df15b57ab1a7e4c9761c4dc5cac/airbyte_cdk/sources/streams/http/http_client.py#L76)

    private val endpoint: String = endpoint
    private val clientIdFieldName: String = "client_id"
    private val clientId: String = clientId
    private val clientSecretFieldName: String = "client_secret"
    private val clientSecret: String = clientSecret
    private val grantTypeFieldName: String = "grant_type"
    private val grantType: String = "refresh_token"
    private val refreshTokenFieldName: String = "refresh_token"
    private val refreshToken: String = refreshToken

    private var accessToken: String? = null

    override fun intercept(chain: Interceptor.Chain): Response {
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
        val formBody: RequestBody = FormBody.Builder()
            .add(grantTypeFieldName, grantType)
            .add(clientIdFieldName, clientId)
            .add(clientSecretFieldName, clientSecret)
            .add(refreshTokenFieldName, refreshToken)
            .build()
        val request: Request = Request.Builder()
            .url(endpoint)
            .method("POST", formBody)
            .build();
        val response: Response = httpClient.newCall(request).execute()
        return Jsons.readTree(response.body!!.bytes())
    }

    private fun refreshAccessToken() {
        accessToken = queryForAccessToken().get("access_token").asText()
    }
}
