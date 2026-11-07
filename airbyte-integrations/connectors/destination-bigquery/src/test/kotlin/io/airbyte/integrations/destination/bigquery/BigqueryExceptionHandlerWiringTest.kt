/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery

import com.google.cloud.bigquery.BigQueryException
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.output.ConfigError
import io.airbyte.cdk.output.DefaultExceptionClassifier
import io.airbyte.cdk.output.ExceptionHandler
import io.airbyte.cdk.output.TransientError
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

@MicronautTest
class BigqueryExceptionHandlerWiringTest {

    @Inject lateinit var handler: ExceptionHandler

    @Test
    fun `injected handler runs the BigQuery classifier after the default one`() {
        val types = handler.classifiers.map { it::class }
        val defaultIndex = types.indexOf(DefaultExceptionClassifier::class)
        val bigqueryIndex = types.indexOf(BigqueryExceptionClassifier::class)

        assertTrue(defaultIndex >= 0, "DefaultExceptionClassifier not injected: $types")
        assertTrue(bigqueryIndex > defaultIndex, "unexpected classifier order: $types")
    }

    @Test
    fun `injected handler classifies a wrapped BigQuery 503 as transient`() {
        val e = RuntimeException("Failed to load CSV data", BigQueryException(503, "unavailable"))

        assertTrue(handler.classify(e) is TransientError)
    }

    @Test
    fun `injected handler keeps an explicit config error`() {
        val e = ConfigErrorException("billing", BigQueryException(503, "unavailable"))

        assertEquals(ConfigError("billing"), handler.classify(e))
    }
}
