/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.http.okhttp

import io.airbyte.cdk.load.http.Response
import java.io.InputStream
import okhttp3.Response as OkhttpResponse

class OkHttpResponse(private val response: OkhttpResponse) : Response {

    override fun close() {
        response.close()
    }

    override val statusCode: Int
        get() = response.code
    override val headers: Map<String, List<String>>
        get() = response.headers.toMultimap()
    override val body: InputStream?
        get() = response.body?.byteStream()
}
