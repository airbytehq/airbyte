/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.auth

import com.sun.net.httpserver.HttpExchange
import com.sun.net.httpserver.HttpServer
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.TransientErrorException
import java.net.InetSocketAddress
import java.net.URI
import java.net.http.HttpClient
import java.nio.charset.StandardCharsets
import java.util.Base64
import java.util.concurrent.atomic.AtomicInteger
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.ValueSource

internal class SnowflakeOAuthTokenProviderTest {

    @Test
    fun testRefreshRequestAndTokenCaching() {
        withTokenServer(
            response = { _, _ ->
                TokenResponse(200, """{"access_token":"test-access-token","expires_in":600}""")
            },
            block = { serverUri, requests ->
                val provider =
                    provider(
                        serverUri,
                        clientId = "test-client-id",
                        clientSecret = "test-client-secret",
                        refreshToken = "refresh token/value",
                    )

                assertEquals("test-access-token", provider.getAccessToken())
                assertEquals("test-access-token", provider.getAccessToken())
                assertEquals(1, requests.size)
                assertEquals(
                    "grant_type=refresh_token&refresh_token=refresh+token%2Fvalue",
                    requests.single().body,
                )
                assertEquals(
                    "Basic " +
                        Base64.getEncoder()
                            .encodeToString("test-client-id:test-client-secret".toByteArray()),
                    requests.single().authorization,
                )
            },
        )
    }

    @Test
    fun testNearExpiryTokenIsRefreshed() {
        withTokenServer(
            response = { requestNumber, _ ->
                if (requestNumber == 1) {
                    TokenResponse(200, """{"access_token":"first-token","expires_in":1}""")
                } else {
                    TokenResponse(200, """{"access_token":"second-token","expires_in":600}""")
                }
            },
            block = { serverUri, requests ->
                val provider = provider(serverUri)

                assertEquals("first-token", provider.getAccessToken())
                assertEquals("second-token", provider.getAccessToken())
                assertEquals(2, requests.size)
            },
        )
    }

    @ParameterizedTest
    @ValueSource(ints = [400, 401])
    fun testRejectedRefreshTokenThrowsConfigError(statusCode: Int) {
        withTokenServer(
            response = { _, _ -> TokenResponse(statusCode, "{}") },
            block = { serverUri, _ ->
                assertThrows<ConfigErrorException> { provider(serverUri).getAccessToken() }
            },
        )
    }

    @Test
    fun testServerErrorThrowsTransientError() {
        withTokenServer(
            response = { _, _ -> TokenResponse(500, "{}") },
            block = { serverUri, _ ->
                assertThrows<TransientErrorException> { provider(serverUri).getAccessToken() }
            },
        )
    }

    @Test
    fun testMissingAccessTokenThrowsTransientError() {
        withTokenServer(
            response = { _, _ -> TokenResponse(200, """{"expires_in":600}""") },
            block = { serverUri, _ ->
                assertThrows<TransientErrorException> { provider(serverUri).getAccessToken() }
            },
        )
    }

    private fun provider(
        serverUri: URI,
        clientId: String = "test-client-id",
        clientSecret: String = "test-client-secret",
        refreshToken: String = "test-refresh-token",
    ) =
        SnowflakeOAuthTokenProvider(
            host = serverUri.toString(),
            clientId = clientId,
            clientSecret = clientSecret,
            refreshToken = refreshToken,
            httpClient = HttpClient.newHttpClient(),
        )

    private fun <T> withTokenServer(
        response: (requestNumber: Int, request: RecordedRequest) -> TokenResponse,
        block: (serverUri: URI, requests: List<RecordedRequest>) -> T,
    ): T {
        val server = HttpServer.create(InetSocketAddress("localhost", 0), 0)
        val requestNumber = AtomicInteger()
        val requests = mutableListOf<RecordedRequest>()
        server.createContext("/oauth/token-request") { exchange ->
            val recordedRequest =
                RecordedRequest(
                    body = exchange.requestBody.readBytes().toString(StandardCharsets.UTF_8),
                    authorization = exchange.requestHeaders.getFirst("Authorization"),
                )
            requests.add(recordedRequest)
            val tokenResponse = response(requestNumber.incrementAndGet(), recordedRequest)
            writeResponse(exchange, tokenResponse)
        }
        server.start()
        return try {
            block(URI.create("http://localhost:${server.address.port}"), requests)
        } finally {
            server.stop(0)
        }
    }

    private fun writeResponse(exchange: HttpExchange, response: TokenResponse) {
        val body = response.body.toByteArray(StandardCharsets.UTF_8)
        exchange.sendResponseHeaders(response.statusCode, body.size.toLong())
        exchange.responseBody.use { it.write(body) }
    }

    private data class TokenResponse(val statusCode: Int, val body: String)

    private data class RecordedRequest(val body: String, val authorization: String?)
}
