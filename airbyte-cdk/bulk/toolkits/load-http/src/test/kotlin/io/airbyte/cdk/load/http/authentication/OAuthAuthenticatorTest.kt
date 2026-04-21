/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.http.authentication

import io.airbyte.cdk.load.http.HttpClient
import io.airbyte.cdk.load.http.Response
import io.micronaut.http.HttpHeaders
import io.mockk.every
import io.mockk.mockk
import io.mockk.verify
import java.time.Clock
import java.time.Instant
import java.time.ZoneId
import kotlin.test.assertFailsWith
import okhttp3.Interceptor
import okhttp3.Request
import okhttp3.Response as OkHttpResponse
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

const val AN_ACCESS_TOKEN = "an_access_token"
const val A_CLIENT_ID = "a_client_id"
const val A_CLIENT_SECRET = "a_client_secret"
const val A_ENDPOINT = "https://a-endpoint.com"
const val A_REFRESH_TOKEN = "a_refresh_token"

class OAuthAuthenticatorTest {

    private lateinit var authenticator: OAuthAuthenticator
    private val httpClient: HttpClient = mockk()

    @BeforeEach
    fun setup() {
        authenticator =
            OAuthAuthenticator(
                A_ENDPOINT,
                A_CLIENT_ID,
                A_CLIENT_SECRET,
                A_REFRESH_TOKEN,
                httpClient
            )
    }

    @Test
    internal fun `test when performing a request then perform oauth authentication`() {
        val originalRequest: Request = mockk()
        val chain: Interceptor.Chain = mockChain(originalRequest)
        val builder: Request.Builder = mockBuilder(originalRequest)
        mockCall()

        authenticator.intercept(chain)

        verify(exactly = 1) {
            builder.addHeader(HttpHeaders.AUTHORIZATION, "Bearer an_access_token")
        }
    }

    @Test
    internal fun `test given access token already fetched when performing a request then do not query again`() {
        val originalRequest: Request = mockk()
        val chain: Interceptor.Chain = mockChain(originalRequest)
        mockBuilder(originalRequest)
        mockCall()

        authenticator.intercept(chain)
        authenticator.intercept(chain)

        verify(exactly = 1) { httpClient.send(any()) }
    }

    @Test
    internal fun `test given token with expires_in when token expires then refresh token`() {
        val fixedInstant = Instant.parse("2026-01-01T00:00:00Z")
        val clock = Clock.fixed(fixedInstant, ZoneId.of("UTC"))
        val authWithClock =
            OAuthAuthenticator(
                A_ENDPOINT,
                A_CLIENT_ID,
                A_CLIENT_SECRET,
                A_REFRESH_TOKEN,
                httpClient,
                clock
            )

        val originalRequest: Request = mockk()
        val chain: Interceptor.Chain = mockChain(originalRequest)
        mockBuilder(originalRequest)
        mockCallWithExpiresIn(1800) // 30 minutes

        // First call fetches the token
        authWithClock.intercept(chain)
        verify(exactly = 1) { httpClient.send(any()) }

        // Second call within expiry window should not refresh
        authWithClock.intercept(chain)
        verify(exactly = 1) { httpClient.send(any()) }
    }

    @Test
    internal fun `test given expired token when performing a request then refresh token`() {
        val startInstant = Instant.parse("2026-01-01T00:00:00Z")
        // Token expires in 1800s (30 min), buffer is 60s, so expired at startInstant + 1740s
        val expiredInstant = startInstant.plusSeconds(1800)
        val mutableClock = mockk<Clock>()
        every { mutableClock.instant() } returns startInstant
        every { mutableClock.zone } returns ZoneId.of("UTC")

        val authWithClock =
            OAuthAuthenticator(
                A_ENDPOINT,
                A_CLIENT_ID,
                A_CLIENT_SECRET,
                A_REFRESH_TOKEN,
                httpClient,
                mutableClock
            )

        val originalRequest: Request = mockk()
        val chain: Interceptor.Chain = mockChain(originalRequest)
        mockBuilder(originalRequest)
        mockCallWithExpiresIn(1800)

        // First call fetches the token
        authWithClock.intercept(chain)
        verify(exactly = 1) { httpClient.send(any()) }

        // Advance time past expiry
        every { mutableClock.instant() } returns expiredInstant

        // Second call should refresh because token is expired
        authWithClock.intercept(chain)
        verify(exactly = 2) { httpClient.send(any()) }
    }

    @Test
    internal fun `test given no expires_in in response when performing requests then do not refresh`() {
        val originalRequest: Request = mockk()
        val chain: Interceptor.Chain = mockChain(originalRequest)
        mockBuilder(originalRequest)
        mockCall() // no expires_in in response

        authenticator.intercept(chain)
        authenticator.intercept(chain)

        // Without expires_in, token is never considered expired (backward compatible)
        verify(exactly = 1) { httpClient.send(any()) }
    }

    @Test
    internal fun `test given status is not 2XX when performing a request then raise`() {
        val originalRequest: Request = mockk()
        val chain: Interceptor.Chain = mockChain(originalRequest)
        mockBuilder(originalRequest)
        val oauthResponse: Response = mockk<Response>()
        every { oauthResponse.statusCode } returns 400
        every { oauthResponse.body } returns
            "{\"error_message\":\"failed\"}".byteInputStream(Charsets.UTF_8)
        every { oauthResponse.close() } returns Unit
        every { httpClient.send(any()) } returns (oauthResponse)

        assertFailsWith<IllegalStateException>(block = { authenticator.intercept(chain) })
    }

    private fun mockCall() {
        val oauthResponse: Response = mockk<Response>()
        every { oauthResponse.statusCode } returns 200
        every { oauthResponse.body } returns
            "{\"access_token\":\"${AN_ACCESS_TOKEN}\"}".byteInputStream(Charsets.UTF_8)
        every { oauthResponse.close() } returns Unit
        every { httpClient.send(any()) } returns (oauthResponse)
    }

    private fun mockCallWithExpiresIn(expiresIn: Int) {
        every { httpClient.send(any()) } answers
            {
                val oauthResponse: Response = mockk<Response>()
                every { oauthResponse.statusCode } returns 200
                every { oauthResponse.body } returns
                    "{\"access_token\":\"${AN_ACCESS_TOKEN}\",\"expires_in\":$expiresIn}".byteInputStream(
                        Charsets.UTF_8
                    )
                every { oauthResponse.close() } returns Unit
                oauthResponse
            }
    }

    private fun mockBuilder(originalRequest: Request): Request.Builder {
        val builder: Request.Builder = mockk()
        every { builder.addHeader(any(), any()) } returns (builder)
        every { builder.build() } returns (mockk<Request>())
        every { originalRequest.newBuilder() } returns (builder)
        return builder
    }

    private fun mockChain(request: Request): Interceptor.Chain {
        val chain: Interceptor.Chain = mockk()
        every { chain.request() } returns (request)
        every { chain.proceed(any()) } returns (mockk<OkHttpResponse>())

        return chain
    }
}
