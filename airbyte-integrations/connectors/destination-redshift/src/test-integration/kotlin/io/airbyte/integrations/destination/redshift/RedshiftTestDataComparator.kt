/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.redshift

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.integrations.standardtest.destination.comparator.AdvancedTestDataComparator
import java.time.LocalDate
import java.time.ZoneOffset
import java.time.ZonedDateTime
import java.time.format.DateTimeFormatter
import java.time.format.DateTimeParseException
import java.util.Locale
import org.slf4j.Logger
import org.slf4j.LoggerFactory

class RedshiftTestDataComparator : AdvancedTestDataComparator() {
    private val namingResolver = RedshiftSQLNameTransformer()

    @SuppressFBWarnings("NP_PARAMETER_MUST_BE_NONNULL_BUT_MARKED_AS_NULLABLE")
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

    override fun compareDateTimeWithTzValues(
        airbyteMessageValue: String,
        destinationValue: String
    ): Boolean {
        try {
            val airbyteDate =
                ZonedDateTime.parse(airbyteMessageValue, airbyteDateTimeWithTzFormatter)
                    .withZoneSameInstant(ZoneOffset.UTC)

            val destinationDate =
                ZonedDateTime.parse(destinationValue).withZoneSameInstant(ZoneOffset.UTC)
            return airbyteDate == destinationDate
        } catch (e: DateTimeParseException) {
            LOGGER.warn(
                "Fail to convert values to ZonedDateTime. Try to compare as text. Airbyte value({}), Destination value ({}). Exception: {}",
                airbyteMessageValue,
                destinationValue,
                e
            )
            return compareTextValues(airbyteMessageValue, destinationValue)
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

    companion object {
        private val LOGGER: Logger = LoggerFactory.getLogger(RedshiftTestDataComparator::class.java)

        protected const val REDSHIFT_DATETIME_WITH_TZ_FORMAT: String = "yyyy-MM-dd HH:mm:ssX"
    }
}
