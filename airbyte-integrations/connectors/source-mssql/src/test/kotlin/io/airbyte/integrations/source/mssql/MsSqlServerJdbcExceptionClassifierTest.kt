/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mssql

import io.airbyte.cdk.output.JdbcExceptionClassifier
import io.airbyte.cdk.output.TransientError
import io.micronaut.context.env.Environment
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import java.sql.SQLException
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

@MicronautTest(environments = [Environment.TEST], rebuildContext = true)
class MsSqlServerJdbcExceptionClassifierTest {

    @Inject lateinit var classifier: JdbcExceptionClassifier

    @Test
    fun testAzureSqlReadReplicaRedoLagIsTransient() {
        Assertions.assertEquals(
            TransientError(
                "SQL Server Read Replica Error: Azure SQL read replica aborted the query.\n" +
                    "https://techcommunity.microsoft.com/blog/azuredbsupport/troubleshooting-intermittent-query-failures-on-azure-sql-db-read-replicas-error-/4499635"
            ),
            classifier.classify(
                SQLException(
                    "The service has encountered an error processing your request. Please try again. Error code 3947.",
                    "HY000",
                    3947,
                )
            ),
        )
    }
}
