/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery

import com.google.api.client.http.HttpHeaders
import com.google.api.client.http.HttpResponseException
import com.google.cloud.bigquery.BigQueryError
import com.google.cloud.bigquery.BigQueryException
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.output.ConfigError
import io.airbyte.cdk.output.DefaultExceptionClassifier
import io.airbyte.cdk.output.ExceptionHandler
import io.airbyte.cdk.output.TransientError
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

class BigqueryExceptionClassifierTest {
    private val classifier = BigqueryExceptionClassifier()

    @Test
    fun `classifies a BigQuery 503 as transient`() {
        val exception = BigQueryException(503, "Backend unavailable")

        assertEquals(
            TransientError(
                "BigQuery returned a temporary server error, which usually resolves on retry: Backend unavailable"
            ),
            classifier.classify(exception)
        )
    }

    @Test
    fun `classifies a wrapped BigQuery 503 as transient`() {
        val exception = BigQueryException(503, "Backend unavailable")

        assertEquals(
            TransientError(
                "BigQuery returned a temporary server error, which usually resolves on retry: Backend unavailable"
            ),
            classifier.classify(RuntimeException("Failed to load CSV...", exception))
        )
    }

    @Test
    fun `classifies a raw HTTP 503 as transient`() {
        val exception =
            HttpResponseException.Builder(503, "Service Unavailable", HttpHeaders()).build()

        assertTrue(classifier.classify(exception) is TransientError)
    }

    @Test
    fun `classifies a BigQuery backend error as transient`() {
        val exception = BigQueryException(listOf(BigQueryError("backendError", "US", "msg")))

        assertTrue(classifier.classify(exception) is TransientError)
    }

    @Test
    fun `does not classify a BigQuery 400`() {
        assertNull(classifier.classify(BigQueryException(400, "Invalid request")))
    }

    @Test
    fun `preserves an explicit config error classification`() {
        val exception =
            ConfigErrorException("billing", BigQueryException(503, "Backend unavailable"))

        assertNull(classifier.classify(exception))
        assertEquals(
            ConfigError("billing"),
            ExceptionHandler(listOf(DefaultExceptionClassifier(1), BigqueryExceptionClassifier()))
                .classify(exception)
        )
    }

    @Test
    fun `does not classify a generic runtime exception`() {
        assertNull(classifier.classify(RuntimeException("Unexpected error")))
    }
}
