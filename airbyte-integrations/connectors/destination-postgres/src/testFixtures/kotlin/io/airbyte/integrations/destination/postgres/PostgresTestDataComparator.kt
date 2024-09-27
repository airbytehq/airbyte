/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.postgres

import io.airbyte.cdk.integrations.destination.StandardNameTransformer
import io.airbyte.cdk.integrations.standardtest.destination.comparator.AdvancedTestDataComparator
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.ZoneOffset
import java.time.ZonedDateTime
import java.time.format.DateTimeFormatter
import java.util.*

class PostgresTestDataComparator : AdvancedTestDataComparator() {
    private val namingResolver = StandardNameTransformer()

    override fun resolveIdentifier(identifier: String?): List<String?> {
        val result: MutableList<String?> = ArrayList()
        val resolved = namingResolver.getIdentifier(identifier!!)
        result.add(identifier)
        result.add(resolved)
        if (!resolved.startsWith("\"")) {
            result.add(resolved.lowercase(Locale.getDefault()))
            result.add(resolved.uppercase(Locale.getDefault()))
        }
        return result
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

    override fun parseDestinationDateWithTz(destinationValue: String): ZonedDateTime {
        return ZonedDateTime.of(
            LocalDateTime.parse(
                destinationValue,
                DateTimeFormatter.ofPattern(POSTGRES_DATETIME_WITH_TZ_FORMAT)
            ),
            ZoneOffset.UTC
        )
    }

    private fun parseLocalDate(dateTimeValue: String?): LocalDate? {
        return if (dateTimeValue != null) {
            LocalDate.parse(dateTimeValue, DateTimeFormatter.ofPattern(getFormat(dateTimeValue)))
        } else {
            null
        }
    }

    private fun getFormat(dateTimeValue: String): String {
        return if (dateTimeValue.matches(".+Z".toRegex())) {
            POSTGRES_DATETIME_FORMAT
        } else if (dateTimeValue.contains("T")) {
            // Postgres stores array of objects as a jsobb type, i.e. array of string for all cases
            AIRBYTE_DATETIME_FORMAT
        } else {
            // Postgres stores datetime as datetime type after normalization
            AIRBYTE_DATETIME_PARSED_FORMAT
        }
    }

    companion object {
        private const val POSTGRES_DATETIME_FORMAT = "yyyy-MM-dd'T'HH:mm:ss'Z'"
        private const val POSTGRES_DATETIME_WITH_TZ_FORMAT = "yyyy-MM-dd'T'HH:mm:ss'Z'"
    }
}
