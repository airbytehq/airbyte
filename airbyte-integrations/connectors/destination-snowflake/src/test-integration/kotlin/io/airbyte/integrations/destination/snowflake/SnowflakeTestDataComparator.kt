/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.snowflake

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.integrations.destination.NamingConventionTransformer
import io.airbyte.cdk.integrations.standardtest.destination.comparator.AdvancedTestDataComparator
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.ZoneOffset
import java.time.ZonedDateTime
import java.time.format.DateTimeFormatter
import java.util.*

class SnowflakeTestDataComparator : AdvancedTestDataComparator() {
    @SuppressFBWarnings("NP_PARAMETER_MUST_BE_NONNULL_BUT_MARKED_AS_NULLABLE")
    override fun resolveIdentifier(identifier: String?): List<String?> {
        val result: MutableList<String?> = ArrayList()
        val resolved = NAME_TRANSFORMER.getIdentifier(identifier!!)
        result.add(identifier)
        result.add(resolved)
        if (!resolved.startsWith("\"")) {
            result.add(resolved.lowercase(Locale.getDefault()))
            result.add(resolved.uppercase(Locale.getDefault()))
        }
        return result
    }

    private fun parseDate(dateValue: String?): LocalDate? {
        if (dateValue != null) {
            val format =
                (if (dateValue.matches(".+Z".toRegex())) SNOWFLAKE_DATETIME_FORMAT
                else SNOWFLAKE_DATE_FORMAT)
            return LocalDate.parse(dateValue, DateTimeFormatter.ofPattern(format))
        } else {
            return null
        }
    }

    private fun parseLocalDate(dateTimeValue: String?): LocalDate? {
        if (dateTimeValue != null) {
            val format =
                (if (dateTimeValue.matches(".+Z".toRegex())) POSTGRES_DATETIME_WITH_TZ_FORMAT
                else AIRBYTE_DATETIME_FORMAT)
            return LocalDate.parse(dateTimeValue, DateTimeFormatter.ofPattern(format))
        } else {
            return null
        }
    }

    override fun compareDateTimeValues(
        airbyteMessageValue: String,
        destinationValue: String
    ): Boolean {
        val destinationDate = parseLocalDate(destinationValue)
        val expectedDate =
            LocalDate.parse(
                airbyteMessageValue,
                DateTimeFormatter.ofPattern(AIRBYTE_DATETIME_FORMAT)
            )
        return expectedDate == destinationDate
    }

    override fun compareDateValues(airbyteMessageValue: String, destinationValue: String): Boolean {
        val destinationDate = parseDate(destinationValue)
        val expectedDate =
            LocalDate.parse(airbyteMessageValue, DateTimeFormatter.ofPattern(AIRBYTE_DATE_FORMAT))
        return expectedDate == destinationDate
    }

    override fun parseDestinationDateWithTz(destinationValue: String): ZonedDateTime {
        return ZonedDateTime.of(
            LocalDateTime.parse(
                destinationValue,
                DateTimeFormatter.ofPattern(POSTGRES_DATETIME_WITH_TZ_FORMAT)
            ),
            ZoneOffset.UTC
        )
    }

    companion object {
        val NAME_TRANSFORMER: NamingConventionTransformer = SnowflakeSQLNameTransformer()

        private const val SNOWFLAKE_DATETIME_FORMAT = "yyyy-MM-dd'T'HH:mm:ss'Z'"
        private const val SNOWFLAKE_DATE_FORMAT = "yyyy-MM-dd"
        private const val POSTGRES_DATETIME_WITH_TZ_FORMAT = "yyyy-MM-dd'T'HH:mm:ss.SSSSSS'Z'"
    }
}
