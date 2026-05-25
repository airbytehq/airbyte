/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mssql

import io.airbyte.cdk.output.JdbcExceptionClassifier
import io.airbyte.cdk.output.TransientError
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import java.sql.SQLException
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

@MicronautTest
class MsSqlServerExceptionClassifierTest {

    @Inject lateinit var classifier: JdbcExceptionClassifier

    @Test
    fun testAzureSqlReadReplicaAbortIsTransient() {
        val exception =
            SQLException(
                "The service has encountered an error processing your request. Please try again. Error code 3947.",
                "HY000",
                3947,
            )

        Assertions.assertEquals(
            TransientError("Azure SQL read replica aborted the query."),
            classifier.classify(exception),
        )
    }
}
