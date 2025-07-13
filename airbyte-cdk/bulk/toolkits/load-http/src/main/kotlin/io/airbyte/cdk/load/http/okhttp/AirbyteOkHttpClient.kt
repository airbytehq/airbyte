/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.http.okhttp

import dev.failsafe.RetryPolicy
import dev.failsafe.okhttp.FailsafeCall
import io.airbyte.cdk.load.http.HttpClient
import io.airbyte.cdk.load.http.Request
import io.airbyte.cdk.load.http.Response
import okhttp3.HttpUrl
import okhttp3.HttpUrl.Companion.toHttpUrlOrNull
import okhttp3.OkHttpClient
import okhttp3.RequestBody.Companion.toRequestBody

class AirbyteOkHttpClient(
    private val client: OkHttpClient,
    private val retryPolicy: RetryPolicy<okhttp3.Response>
) : HttpClient {

    override fun send(request: Request): Response {
        val url = createUrl(request)

        val okhttpRequest: okhttp3.Request =
            okhttp3.Request.Builder()
                .url(url)
                .method(request.method.toString(), request.body?.toRequestBody())
                .apply { request.headers.forEach { header -> addHeader(header.key, header.value) } }
                .build()
        val response: okhttp3.Response =
            FailsafeCall.with(retryPolicy).compose(client.newCall(okhttpRequest)).execute()
        return OkHttpResponse(response)
    }

    private fun createUrl(request: Request): HttpUrl {
        val urlBuilder =
            request.url.toHttpUrlOrNull()?.let { it.newBuilder() }
                ?: throw IllegalStateException("Request URL ${request.url} is invalid.")
        return urlBuilder
            .apply {
                request.query.forEach { query ->
                    query.value.forEach { queryValue -> addQueryParameter(query.key, queryValue) }
                }
            }
            .build()
    }
}
