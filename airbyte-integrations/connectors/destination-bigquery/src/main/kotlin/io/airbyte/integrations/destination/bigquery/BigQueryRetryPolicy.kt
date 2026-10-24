/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery

import com.google.api.client.http.HttpResponseException
import com.google.api.gax.retrying.RetrySettings
import com.google.cloud.BaseService
import com.google.cloud.ExceptionHandler
import com.google.cloud.ExceptionHandler.Interceptor.RetryResult
import java.net.ConnectException
import java.net.SocketException
import java.net.UnknownHostException
import java.time.Duration

object BigQueryRetryPolicy {
    val RETRYABLE_HTTP_STATUS_CODES = setOf(500, 502, 503, 504)

    val retrySettings: RetrySettings =
        RetrySettings.newBuilder()
            .setInitialRetryDelayDuration(Duration.ofMillis(1000L))
            .setMaxRetryDelayDuration(Duration.ofMillis(32_000L))
            .setTotalTimeoutDuration(Duration.ofMillis(60_000L))
            .setInitialRpcTimeoutDuration(Duration.ofMillis(50_000L))
            .setRpcTimeoutMultiplier(1.0)
            .setMaxRpcTimeoutDuration(Duration.ofMillis(50_000L))
            .setMaxAttempts(15)
            .setRetryDelayMultiplier(1.5)
            .build()

    object RetryableHttpStatusInterceptor : ExceptionHandler.Interceptor {
        override fun beforeEval(exception: Exception): RetryResult =
            if (
                exception is HttpResponseException &&
                    exception.statusCode in RETRYABLE_HTTP_STATUS_CODES
            ) {
                RetryResult.RETRY
            } else {
                RetryResult.CONTINUE_EVALUATION
            }

        override fun afterEval(
            exception: Exception,
            retryResult: RetryResult,
        ): RetryResult = RetryResult.CONTINUE_EVALUATION

        private fun readResolve(): Any = RetryableHttpStatusInterceptor
    }

    val resultRetryAlgorithm: ExceptionHandler =
        ExceptionHandler.newBuilder()
            .abortOn(RuntimeException::class.java)
            .retryOn(ConnectException::class.java)
            .retryOn(UnknownHostException::class.java)
            .retryOn(SocketException::class.java)
            .addInterceptors(
                RetryableHttpStatusInterceptor,
                BaseService.EXCEPTION_HANDLER_INTERCEPTOR,
            )
            .build()
}
