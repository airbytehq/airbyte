/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.standardtest.destination.comparator

import com.fasterxml.jackson.databind.JsonNode
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.function.Function
import org.junit.jupiter.api.Assertions

private val LOGGER = KotlinLogging.logger {}

class BasicTestDataComparator(private val nameResolver: Function<String?, List<String?>>) :
    TestDataComparator {
    override fun assertSameData(expected: List<JsonNode>, actual: List<JsonNode>) {
        LOGGER.info("Expected data {}", expected)
        LOGGER.info("Actual data   {}", actual)
        Assertions.assertEquals(expected.size, actual.size)
        val expectedIterator = expected.iterator()
        val actualIterator = actual.iterator()
        while (expectedIterator.hasNext() && actualIterator.hasNext()) {
            val expectedData = expectedIterator.next()
            val actualData = actualIterator.next()
            val expectedDataIterator = expectedData.fields()
            LOGGER.info("Expected row {}", expectedData)
            LOGGER.info("Actual row   {}", actualData)
            Assertions.assertEquals(expectedData.size(), actualData.size(), "Unequal row size")
            while (expectedDataIterator.hasNext()) {
                val expectedEntry = expectedDataIterator.next()
                val expectedValue = expectedEntry.value
                val key = expectedEntry.key
                val actualValue =
                    ComparatorUtils.getActualValueByExpectedKey(key, actualData, nameResolver)
                LOGGER.info("For {} Expected {} vs Actual {}", key, expectedValue, actualValue)
                assertSameValue(expectedValue, actualValue)
            }
        }
    }

    // Allows subclasses to implement custom comparison asserts
    protected fun assertSameValue(expectedValue: JsonNode?, actualValue: JsonNode?) {
        Assertions.assertEquals(expectedValue, actualValue)
    }

    companion object {}
}
