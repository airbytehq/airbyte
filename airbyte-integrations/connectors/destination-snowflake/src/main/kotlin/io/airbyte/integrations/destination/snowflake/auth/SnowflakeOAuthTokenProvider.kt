/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.auth

import com.fasterxml.jackson.core.JsonProcessingException
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.TransientErrorException
import io.airbyte.cdk.util.Jsons
import java.io.IOException
import java.net.URI
import java.net.URLEncoder
import java.net.http.HttpClient
import java.net.http.HttpRequest
import java.net.http.HttpResponse
import java.nio.charset.StandardCharsets
import java.time.Duration
import java.util.Base64
import java.util.concurrent.TimeUnit

class SnowflakeOAuthTokenProvider(
    host: String,
    private val clientId: String,
    private val clientSecret: String,
    private val refreshToken: String,
    private val httpClient: HttpClient,
) {
    private val tokenRequestUri =
        URI.create("${host.toHttpsHost().trimEnd('/')}/oauth/token-request")

    private var accessToken: String? = null
    private var accessTokenExpiresAtMillis = 0L

    @Synchronized
    fun getAccessToken(): String {
        val now = System.currentTimeMillis()
        val cachedToken = accessToken
        if (
            cachedToken != null &&
                now < accessTokenExpiresAtMillis - TOKEN_EXPIRY_SAFETY_MARGIN_MILLIS
        ) {
            return cachedToken
        }

        val authorization =
            Base64.getEncoder()
                .encodeToString("$clientId:$clientSecret".toByteArray(StandardCharsets.UTF_8))
        val body =
            "grant_type=refresh_token&refresh_token=${URLEncoder.encode(refreshToken, StandardCharsets.UTF_8)}"
        val request =
            HttpRequest.newBuilder(tokenRequestUri)
                .timeout(Duration.ofSeconds(30))
                .header("Authorization", "Basic $authorization")
                .header("Accept", "application/json")
                .header("Content-Type", "application/x-www-form-urlencoded")
                .POST(HttpRequest.BodyPublishers.ofString(body))
                .build()

        val response =
            try {
                httpClient.send(request, HttpResponse.BodyHandlers.ofString())
            } catch (e: InterruptedException) {
                Thread.currentThread().interrupt()
                throw TransientErrorException("Snowflake OAuth token refresh was interrupted", e)
            } catch (e: IOException) {
                throw TransientErrorException("Snowflake OAuth token refresh failed", e)
            }

        if (response.statusCode() in setOf(400, 401, 403)) {
            throw ConfigErrorException(
                "Snowflake OAuth token refresh was rejected. Re-authenticate the destination."
            )
        }
        if (response.statusCode() !in 200..299) {
            throw TransientErrorException(
                "Snowflake OAuth token refresh returned HTTP ${response.statusCode()}."
            )
        }

        val responseJson =
            try {
                Jsons.readTree(response.body())
            } catch (e: JsonProcessingException) {
                throw TransientErrorException("Snowflake OAuth token response was invalid", e)
            }
        val refreshedToken = responseJson.path("access_token").asText(null)
        if (refreshedToken.isNullOrBlank()) {
            throw TransientErrorException(
                "Snowflake OAuth token response did not include an access token"
            )
        }
        val expiresInSeconds = responseJson.path("expires_in").asLong(DEFAULT_TOKEN_EXPIRY_SECONDS)
        accessToken = refreshedToken
        accessTokenExpiresAtMillis =
            System.currentTimeMillis() + TimeUnit.SECONDS.toMillis(expiresInSeconds)
        return refreshedToken
    }

    private fun String.toHttpsHost(): String =
        if (startsWith("http://", ignoreCase = true) || startsWith("https://", ignoreCase = true)) {
            this
        } else {
            "https://$this"
        }

    private companion object {
        const val DEFAULT_TOKEN_EXPIRY_SECONDS = 600L
        const val TOKEN_EXPIRY_SAFETY_MARGIN_MILLIS = 60_000L
    }
}
