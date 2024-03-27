/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.api.client

import com.fasterxml.jackson.databind.ObjectMapper
import io.airbyte.api.client.invoker.generated.ApiClient
import io.airbyte.api.client.invoker.generated.ApiException
import io.airbyte.api.client.invoker.generated.ApiResponse
import io.airbyte.api.client.model.generated.LogsRequestBody
import java.io.File
import java.io.IOException
import java.io.InputStream
import java.net.URI
import java.net.http.HttpClient
import java.net.http.HttpRequest
import java.net.http.HttpResponse
import java.time.Duration
import java.util.function.Consumer
import org.apache.commons.io.FileUtils

/**
 * This class is a copy of [io.airbyte.api.client.generated.LogsApi] except it allows Accept:
 * text/plain. Without this modification, [io.airbyte.api.client.generated.LogsApi] returns a 406
 * because the generated code requests the wrong response type.
 */
class PatchedLogsApi @JvmOverloads constructor(apiClient: ApiClient = ApiClient()) {
    private val memberVarHttpClient: HttpClient = apiClient.httpClient
    private val memberVarObjectMapper: ObjectMapper = apiClient.objectMapper
    private val memberVarBaseUri: String = apiClient.baseUri
    private val memberVarInterceptor: Consumer<HttpRequest.Builder>? = apiClient.requestInterceptor
    private val memberVarReadTimeout: Duration? = apiClient.readTimeout
    private val memberVarResponseInterceptor: Consumer<HttpResponse<InputStream?>>? =
        apiClient.responseInterceptor

    /**
     * Get logs
     *
     * @param logsRequestBody (required)
     * @return File
     * @throws ApiException if fails to make API call
     */
    @Throws(ApiException::class)
    fun getLogs(logsRequestBody: LogsRequestBody?): File {
        val localVarResponse = getLogsWithHttpInfo(logsRequestBody)
        return localVarResponse.data
    }

    /**
     * Get logs
     *
     * @param logsRequestBody (required)
     * @return ApiResponse&lt;File&gt;
     * @throws ApiException if fails to make API call
     */
    @Throws(ApiException::class)
    fun getLogsWithHttpInfo(logsRequestBody: LogsRequestBody?): ApiResponse<File> {
        val localVarRequestBuilder = getLogsRequestBuilder(logsRequestBody)
        try {
            val localVarResponse =
                memberVarHttpClient.send(
                    localVarRequestBuilder.build(),
                    HttpResponse.BodyHandlers.ofInputStream()
                )
            memberVarResponseInterceptor?.accept(localVarResponse)
            if (isErrorResponse(localVarResponse)) {
                throw ApiException(
                    localVarResponse.statusCode(),
                    "getLogs call received non-success response",
                    localVarResponse.headers(),
                    if (localVarResponse.body() == null) null
                    else String(localVarResponse.body()!!.readAllBytes())
                )
            }

            val tmpFile = File.createTempFile("patched-logs-api", "response") // CHANGED
            tmpFile.deleteOnExit() // CHANGED

            FileUtils.copyInputStreamToFile(localVarResponse.body(), tmpFile) // CHANGED

            return ApiResponse(
                localVarResponse.statusCode(),
                localVarResponse.headers().map(),
                tmpFile // CHANGED
            )
        } catch (e: IOException) {
            throw ApiException(e)
        } catch (e: InterruptedException) {
            Thread.currentThread().interrupt()
            throw ApiException(e)
        }
    }

    private fun isErrorResponse(httpResponse: HttpResponse<InputStream?>): Boolean {
        return httpResponse.statusCode() / 100 != 2
    }

    @Throws(ApiException::class)
    private fun getLogsRequestBuilder(logsRequestBody: LogsRequestBody?): HttpRequest.Builder {
        // verify the required parameter 'logsRequestBody' is set
        if (logsRequestBody == null) {
            throw ApiException(
                400,
                "Missing the required parameter 'logsRequestBody' when calling getLogs"
            )
        }

        val localVarRequestBuilder = HttpRequest.newBuilder()

        val localVarPath = "/v1/logs/get"

        localVarRequestBuilder.uri(URI.create(memberVarBaseUri + localVarPath))

        localVarRequestBuilder.header("Content-Type", "application/json")

        localVarRequestBuilder.header("Accept", "text/plain") // CHANGED

        try {
            val localVarPostBody = memberVarObjectMapper.writeValueAsBytes(logsRequestBody)
            localVarRequestBuilder.method(
                "POST",
                HttpRequest.BodyPublishers.ofByteArray(localVarPostBody)
            )
        } catch (e: IOException) {
            throw ApiException(e)
        }
        if (memberVarReadTimeout != null) {
            localVarRequestBuilder.timeout(memberVarReadTimeout)
        }
        memberVarInterceptor?.accept(localVarRequestBuilder)
        return localVarRequestBuilder
    }
}
