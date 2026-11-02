/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.starrocks.http

import com.fasterxml.jackson.databind.ObjectMapper
import okhttp3.Credentials
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody

/**
 * Parsed StarRocks Stream Load response. Note: the BE returns HTTP 200 even on a logical load
 * failure, so success is determined by the JSON [status] field, not the HTTP code.
 */
data class StreamLoadResponse(
    val status: String,
    val message: String?,
    val loadedRows: Long,
    val filteredRows: Long,
    val label: String?,
    val errorUrl: String?,
    val raw: String,
) {
    /** `Publish Timeout` = committed but not yet visible; per StarRocks docs, do NOT retry. */
    val isSuccess: Boolean
        get() = status == STATUS_SUCCESS || status == STATUS_PUBLISH_TIMEOUT

    val labelAlreadyExists: Boolean
        get() = status == STATUS_LABEL_EXISTS

    companion object {
        const val STATUS_SUCCESS = "Success"
        const val STATUS_PUBLISH_TIMEOUT = "Publish Timeout"
        const val STATUS_LABEL_EXISTS = "Label Already Exists"
    }
}

/**
 * StarRocks Stream Load HTTP client.
 *
 * The FE (`http_port`, default 8030) answers `/api/{db}/{table}/_stream_load` with a **307** to a
 * BE/CN node on a different host:port. OkHttp (a) will not auto-follow a 307 on a PUT and (b)
 * strips `Authorization` on a cross-host redirect — so we disable auto-follow and follow the
 * `Location` manually, re-attaching the `Authorization` header on every hop. This is `curl
 * --location-trusted`.
 *
 * StarRocks' `http_port` is plain HTTP even on TLS-enabled clusters (`ssl` is for the JDBC control
 * plane only), so this client always speaks HTTP.
 */
class StreamLoadClient(
    private val host: String,
    private val httpPort: Int,
    username: String,
    password: String,
    // `Expect: 100-continue` lets the FE answer 307 without receiving the body (so the body is only
    // ever sent to the BE). Disabled in unit tests because MockWebServer doesn't do the 100
    // handshake.
    private val expectContinue: Boolean = true,
    private val client: OkHttpClient =
        OkHttpClient.Builder().followRedirects(false).followSslRedirects(false).build(),
) {
    private val authHeader = Credentials.basic(username, password)
    private val mapper = ObjectMapper()

    fun streamLoad(
        database: String,
        table: String,
        label: String,
        headers: Map<String, String>,
        body: ByteArray,
    ): StreamLoadResponse {
        // StarRocks serves Stream Load on the FE HTTP port, which is plain HTTP (no TLS variant).
        val streamLoadUrl =
            "http://$host:$httpPort/api/$database/$table/_stream_load" // # ignore-https-check
        var request = buildRequest(streamLoadUrl, label, headers, body)
        var redirects = 0
        var response = client.newCall(request).execute()
        try {
            while (response.isRedirect && redirects++ < MAX_REDIRECTS) {
                val location =
                    response.header("Location")
                        ?: error(
                            "Stream Load redirect (${response.code}) missing a Location header"
                        )
                response.close()
                request = buildRequest(location, label, headers, body)
                response = client.newCall(request).execute()
            }
            val text = response.body?.string().orEmpty()
            require(response.code in 200..299) {
                "Stream Load HTTP ${response.code} from ${response.request.url}: $text"
            }
            val json = mapper.readTree(text)
            return StreamLoadResponse(
                status = json.path("Status").asText(""),
                message = json.path("Message").asText(null),
                loadedRows = json.path("NumberLoadedRows").asLong(0),
                filteredRows = json.path("NumberFilteredRows").asLong(0),
                label = json.path("Label").asText(null),
                errorUrl = json.path("ErrorURL").asText(null),
                raw = text,
            )
        } finally {
            response.close()
        }
    }

    private fun buildRequest(
        url: String,
        label: String,
        headers: Map<String, String>,
        body: ByteArray,
    ): Request =
        Request.Builder()
            .url(url)
            .put(body.toRequestBody())
            .header("Authorization", authHeader) // re-attached on every hop (FE and BE/CN)
            .header("label", label)
            .apply {
                if (expectContinue) header("Expect", "100-continue")
                headers.forEach { (k, v) -> header(k, v) }
            }
            .build()

    companion object {
        private const val MAX_REDIRECTS = 5
    }
}
