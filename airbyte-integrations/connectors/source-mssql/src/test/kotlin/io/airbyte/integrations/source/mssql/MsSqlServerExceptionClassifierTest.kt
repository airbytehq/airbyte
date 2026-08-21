/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql

import io.airbyte.cdk.output.ConfigError
import io.airbyte.cdk.output.JdbcExceptionClassifier
import io.airbyte.cdk.output.RegexExceptionClassifier
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import java.sql.SQLException
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

@MicronautTest
class MsSqlServerExceptionClassifierTest {

    @Inject lateinit var regexClassifier: RegexExceptionClassifier

    @Inject lateinit var jdbcClassifier: JdbcExceptionClassifier

    @Test
    fun azureGatewayVendorErrorIsClassifiedAsConfigError() {
        val result =
            jdbcClassifier.classify(
                SQLException(
                    "Cannot open server \"localhost\" requested by the login. The login failed.",
                    "S0001",
                    40532,
                )
            )

        Assertions.assertTrue(result is ConfigError, result.toString())
    }

    @Test
    fun azureGatewayMessageIsClassifiedAsConfigError() {
        val result =
            regexClassifier.classify(
                RuntimeException(
                    "Cannot open server \"localhost\" requested by the login. The login failed."
                )
            )

        Assertions.assertTrue(result is ConfigError, result.toString())
    }
}
