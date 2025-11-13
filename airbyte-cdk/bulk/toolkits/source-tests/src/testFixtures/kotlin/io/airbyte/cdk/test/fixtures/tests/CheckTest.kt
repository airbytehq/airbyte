/* Copyright (c) 2025 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.test.fixtures.tests

import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.test.fixtures.connector.IntegrationTestOperations
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.DynamicNode
import org.junit.jupiter.api.DynamicTest
import org.junit.jupiter.api.TestFactory
import org.junit.jupiter.api.Timeout

abstract class CheckTest {

    abstract val testCases: List<TestCase>

    @TestFactory
    @Timeout(300)
    fun tests(): Iterable<DynamicNode> {
        return testCases.map { case ->
            DynamicTest.dynamicTest(case.name) {
                assertTrue(IntegrationTestOperations(case.configSpec).check())
            }
        }
    }

    data class TestCase(
        val name: String,
        val configSpec: ConfigurationSpecification,
    )
}
