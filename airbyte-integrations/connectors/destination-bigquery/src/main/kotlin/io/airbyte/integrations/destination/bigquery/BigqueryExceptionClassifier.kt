/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery

import com.google.api.client.http.HttpResponseException
import com.google.cloud.bigquery.BigQueryException
import io.airbyte.cdk.ConnectorErrorException
import io.airbyte.cdk.output.ConnectorError
import io.airbyte.cdk.output.ExceptionClassifier
import io.airbyte.cdk.output.TransientError
import jakarta.inject.Singleton

@Singleton
class BigqueryExceptionClassifier : ExceptionClassifier {
    override val orderValue = 2

    override fun classify(e: Throwable): ConnectorError? {
        val match =
            ExceptionClassifier.unwind(e) { it is ConnectorErrorException || isTransient(it) }
                ?: return null
        if (match is ConnectorErrorException) {
            return null
        }
        return TransientError(
            "BigQuery returned a temporary server error, which usually resolves on retry: ${match.message}"
        )
    }

    private fun isTransient(t: Throwable): Boolean =
        when (t) {
            is BigQueryException ->
                t.code in BigQueryRetryPolicy.RETRYABLE_HTTP_STATUS_CODES ||
                    t.errors.orEmpty().any { it.reason in TRANSIENT_REASONS } ||
                    t.reason in TRANSIENT_REASONS
            is HttpResponseException ->
                t.statusCode in BigQueryRetryPolicy.RETRYABLE_HTTP_STATUS_CODES
            else -> false
        }

    private companion object {
        val TRANSIENT_REASONS = setOf("backendError", "internalError")
    }
}
