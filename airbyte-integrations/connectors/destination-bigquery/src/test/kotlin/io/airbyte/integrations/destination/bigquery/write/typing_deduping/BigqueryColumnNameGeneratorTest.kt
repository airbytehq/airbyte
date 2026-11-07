/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.bigquery.write.typing_deduping

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNotEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

internal class BigqueryColumnNameGeneratorTest {
    private val generator = BigqueryColumnNameGenerator()

    @Test
    fun testShortNamesAreUnchanged() {
        val column = "a_normal_column_name"
        val result = generator.getColumnName(column)
        assertEquals(column, result.displayName)
        assertEquals(column, result.canonicalName)
    }

    @Test
    fun testOverLengthNameIsTruncatedWithinLimit() {
        // Simulates a Google Sheets header cell containing a full survey question.
        val column =
            "1 which instructions did the monitor need to re explain " +
                "a".repeat(BIGQUERY_MAX_COLUMN_NAME_LENGTH)
        val result = generator.getColumnName(column)

        assertTrue(
            result.displayName.length <= BIGQUERY_MAX_COLUMN_NAME_LENGTH,
            "display name length ${result.displayName.length} exceeds limit",
        )
        assertTrue(
            result.canonicalName.length <= BIGQUERY_MAX_COLUMN_NAME_LENGTH,
            "canonical name length ${result.canonicalName.length} exceeds limit",
        )
    }

    @Test
    fun testTruncationIsDeterministic() {
        val column = "x".repeat(500)
        assertEquals(
            generator.getColumnName(column).displayName,
            generator.getColumnName(column).displayName,
        )
    }

    @Test
    fun testOverLengthNamesSharingPrefixDoNotCollide() {
        val prefix = "y".repeat(BIGQUERY_MAX_COLUMN_NAME_LENGTH + 50)
        val first = generator.getColumnName("${prefix}_alpha")
        val second = generator.getColumnName("${prefix}_beta")
        assertNotEquals(first.canonicalName, second.canonicalName)
    }
}
