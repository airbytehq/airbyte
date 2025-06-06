package io.airbyte.cdk.load.http

import okhttp3.RequestBody.Companion.toRequestBody

interface HttpClient {
  fun sendRequest(request: Request): Response
}
