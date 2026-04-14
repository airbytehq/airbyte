/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.doris.write

import io.airbyte.cdk.load.util.Jsons
import io.airbyte.integrations.destination.doris.spec.DorisConfiguration
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Named
import jakarta.inject.Singleton
import java.io.ByteArrayOutputStream
import java.io.IOException
import java.nio.charset.StandardCharsets
import java.util.zip.GZIPOutputStream
import org.apache.commons.codec.binary.Base64
import org.apache.http.HttpHeaders
import org.apache.http.client.methods.HttpPut
import org.apache.http.entity.ByteArrayEntity
import org.apache.http.entity.ContentType
import org.apache.http.impl.client.CloseableHttpClient
import org.apache.http.util.EntityUtils

private val log = KotlinLogging.logger {}

@Singleton
class DorisStreamLoadClient(
    private val config: DorisConfiguration,
    @Named("dorisHttpClient") private val httpClient: CloseableHttpClient,
) {
    private val maxRetries = 3
    private val authHeader: String

    init {
        val authInfo = "${config.username}:${config.password}"
        val encoded = Base64.encodeBase64(authInfo.toByteArray(StandardCharsets.UTF_8))
        authHeader = "Basic " + String(encoded)
    }

    /**
     * Execute a Stream Load to write data into Doris.
     *
     * @param database Target database
     * @param table Target table name (without namespace)
     * @param data JSON lines data to load
     */
    fun streamLoad(database: String, table: String, data: ByteArray) {
        if (data.isEmpty()) {
            log.debug { "Skipping empty stream load for $database.$table" }
            return
        }

        val label = DorisLabelGenerator.generateLabel(table)
        var currentLabel = label
        var retry = 0

        while (retry <= maxRetries) {
            try {
                val body = if (config.enableGzip) gzip(data) else data
                val url = "${config.feHttpUrl}/api/$database/$table/_stream_load"

                val httpPut = HttpPut(url)
                httpPut.setHeader(HttpHeaders.EXPECT, "100-continue")
                httpPut.setHeader(HttpHeaders.AUTHORIZATION, authHeader)
                httpPut.setHeader("label", currentLabel)
                httpPut.setHeader("format", "json")
                httpPut.setHeader("read_json_by_line", "true")

                if (config.enableGzip) {
                    httpPut.setHeader("compress_type", "gz")
                }

                httpPut.entity = ByteArrayEntity(body, ContentType.APPLICATION_JSON)

                httpClient.execute(httpPut).use { response ->
                    val statusCode = response.statusLine.statusCode
                    val responseBody = EntityUtils.toString(response.entity) ?: ""

                    if (statusCode == 200) {
                        val loadResponse: DorisStreamLoadResponse =
                            Jsons.readValue(responseBody, DorisStreamLoadResponse::class.java)

                        if (loadResponse.isSuccess()) {
                            log.info {
                                "Stream load success: label=$currentLabel, " +
                                    "loaded=${loadResponse.numberLoadedRows}, " +
                                    "bytes=${loadResponse.loadBytes}, " +
                                    "time=${loadResponse.loadTimeMs}ms"
                            }
                            return
                        }

                        if (loadResponse.isLabelAlreadyExistsAndSuccess()) {
                            log.info {
                                "Label $currentLabel already exists with FINISHED status, treating as success"
                            }
                            return
                        }

                        // Fetch error details from errorUrl
                        var errorDetail = ""
                        if (loadResponse.errorUrl != null) {
                            try {
                                val errorGet =
                                    org.apache.http.client.methods.HttpGet(loadResponse.errorUrl)
                                httpClient.execute(errorGet).use { errorResp ->
                                    errorDetail = EntityUtils.toString(errorResp.entity) ?: ""
                                }
                            } catch (_: Exception) {}
                        }

                        log.error {
                            "Stream load failed: label=$currentLabel, " +
                                "status=${loadResponse.status}, " +
                                "message=${loadResponse.message}, " +
                                "errorUrl=${loadResponse.errorUrl}, " +
                                "errorDetail=$errorDetail"
                        }
                    } else {
                        log.error { "Stream load HTTP error: code=$statusCode, body=$responseBody" }
                    }
                }
            } catch (e: IOException) {
                log.error(e) {
                    "Stream load IO error: label=$currentLabel, retry=$retry/$maxRetries"
                }
            }

            if (retry < maxRetries) {
                retry++
                currentLabel = DorisLabelGenerator.retryLabel(label, retry)
                val sleepMs = retry * 1000L
                log.info {
                    "Retrying stream load: label=$currentLabel, retry=$retry, sleeping ${sleepMs}ms"
                }
                Thread.sleep(sleepMs)
            } else {
                throw DorisStreamLoadException(
                    "Stream load failed after $maxRetries retries for $database.$table"
                )
            }
        }
    }

    private fun gzip(data: ByteArray): ByteArray {
        val bos = ByteArrayOutputStream()
        GZIPOutputStream(bos).use { it.write(data) }
        return bos.toByteArray()
    }
}

class DorisStreamLoadException(message: String, cause: Throwable? = null) :
    RuntimeException(message, cause)
