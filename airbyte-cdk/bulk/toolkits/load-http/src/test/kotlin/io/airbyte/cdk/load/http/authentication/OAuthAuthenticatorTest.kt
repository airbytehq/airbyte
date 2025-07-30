/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.http.authentication

import io.airbyte.cdk.load.http.HttpClient
import io.airbyte.cdk.load.http.Response
import io.micronaut.http.HttpHeaders
import io.mockk.every
import io.mockk.mockk
import io.mockk.verify
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
