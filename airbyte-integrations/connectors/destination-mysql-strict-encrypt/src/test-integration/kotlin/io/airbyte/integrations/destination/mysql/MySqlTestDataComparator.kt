/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.mysql

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.integrations.destination.StandardNameTransformer
import io.airbyte.cdk.integrations.standardtest.destination.comparator.AdvancedTestDataComparator
import java.time.LocalDate
import java.time.format.DateTimeFormatter
import java.util.*

class MySqlTestDataComparator : AdvancedTestDataComparator() {
    private val namingResolver: StandardNameTransformer = MySQLNameTransformer()

    @SuppressFBWarnings("NP_PARAMETER_MUST_BE_NONNULL_BUT_MARKED_AS_NULLABLE")
    override fun resolveIdentifier(identifier: String?): List<String?> {
        val result: MutableList<String?> = ArrayList()
        val resolved = namingResolver.getIdentifier(identifier!!)
        result.add(identifier)
        result.add(resolved)
        if (!resolved.startsWith("\"")) {
            result.add(resolved.lowercase(Locale.getDefault()))
        }
        return result
    }

    override fun compareBooleanValues(
        firstBooleanValue: String,
        secondBooleanValue: String
    ): Boolean {
        return if (
            secondBooleanValue.equals("true", ignoreCase = true) ||
                secondBooleanValue.equals("false", ignoreCase = true)
        ) {
            super.compareBooleanValues(firstBooleanValue, secondBooleanValue)
        } else {
            super.compareBooleanValues(firstBooleanValue, (secondBooleanValue == "1").toString())
        }
    }

    override fun compareDateTimeValues(expectedValue: String, actualValue: String): Boolean {
        val destinationDate = parseLocalDateTime(actualValue)
        val expectedDate =
            LocalDate.parse(expectedValue, DateTimeFormatter.ofPattern(AIRBYTE_DATETIME_FORMAT))
        return expectedDate == destinationDate
    }

    private fun parseLocalDateTime(dateTimeValue: String?): LocalDate? {
        return if (dateTimeValue != null) {
            LocalDate.parse(dateTimeValue, DateTimeFormatter.ofPattern(getFormat(dateTimeValue)))
        } else {
            null
        }
    }

    private fun getFormat(dateTimeValue: String): String {
        return if (dateTimeValue.contains("T")) {
            // MySql stores array of objects as a jsonb type, i.e. array of string for all cases
            AIRBYTE_DATETIME_FORMAT
        } else {
            // MySql stores datetime as datetime type after normalization
            AIRBYTE_DATETIME_PARSED_FORMAT
        }
    }
}
