/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mssql

import io.airbyte.cdk.output.ConfigError
import io.airbyte.cdk.output.JdbcExceptionClassifier
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
    fun `classifies SQL Server permission denied errors as config errors`() {
        val expected =
            ConfigError(
                "SQL Server Permission Error: Database user lacks SELECT permission for one or more selected SQL Server objects."
            )

        Assertions.assertEquals(
            expected,
            classifier.classify(
                SQLException(
                    "The SELECT permission was denied on the object.",
                    "42000",
                    229,
                )
            ),
        )
        Assertions.assertEquals(
            expected,
            classifier.classify(
                SQLException(
                    "The SELECT permission was denied on the object.",
                    "S0005",
                    229,
                )
            ),
        )
    }
}
