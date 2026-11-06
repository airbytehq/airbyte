/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.bigquery

import com.google.cloud.bigquery.BigQueryException
import com.google.cloud.bigquery.exception.BigQueryJdbcException
import io.airbyte.cdk.output.ExceptionHandler
import io.airbyte.protocol.models.v0.AirbyteErrorTraceMessage.FailureType
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.ValueSource

/**
 * The exception classifier rules in `application.yml`, applied to the exception chain the JDBC
 * driver throws, with the BigQuery messages captured from the real service.
 */
@MicronautTest
class BigQueryExceptionClassifierTest {

    @Inject lateinit var handler: ExceptionHandler

    /** What `BigQueryStatement.runQuery` throws when the BigQuery job fails with [message]. */
    private fun runQueryFailure(message: String): BigQueryJdbcException =
        BigQueryJdbcException(
            "BigQueryException during runQuery\n$message",
            BigQueryException(400, message),
        )

    @ParameterizedTest
    @ValueSource(
        strings =
            [
                // A column dropped from the base table, referenced as table.column in the view.
                "Name status not found inside orders_daily; failed to parse view " +
                    "'my-project.my_dataset.my_view' at [1:30]",
                // The same, referenced by its bare name.
                "Unrecognized name: c; failed to parse view 'my-project.my_dataset.my_view' at [1:12]",
                // A base table column whose type changed under the view's expression.
                "No matching signature for operator + Argument types: STRING, INT64; " +
                    "failed to parse view 'my-project.my_dataset.my_view' at [1:8]",
            ],
    )
    fun invalidViewDefinitionIsAConfigError(message: String) {
        val trace = handler.handle(runQueryFailure(message))
        Assertions.assertEquals(FailureType.CONFIG_ERROR, trace.failureType)
        Assertions.assertEquals(
            "A selected BigQuery view has an invalid definition and cannot be queried. Fix or " +
                "recreate the view in BigQuery so it only references existing tables and " +
                "columns, or deselect its stream.",
            trace.message,
        )
        // The view BigQuery could not parse stays available to whoever investigates.
        Assertions.assertTrue(
            trace.internalMessage.contains("'my-project.my_dataset.my_view'"),
            trace.internalMessage,
        )
    }

    @Test
    fun invalidQueryOutsideAViewIsASystemError() {
        // An invalid query that is not in a view's definition is a bug in the connector's SQL.
        val message = "Unrecognized name: nope at [1:8]"
        val trace = handler.handle(runQueryFailure(message))
        Assertions.assertEquals(FailureType.SYSTEM_ERROR, trace.failureType)
        Assertions.assertTrue(trace.message.contains(message), trace.message)
    }
}
