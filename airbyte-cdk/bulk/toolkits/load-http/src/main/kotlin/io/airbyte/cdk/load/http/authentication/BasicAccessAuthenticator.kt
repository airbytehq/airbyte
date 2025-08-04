/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.http.authentication

import okhttp3.Credentials
import okhttp3.Interceptor
import okhttp3.Response as OkHttpResponse

class BasicAccessAuthenticator(
    private val username: String,
    private val password: String,
) : Interceptor {

    override fun intercept(chain: Interceptor.Chain): OkHttpResponse {
        val requestWithAuthorization =
            chain
                .request()
                .newBuilder()
                .header("Authorization", Credentials.basic(username, password))
                .build()
        return chain.proceed(requestWithAuthorization)
    }
}
