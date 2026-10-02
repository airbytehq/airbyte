/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.auth

import org.junit.jupiter.api.DynamicTest
import org.junit.jupiter.api.TestFactory

internal class SnowflakeWorkloadIdentityDataSourceTest {
    @TestFactory
    fun workloadIdentityScenarios(): List<DynamicTest> =
        SnowflakeWorkloadIdentityScenarios.cases().map { (name, run) ->
            DynamicTest.dynamicTest(name) { run() }
        }
}
