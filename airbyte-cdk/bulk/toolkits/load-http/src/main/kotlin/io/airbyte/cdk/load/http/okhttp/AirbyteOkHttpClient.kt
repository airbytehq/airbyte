package io.airbyte.cdk.load.http.okhttp

import dev.failsafe.RetryPolicy
import dev.failsafe.okhttp.FailsafeCall
import io.airbyte.cdk.load.http.HttpClient
import io.airbyte.cdk.load.http.Request
import io.airbyte.cdk.load.http.Response
import okhttp3.OkHttpClient
import okhttp3.RequestBody.Companion.toRequestBody

class AirbyteOkHttpClient(client: OkHttpClient, retryPolicy: RetryPolicy<okhttp3.Response>): HttpClient {
    private val client: OkHttpClient = client;
    private val policy = retryPolicy

    override fun sendRequest(request: Request): Response {
        val okhttpRequest: okhttp3.Request = okhttp3.Request.Builder().url(request.url).method(request.method.toString(), request.body?.toRequestBody()).build()
        val response: okhttp3.Response = FailsafeCall.with(policy).compose(client.newCall(okhttpRequest)).execute()
        return Response(response.code, response.headers.toMultimap(), response.body?.source())
    }
}
